#!/usr/bin/env python3
"""Fresh PostgreSQL integration test. No writes to persistent patentdb."""
from pathlib import Path
import subprocess,os,sys,time,json,hashlib,ast
S=Path(__file__).resolve().parents[1]
OUT=S/"07-验收结果/临时数据库";OUT.mkdir(parents=True,exist_ok=True)
C="patentdb-stage2-check-"+str(os.getpid())
ENV={**os.environ,"PATENT_CONTAINER":C,"PYTHONDONTWRITEBYTECODE":"1","PATENT_LOG_DIR":str(OUT/"导入日志")}
IMAGE=os.environ.get("POSTGRES_IMAGE","docker.m.daocloud.io/library/postgres:16")
logs=[];checks=[]
def run(args,txt=None,ok=True):
 p=subprocess.run(args,input=txt,text=True,capture_output=True,env=ENV)
 logs.append("$ "+" ".join(args)+"\n"+p.stdout+p.stderr)
 if ok and p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p
def sql(text,ok=True):
 return run(["docker","exec","-i",C,"psql","-X","-U","postgres","-d","patentdb","-At","-v","ON_ERROR_STOP=1"],text,ok)
def fingerprint():
 tables=sql("SELECT tablename FROM pg_tables WHERE schemaname='patentdb' ORDER BY 1;").stdout.splitlines()
 stmt=" UNION ALL ".join("SELECT '"+n+"',md5(coalesce(string_agg(row_to_json(x)::text,E'\\n' ORDER BY row_to_json(x)::text),'')) FROM patentdb."+n+" x" for n in tables)
 return dict(x.split("|") for x in sql(stmt+";").stdout.splitlines())
def load():
 for n in ["import_samples.py","import_enrichment.py"]:
  run([sys.executable,"-B",str(S/"02-数据导入"/n)])
