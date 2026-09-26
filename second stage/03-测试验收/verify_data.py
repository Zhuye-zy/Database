#!/usr/bin/env python3
"""Read-only DB audit; evidence files stay inside second stage."""
import os,sys,subprocess,json,csv,hashlib,runpy,contextlib,io,datetime
from pathlib import Path
S=Path(__file__).resolve().parents[1]
C=os.environ.get("PATENT_CONTAINER","patentdb")
OUT=S/"07-验收结果"/("现有数据库" if C=="patentdb" else "临时数据库")
OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(S/"02-数据导入"))
def query(sql):
 p=subprocess.run(["docker","exec","-i",C,"psql","-X","-U","postgres","-d","patentdb","-At","-v","ON_ERROR_STOP=1"],input=sql,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
def records(sql):
 return json.loads(query("SELECT COALESCE(json_agg(x),'[]'::json) FROM ("+sql+") x;"))
def export(name,rows):
 (OUT/(name+".json")).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
 if rows:
  with (OUT/(name+".csv")).open("w",encoding="utf-8-sig",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
issues=[]
columns=records("SELECT table_name,column_name,data_type,character_maximum_length,is_nullable FROM information_schema.columns WHERE table_schema='patentdb' ORDER BY table_name,ordinal_position")
constraints=records("SELECT conrelid::regclass::text AS table_name,conname,contype,convalidated,pg_get_constraintdef(oid) AS definition FROM pg_constraint WHERE connamespace='patentdb'::regnamespace ORDER BY conrelid::regclass::text,conname")
indexes=records("SELECT tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='patentdb' ORDER BY tablename,indexname")
export("字段清单",columns);export("约束清单",constraints);export("索引清单",indexes)
baseline=list(csv.DictReader((S/"04-报告与基线/设计基线/02-数据字典.csv").open(encoding="utf-8-sig")))
if {(x["table_name"],x["column_name"]) for x in baseline}!={(x["table_name"],x["column_name"]) for x in columns}:issues.append("Columns differ from A's dictionary")
names=sorted({x["table_name"] for x in columns})
data={n:records('SELECT * FROM patentdb."'+n+'"') for n in names}
counts={n:len(rows) for n,rows in data.items()}
export("逐表行数",[{"table":n,"rows":v} for n,v in counts.items()])
coverage=[{"table":c["table_name"],"column":c["column_name"],"rows":counts[c["table_name"]],"non_null":sum(r[c["column_name"]] is not None for r in data[c["table_name"]])} for c in columns]
export("字段非空覆盖",coverage)
expected={'patent':19,'publication':19,'dataset':5,'title':30,'abstract':13,'description_section':538,'drawing':92,'claim':184,'claim_dependency':84,'patent_citation':805,'patent_citation_category':789,'non_patent_citation':297,'patent_family':3,'patent_family_member':11,'family_member_application_ref':21,'family_member_publication_ref':37,'family_abstract':1,'legal_status_event':10,'designated_state':47,'related_application':11,'international_application':1,'priority_claim':3,'family_citation':0}
for n,v in expected.items():
 if counts.get(n)!=v:issues.append(f"{n}: expected {v}, got {counts.get(n)}")
if len(names)!=43 or len(columns)!=345:issues.append("Expected 43 tables / 345 columns")
if sum(c["contype"]=="f" and c["convalidated"] for c in constraints)!=91:issues.append("Expected 91 validated foreign keys")
if sum(c["contype"]=="p" for c in constraints)!=43:issues.append("Expected 43 primary keys")
if sum(i["indexname"].startswith("ix_") for i in indexes)!=78:issues.append("Expected 78 supporting indexes")
# Compare every prepared field of every base-source row with actual DB values.
from sample_mapping import prepare_sources
ns=prepare_sources(S/"05-官方来源/01-四类基础样例")
mapped=0;row_checks=[]
for table,rows in ns["tables"].items():
 keys={"person":["person_id"]}.get(table,ns["unique_cols"][table])
 lookup={tuple(r[k] for k in keys):r for r in data[table]}
 mismatches=[]
 for cols,vals in rows:
  source=dict(zip(cols,vals));key=tuple(source[k] for k in keys);target=lookup.get(key)
  if target is None:mismatches.append({"key":key,"missing":True});continue
  for col,val in source.items():
   if target[col]!=val:
    mismatches.append({"key":key,"column":col,"source":val,"database":target[col]})
   mapped+=1
 row_checks.append({"table":table,"prepared_rows":len(rows),"mismatches":len(mismatches)})
 if mismatches:issues.append(f"{table}: {len(mismatches)} source-mapping mismatches");export(table+"-映射差异",mismatches)
export("基础样例逐字段对照",row_checks)
en=runpy.run_path(str(S/"02-数据导入/import_enrichment.py"),run_name="supplement_audit")
supplement=records("SELECT table_name,count(*) AS source_rows,sum(mismatches) AS mismatches FROM ("+" UNION ALL ".join(en["verification_queries"])+") checks GROUP BY table_name ORDER BY table_name")
export("补充样例逐字段对照",supplement)
for r in supplement:
 if r["mismatches"]:issues.append(f"{r['table_name']}: {r['mismatches']} supplement source mismatches")
checks={
 "ISA":"""SELECT count(*) FROM patentdb.person p LEFT JOIN patentdb.natural_person n USING(person_id) LEFT JOIN patentdb.organization o USING(person_id)
 WHERE NOT ((p.person_type='N' AND n.person_id IS NOT NULL AND o.person_id IS NULL) OR (p.person_type='L' AND o.person_id IS NOT NULL AND n.person_id IS NULL))""",
 "claim_cross_document":"""SELECT count(*) FROM patentdb.claim_dependency d JOIN patentdb.claim a ON a.claim_id=d.dependent_claim_id JOIN patentdb.claim b ON b.claim_id=d.parent_claim_id WHERE a.publication_id<>b.publication_id OR a.lang_code<>b.lang_code""",
 "citation_owner":"""SELECT count(*) FROM patentdb.patent_citation c JOIN patentdb.publication p ON p.publication_id=c.citing_publication_id WHERE c.citing_patent_id<>p.patent_id""",
 "citation_missing_raw":"""SELECT count(*) FROM patentdb.patent_citation WHERE citation_type='P' AND cited_publn_id IS NULL AND coalesce(cited_doc_number,'')=''""",
 "NPL_detail_missing":"""SELECT count(*) FROM patentdb.patent_citation c LEFT JOIN patentdb.non_patent_citation n USING(citation_id) WHERE c.citation_type='N' AND n.npl_id IS NULL""",
 "invented_family":"""SELECT count(*) FROM patentdb.patent_family WHERE source_family_id<0 OR family_type='LOCAL'""",
 "partial_date_invented":"""SELECT count(*) FROM patentdb.patent_citation WHERE (cited_doc_date_raw LIKE '%00' OR cited_doc_date_raw='99991231') AND cited_doc_date IS NOT NULL"""
}
integrity={k:int(query(v)) for k,v in checks.items()}
for k,v in integrity.items():
 if v:issues.append(f"{k}: {v}")
export("完整性检查",[{"check":k,"violations":v} for k,v in integrity.items()])
langs=records("SELECT p.publn_nr,c.lang_code,count(*) AS claims FROM patentdb.claim c JOIN patentdb.publication p USING(publication_id) WHERE p.publn_auth='EP' GROUP BY p.publn_nr,c.lang_code ORDER BY p.publn_nr,c.lang_code")
if {(r["publn_nr"],r["lang_code"],r["claims"]) for r in langs}!={(n,l,v) for n,v in [("0712096",10),("0890251",14)] for l in ["EN","DE","FR"]}:issues.append("EP multilingual claim mismatch")
export("EP多语言权利要求",langs)
manifest=[]
for p in sorted((S/"05-官方来源").rglob("*")):
 if p.is_file():manifest.append({"file":str(p.relative_to(S)),"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
export("来源文件SHA256",manifest)
summary={"timestamp_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"container":C,"tables":len(names),"columns":len(columns),"nonempty_tables":sum(v>0 for v in counts.values()),"mapped_field_comparisons":mapped,
 "issues":issues,"status":"PASS" if not issues else "FAIL","scope":"固定官方样例及映射字段；不等同全量数据/所有XML路径已覆盖"}
export("验收摘要",[summary])
print(json.dumps(summary,ensure_ascii=False,indent=2))
for n,v in counts.items():print(f"{n:34} {v}")
sys.exit(bool(issues))