try:
 run(["docker","run","-d","--name",C,"-e","POSTGRES_PASSWORD=stage2-disposable","-e","POSTGRES_DB=patentdb",IMAGE])
 for _ in range(45):
  if run(["docker","exec",C,"pg_isready","-U","postgres"],ok=False).returncode==0:break
  time.sleep(1)
 else:raise RuntimeError("PostgreSQL readiness timeout")
 for p in sorted((S/"01-数据库结构").glob("*.sql")):sql(p.read_text())
 checks.append("fresh_schema_and_migration")
 load()
 before=fingerprint();load()
 if fingerprint()!=before:raise AssertionError("Repeated import changed logical table contents")
 checks.append("repeat_import_all_table_contents_stable")
 run([sys.executable,"-B",str(S/"03-测试验收/verify_data.py")])
 # Negative tests use explicit transactions that rollback on error / exit.
 cases={
 "unique_publication":("INSERT INTO patentdb.publication SELECT * FROM patentdb.publication LIMIT 1;","duplicate key"),
 "composite_foreign_key":("UPDATE patentdb.publication SET publn_kind='ZZ' WHERE publication_id=1;","foreign key"),
 "invalid_person_type":("UPDATE patentdb.person SET person_type='X' WHERE person_id=1;","check constraint"),
 "missing_ISA_subtype":("DELETE FROM patentdb.natural_person WHERE person_id=(SELECT min(person_id) FROM patentdb.natural_person); SET CONSTRAINTS ALL IMMEDIATE;","must have exactly one subtype"),
 "ISA_old_owner_update":("""INSERT INTO patentdb.person(person_id,person_name,person_type) VALUES(999991,'integration-test-only','N');
 UPDATE patentdb.natural_person SET person_id=999991 WHERE person_id=(SELECT min(person_id) FROM patentdb.natural_person);
 SET CONSTRAINTS ALL IMMEDIATE;""","must have exactly one subtype"),
 "invalid_claim_number":("UPDATE patentdb.claim SET claim_number=0 WHERE claim_id=1;","check constraint")
 }
 for name,(body,fragment) in cases.items():
  p=sql("BEGIN;\n"+body+"\nROLLBACK;",False)
  if p.returncode==0 or fragment not in p.stderr:raise AssertionError(name+": unexpected result "+p.stderr)
  checks.append(name)
 # Test the same date conversion function that the parser uses.
 sys.path.insert(0,str(S/"02-数据导入"))
 from sample_mapping import date_parts
 ns={"date_parts":date_parts}
 for raw,expected in [("20240100",(None,"20240100")),("99991231",(None,"99991231")),("20240229",("2024-02-29","20240229")),("20230229",(None,"20230229"))]:
  assert ns["date_parts"](raw)==expected
 checks.append("actual_partial_sentinel_leap_dates")
 sys.path.insert(0,str(S/"02-数据导入"))
 from import_support import logical_roots
 assert len(logical_roots(b'<?xml version="1.0"?><us-patent-grant/><?xml version="1.0"?><us-patent-grant/>'))==2
 assert len(logical_roots(b'<exchange-documents><exchange-document/><exchange-document/></exchange-documents>'))==2
 checks.append("concatenated_USPTO_and_DOCDB_wrapper")
 # Verify long IPC group and partial date supported; rollback the test.
 sql("BEGIN; UPDATE patentdb.patent SET appln_filing_date=NULL,appln_filing_date_raw='20240100' WHERE patent_id=1; INSERT INTO patentdb.ipc_techn_field VALUES('H04L12/00',4,NULL,NULL); ROLLBACK;")
 checks.append("nullable_partial_date_and_long_IPC")
 # Repair test: repeated import must restore mapped content, not silently ignore conflict.
 sql("UPDATE patentdb.drawing SET image_file='test-corrupt-value' WHERE drawing_id=1;")
 load()
 if fingerprint()!=before:raise AssertionError("UPSERT did not repair changed mapped content")
 checks.append("upsert_repairs_changed_mapped_field")
 # B-role batch acceptance: real CV records plus isolated synthetic change fixtures.
 import copy,xml.etree.ElementTree as ET,shutil
 fixture=OUT/"批次测试输入";fixture.mkdir(exist_ok=True)
 def batch(root=None,operation=None,ok=True):
  cmd=[sys.executable,"-B",str(S/"02-数据导入/import_batch.py")]
  if root is not None:cmd+=["--source-root",str(root)]
  if operation is not None:cmd+=["--operations-file",str(operation)]
  return run(cmd,ok=ok)
 cv=next((S/"05-官方来源/02-IPDPS补充样例/02-DOCDB原文").glob("*CreateDelete*.xml"))
 batch(operation=cv)
 actual=fingerprint()
 if actual!=before:raise AssertionError("Batch replay changed business contents: "+str([k for k in before if before[k]!=actual[k]]))
 assert sql("SELECT count(*) FROM stage2_meta.source_document WHERE raw_operation='CV' AND disposition='VOID_NOTICE_RECORDED';").stdout.strip()=="5"
 checks.append("real_CV_notices_recorded_without_fake_patents")
 base=next((S/"05-官方来源/01-四类基础样例/ep-docdb").glob("*.xml"))
 node=copy.deepcopy(list(ET.parse(base).getroot())[0])
 node.set("doc-number","99990001");node.set("family-id","123456789");node.set("doc-id","integration-only")
 node.set("date-of-last-exchange","20260927");node.set("status","C")
 bib=next(x for x in node if x.tag.endswith("bibliographic-data"))
 for ref in bib:
  tag=ref.tag.rsplit("}",1)[-1]
  if tag in ("application-reference","publication-reference"):
   for item in ref.iter():
    if item.tag.rsplit("}",1)[-1]=="doc-number":item.text="99990001"
 full=fixture/"新增批次";(full/"ep-docdb").mkdir(parents=True,exist_ok=True)
 target=full/"ep-docdb/test.xml"
 def save():
  wrapper=ET.Element("exchange-documents");wrapper.append(node);ET.ElementTree(wrapper).write(target,encoding="utf-8",xml_declaration=True)
 save();batch(full)
 new_id=sql("SELECT publication_id FROM patentdb.publication WHERE publn_auth='EP' AND publn_nr='99990001';").stdout.strip()
 assert int(new_id)>1001
 assert sql("SELECT count(*) FROM patentdb.publication;").stdout.strip()=="20"
 snapshot=fingerprint();batch(full)
 assert fingerprint()==snapshot
 checks.append("incremental_C_allocates_stable_business_ids")
 node.set("status","A");node.set("date-of-last-exchange","20260928")
 for el in list(bib):
  if el.tag.rsplit("}",1)[-1]=="invention-title":
   if el.get("lang")=="fr":bib.remove(el)
   else:el.text="Integration-only amended title"
 save();batch(full)
 assert sql("SELECT count(*) FROM patentdb.title WHERE publication_id="+new_id+";").stdout.strip()=="2"
 assert sql("SELECT count(*) FROM patentdb.title WHERE publication_id="+new_id+" AND title_text='Integration-only amended title';").stdout.strip()=="2"
 checks.append("amend_updates_fields_and_removes_stale_children")
 empty=fixture/"空输入";empty.mkdir(exist_ok=True)
 delete=ET.Element("exchange-document",{"country":"EP","doc-number":"99990001","kind":node.get("kind"),"status":"D","date-of-last-exchange":"20260929"})
 operation=fixture/"delete.xml";ET.ElementTree(delete).write(operation,encoding="utf-8")
 batch(empty,operation)
 assert sql("SELECT count(*) FROM patentdb.publication WHERE publication_id="+new_id+";").stdout.strip()=="1"
 assert sql("SELECT count(*) FROM stage2_meta.active_publication WHERE publication_id="+new_id+";").stdout.strip()=="0"
 checks.append("D_soft_delete_preserves_physical_rows")
 node.set("date-of-last-exchange","20260930");save();batch(full)
 assert sql("SELECT count(*) FROM stage2_meta.active_publication WHERE publication_id="+new_id+";").stdout.strip()=="1"
 batch(empty,operation)
 assert sql("SELECT count(*) FROM stage2_meta.active_publication WHERE publication_id="+new_id+";").stdout.strip()=="1"
 checks.append("A_reactivates_and_stale_D_is_ignored")
 broken=fixture/"损坏XML";(broken/"us-application").mkdir(parents=True,exist_ok=True)
 (broken/"us-application/broken.xml").write_text("<broken")
 p=batch(broken,ok=False)
 assert p.returncode
 assert int(sql("SELECT count(*) FROM stage2_meta.source_document WHERE disposition='ERROR' AND error_type='ParseError' AND xml_path='/';").stdout.strip())>0
 checks.append("parse_failure_has_source_and_error_context")
 us=next(p for p in (S/"05-官方来源/01-四类基础样例/us-application").rglob("*") if p.suffix.lower()==".xml")
 invalid=ET.parse(us).getroot()
 claim=next(x for x in invalid.iter() if x.tag.rsplit("}",1)[-1]=="claim");claim.set("num","-1")
 bad=fixture/"约束错误";(bad/"us-application").mkdir(parents=True,exist_ok=True)
 ET.ElementTree(invalid).write(bad/"us-application/invalid.xml",encoding="utf-8",xml_declaration=True)
 snapshot=fingerprint();p=batch(bad,ok=False)
 assert p.returncode and fingerprint()==snapshot
 assert int(sql("SELECT count(*) FROM stage2_meta.source_document WHERE error_type='DatabaseImportError' AND logical_identifier IS NOT NULL AND xml_path<>'/';").stdout.strip())>0
 checks.append("SQL_failure_rolls_back_and_identifies_source_document")
 # Fixtures are explicitly synthetic and never enter the persistent database.
 assert fixture.resolve().is_relative_to(OUT.resolve())
 shutil.rmtree(fixture)
 r=sql((S/"03-测试验收/queries.sql").read_text())
 (OUT/"查询与执行计划.txt").write_text(r.stdout)
 result={"status":"PASS","checks":checks}
 print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception as ex:
 result={"status":"FAIL","checks":checks,"error":str(ex)}
 print(json.dumps(result,ensure_ascii=False,indent=2));raise
finally:
 (OUT/"集成测试摘要.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
 (OUT/"集成测试日志.txt").write_text("\n".join(logs))
 run(["docker","rm","-f","-v",C],ok=False)
