#!/usr/bin/env python3
"""Transactional, business-key based import with per-document provenance and DOCDB soft deletes."""
from pathlib import Path
import argparse,os,sys,json,uuid,hashlib,subprocess,datetime,base64
import xml.etree.ElementTree as ET
from sample_mapping import *
from batch_extensions import extend
from import_support import logical_roots,write_log
S=Path(__file__).resolve().parents[1]
C=os.environ.get("PATENT_CONTAINER","patentdb")
def db(sql,check=True):
    p=subprocess.run(["docker","exec","-i",C,"psql","-X","-U","postgres","-d","patentdb","-At","-v","ON_ERROR_STOP=1"],input=sql,text=True,capture_output=True)
    if check and p.returncode:raise RuntimeError(p.stderr)
    return p
def rows(sql):
    return json.loads(db("SELECT coalesce(json_agg(x),'[]'::json) FROM ("+sql+") x;").stdout)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root",type=Path,default=S/"05-官方来源/01-四类基础样例")
    ap.add_argument("--operations-file",type=Path,action="append",default=[])
    args=ap.parse_args();source=args.source_root.resolve()
    for path in [source,*args.operations_file]:
        if not path.resolve().is_relative_to(S.resolve()):ap.error("Inputs must remain under second stage")
    bid=str(uuid.uuid4())
    db("INSERT INTO stage2_meta.import_batch(batch_id,source_root,status) VALUES("+q(bid)+","+q(str(source.relative_to(S)))+",'RUNNING');")
    docs=[];lookup={};errors=[];marker=None;scanned=set()
    states={ (r["publn_auth"].strip(),r["publn_nr"],r["publn_kind"]):r for r in rows("SELECT * FROM stage2_meta.publication_state")}
    def scan(path,bucket):
        if path.resolve() in scanned:return
        scanned.add(path.resolve())
        try:roots=logical_roots(path.read_bytes())
        except Exception as ex:
            docs.append(dict(source_file=str(path.relative_to(S)),document_index=0,dataset=bucket,logical_identifier=None,
                xml_path="/",sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_operation=None,disposition="ERROR",
                raw_xml=path.read_text(errors="replace"),error_type=type(ex).__name__,error_message=str(ex)))
            errors.append(str(ex));return
        for index,node in enumerate(roots,1):
            raw=ET.tostring(node,encoding="unicode");op=node.get("status") if local(node)=="exchange-document" else "UPSERT"
            rec=dict(source_file=str(path.relative_to(S)),document_index=index,dataset=bucket,logical_identifier=None,
                xml_path="/"+local(node),sha256=hashlib.sha256(raw.encode()).hexdigest(),raw_operation=op or "UPSERT",
                disposition="NORMALIZED",raw_xml=raw,error_type=None,error_message=None)
            try:
                if local(node)=="exchange-document":
                    key=(node.get("country"),node.get("doc-number"),node.get("kind"))
                    if not all(key):raise ValueError("DOCDB publication identifier missing")
                    if op in ("CV","DV"):rec["disposition"]="VOID_NOTICE_RECORDED"
                    elif op=="D":rec["disposition"]="SOFT_DELETED"
                    elif op not in ("A","C",None,""):raise ValueError("Unknown DOCDB exchange status "+str(op))
                else:key=parse_document(node,bucket,str(path))["pubkey"]
                rec["logical_identifier"]="-".join(key)
                rec["_key"]=key;rec["_node"]=node
                date=date_parts(node.get("date-of-last-exchange"))[0]
                rec["_date"]=date
                old=states.get(key)
                if op not in ("CV","DV") and old and old["last_exchange_date"] and date and date<old["last_exchange_date"]:
                    rec["disposition"]="STALE_IGNORED"
            except Exception as ex:
                rec.update(disposition="ERROR",error_type=type(ex).__name__,error_message=str(ex));errors.append(str(ex))
            docs.append(rec);lookup[(str(path.resolve()),index)]=rec
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.suffix.lower()==".xml":
            bucket=path.relative_to(source).parts[0]
            if bucket in DATASETS:scan(path,bucket)
    for path in args.operations_file:
        scan(path.resolve(),"ep-docdb")
    for rec in docs:
        if any(rec["source_file"]==str(p.resolve().relative_to(S)) for p in args.operations_file) and rec["raw_operation"] not in ("D","CV","DV"):
            rec.update(disposition="ERROR",error_type="InputLayoutError",error_message="Full DOCDB records belong in source-root/ep-docdb; operations-file accepts D/CV/DV only")
            errors.append(rec["error_message"])
    def accept(node,bucket,path,index):
        return lookup[(str(path.resolve()),index)]["disposition"]=="NORMALIZED"
    ns=prepare_sources(source,accept);extend(ns)
    for err in ns["parse_errors"]:
        errors.append(err["message"])
        for rec in docs:
            if rec["source_file"].endswith(err["source_file"]):
                rec.update(disposition="ERROR",error_type=err["error_type"],error_message=err["message"],xml_path=err["xml_path"])
    def journal(status,summary,execute=True):
        stmts=["BEGIN;"]
        for rec in docs:
            cleanrec={k:v for k,v in rec.items() if not k.startswith("_")}
            cleanrec["batch_id"]=bid
            if status=="FAILED" and cleanrec["disposition"]=="NORMALIZED":cleanrec["disposition"]="ROLLED_BACK"
            if status=="FAILED" and marker and cleanrec["logical_identifier"]==marker.get("logical_document"):
                cleanrec.update(error_type="DatabaseImportError",error_message=str(summary.get("error")),xml_path=marker.get("xml_path","/"))
            cs=list(cleanrec);stmts.append("INSERT INTO stage2_meta.source_document("+",".join(cs)+") VALUES("+",".join(q(cleanrec[c]) for c in cs)+");")
        stmts.append("UPDATE stage2_meta.import_batch SET status="+q(status)+",finished_at=now(),summary="+q(json.dumps(summary,ensure_ascii=False))+"::jsonb WHERE batch_id="+q(bid)+"; COMMIT;")
        if execute:db("\n".join(stmts))
        return stmts
    if errors:
        journal("FAILED",{"errors":errors});write_log("batch-import",{"batch_id":bid,"status":"FAILED","errors":errors})
        raise SystemExit("Batch rejected before business writes: "+str(errors))
    identity={r["table_name"]:r["column_name"] for r in rows("SELECT table_name,column_name FROM information_schema.columns WHERE table_schema='patentdb' AND is_identity='YES'")}
    fkrows=rows("""SELECT c.conrelid::regclass::text AS child,a.attname AS col,
       c.confrelid::regclass::text AS parent,b.attname AS target
       FROM pg_constraint c JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
       JOIN pg_attribute b ON b.attrelid=c.confrelid AND b.attnum=c.confkey[1]
       WHERE c.connamespace='patentdb'::regnamespace AND c.contype='f' AND cardinality(c.conkey)=1""")
    refs={(r["child"].split(".")[-1],r["col"]):(r["parent"].split(".")[-1],r["target"]) for r in fkrows}
    parts=["BEGIN;","SELECT pg_advisory_xact_lock(782143345);","SET CONSTRAINTS ALL DEFERRED;",
           "CREATE TEMP TABLE import_ids(entity text,local_id bigint,actual_id bigint,PRIMARY KEY(entity,local_id)) ON COMMIT DROP;",
           "CREATE TEMP TABLE import_empty(entity text PRIMARY KEY) ON COMMIT DROP;",
           "CREATE TEMP TABLE import_keys(entity text,key jsonb) ON COMMIT DROP;"]
    for table,ident in identity.items():
        parts.append("INSERT INTO import_empty SELECT "+q(table)+" WHERE NOT EXISTS(SELECT 1 FROM patentdb."+table+");")
        parts.append("SELECT setval(pg_get_serial_sequence('patentdb."+table+"','"+ident+"'),greatest(coalesce((SELECT max("+ident+") FROM patentdb."+table+"),1),1),EXISTS(SELECT 1 FROM patentdb."+table+"));")
    def expr(table,col,value):
        ref=refs.get((table,col))
        if value is not None and ref and identity.get(ref[0])==ref[1]:
            return "(SELECT actual_id FROM import_ids WHERE entity="+q(ref[0])+" AND local_id="+q(value)+")"
        return q(value)
    bypat={ns["app_id"][d["appkey"]]:d for d in ns["parsed"]}
    bypub={ns["pub_id"][d["pubkey"]]:d for d in ns["parsed"]}
    for table in ns["ORDER"]:
        for cols,values in ns["tables"][table]:
            r=dict(zip(cols,values));ident=identity.get(table);keys=ns["unique_cols"][table]
            doc=bypub.get(r.get("publication_id",r.get("citing_publication_id"))) or bypat.get(r.get("patent_id",r.get("citing_patent_id")))
            origin={"dataset":doc["bucket"] if doc else "shared-reference",
              "source_file":doc["source"] if doc else str(source.relative_to(S)),
              "logical_document":"-".join(doc["pubkey"]) if doc else None,
              "xml_path":"/"+local(doc["root"]) if doc else "/",
              "table":table,"business_key":{k:r[k] for k in keys}}
            parts.append("\\echo ROW_CONTEXT "+base64.b64encode(json.dumps(origin,ensure_ascii=False).encode()).decode())
            outcols=[c for c in cols if c!=ident]
            vals=[expr(table,c,r[c]) for c in outcols]
            updates=[c+"=EXCLUDED."+c for c in outcols if c not in keys]
            action="DO UPDATE SET "+",".join(updates) if updates else "DO NOTHING"
            if ident:
                # Preserve original sample IDs in empty tables; allocate stable sequence IDs in populated DBs.
                new_id="CASE WHEN EXISTS(SELECT 1 FROM import_empty WHERE entity="+q(table)+") THEN "+q(r[ident])+" ELSE nextval(pg_get_serial_sequence('patentdb."+table+"','"+ident+"')) END"
                if table=="person":
                    predicate="person_type="+q(r["person_type"])+" AND lower(person_name)=lower("+q(r["person_name"])+") AND ctry_code IS NOT DISTINCT FROM "+q(r.get("ctry_code"))
                    sql="WITH existing AS MATERIALIZED(SELECT person_id FROM patentdb.person WHERE "+predicate+" ORDER BY person_id LIMIT 1), ins AS (INSERT INTO patentdb.person("+",".join([ident,*outcols])+") SELECT "+",".join([new_id,*vals])+" WHERE NOT EXISTS(SELECT 1 FROM existing) RETURNING person_id) INSERT INTO import_ids SELECT 'person',"+q(r[ident])+",person_id FROM existing UNION ALL SELECT 'person',"+q(r[ident])+",person_id FROM ins;"
                    parts.append(sql)
                    parts.append("UPDATE patentdb.person SET "+",".join(c+"="+expr(table,c,r[c]) for c in outcols)+" WHERE person_id=(SELECT actual_id FROM import_ids WHERE entity='person' AND local_id="+q(r[ident])+");")
                else:
                    if not updates:action="DO UPDATE SET "+keys[0]+"=EXCLUDED."+keys[0]
                    parts.append("WITH ins AS (INSERT INTO patentdb."+table+"("+",".join([ident,*outcols])+") VALUES("+",".join([new_id,*vals])+") ON CONFLICT ("+",".join(keys)+") "+action+" RETURNING "+ident+") INSERT INTO import_ids SELECT "+q(table)+","+q(r[ident])+","+ident+" FROM ins;")
            else:
                parts.append("INSERT INTO patentdb."+table+"("+",".join(outcols)+") VALUES("+",".join(vals)+") ON CONFLICT ("+",".join(keys)+") "+action+";")
            parts.append("INSERT INTO import_keys VALUES("+q(table)+",jsonb_build_array("+",".join(expr(table,k,r[k]) for k in keys)+"));")
    # Resolve family application references against the entire local DB, not just this batch.
    parts.append("""UPDATE patentdb.patent_family_member m SET member_patent_id=(
      SELECT p.patent_id FROM patentdb.family_member_application_ref r JOIN patentdb.patent p
      ON p.appln_auth=r.country_code AND p.appln_nr=r.appln_nr
      WHERE r.member_id=m.member_id AND r.data_format='docdb' ORDER BY p.patent_id LIMIT 1)
      WHERE m.member_id IN (SELECT actual_id FROM import_ids WHERE entity='patent_family_member');""")
    # Full document components: remove stale rows omitted by an amended source snapshot.
    for table in ("title","abstract","description_section","drawing","claim","patent_citation"):
        ident=identity[table];owner="citing_publication_id" if table=="patent_citation" else "publication_id"
        parts.append("DELETE FROM patentdb."+table+" WHERE "+owner+" IN (SELECT actual_id FROM import_ids WHERE entity='publication') AND "+ident+" NOT IN (SELECT actual_id FROM import_ids WHERE entity="+q(table)+");")
    for table,owner,entity in [
      ("patent_classification","patent_id","patent"),("priority_claim","patent_id","patent"),
      ("related_application","patent_id","patent"),("international_application","patent_id","patent"),
      ("patent_applicant","patent_id","patent"),("patent_inventor","patent_id","patent"),
      ("patent_assignee","patent_id","patent"),("patent_agent","patent_id","patent"),
      ("patent_examiner","patent_id","patent"),("claim_dependency","dependent_claim_id","claim"),
      ("patent_citation_category","citation_id","patent_citation"),
      ("family_member_application_ref","member_id","patent_family_member"),
      ("family_member_publication_ref","member_id","patent_family_member"),
      ("family_abstract","family_id","patent_family"),("patent_family_member","family_id","patent_family")]:
        keys=ns["unique_cols"][table]
        parts.append("DELETE FROM patentdb."+table+" target WHERE "+owner+" IN (SELECT actual_id FROM import_ids WHERE entity="+q(entity)+") AND NOT EXISTS(SELECT 1 FROM import_keys k WHERE k.entity="+q(table)+" AND k.key=jsonb_build_array("+",".join("target."+k for k in keys)+"));")
    parts.append("""INSERT INTO patentdb.keyword(keyword_text,lang_code,source)
      SELECT DISTINCT lower(tok),t.lang_code,'TITLE_DERIVED' FROM patentdb.title t
      CROSS JOIN LATERAL regexp_split_to_table(t.title_text,'[^A-Za-z]+') tok
      WHERE t.lang_code='EN' AND length(tok)>=5 ON CONFLICT DO NOTHING;""")
    parts.append("""INSERT INTO patentdb.patent_keyword(patent_id,keyword_id,weight,source)
      SELECT DISTINCT p.patent_id,k.keyword_id,1.0,'TITLE_DERIVED'
      FROM patentdb.title t JOIN patentdb.publication p USING(publication_id)
      CROSS JOIN LATERAL regexp_split_to_table(t.title_text,'[^A-Za-z]+') tok
      JOIN patentdb.keyword k ON k.keyword_text=lower(tok) AND k.lang_code=t.lang_code
      WHERE t.lang_code='EN' AND length(tok)>=5 ON CONFLICT DO NOTHING;""")
    parts.append("""DELETE FROM patentdb.patent_keyword pk WHERE pk.source='TITLE_DERIVED'
      AND pk.patent_id IN(SELECT actual_id FROM import_ids WHERE entity='patent')
      AND NOT EXISTS(SELECT 1 FROM patentdb.title t JOIN patentdb.publication p USING(publication_id)
       CROSS JOIN LATERAL regexp_split_to_table(t.title_text,'[^A-Za-z]+') tok
       JOIN patentdb.keyword k ON k.keyword_text=lower(tok) AND k.lang_code=t.lang_code
       WHERE p.patent_id=pk.patent_id AND k.keyword_id=pk.keyword_id AND t.lang_code='EN' AND length(tok)>=5);""")
    # Keep soft-delete records even for publications not present locally. CV/DV never fabricate a patent.
    operations=sorted(docs,key=lambda r:0 if r["raw_operation"]=="D" else 1)
    for rec in operations:
        if rec["disposition"] not in ("NORMALIZED","SOFT_DELETED"):continue
        key=rec["_key"];node=rec["_node"]
        parts.append("INSERT INTO stage2_meta.publication_state(publn_auth,publn_nr,publn_kind,source_doc_id,last_exchange_date,is_deleted,last_operation,last_batch_id) VALUES("+",".join(q(x) for x in [*key,node.get("doc-id"),rec["_date"],rec["raw_operation"]=="D",rec["raw_operation"],bid])+") ON CONFLICT(publn_auth,publn_nr,publn_kind) DO UPDATE SET source_doc_id=EXCLUDED.source_doc_id,last_exchange_date=EXCLUDED.last_exchange_date,is_deleted=EXCLUDED.is_deleted,last_operation=EXCLUDED.last_operation,last_batch_id=EXCLUDED.last_batch_id;")
    for table,ident in identity.items():
        parts.append("SELECT setval(pg_get_serial_sequence('patentdb."+table+"','"+ident+"'),greatest(coalesce((SELECT max("+ident+") FROM patentdb."+table+"),1),1),EXISTS(SELECT 1 FROM patentdb."+table+"));")
    summary={"batch_id":bid,"documents":len(docs),"normal_documents":len(ns["parsed"]),"operations":dict(__import__("collections").Counter(r["raw_operation"] for r in docs)),"prepared_rows":sum(len(v) for v in ns["tables"].values())}
    # Business mutation and its successful source journal commit atomically.
    parts.extend(journal("SUCCEEDED",summary,execute=False)[1:-1])
    parts.append("COMMIT;")
    result=db("\n".join(parts),False)
    if result.returncode:
        markers=[x.removeprefix("ROW_CONTEXT ") for x in result.stdout.splitlines() if x.startswith("ROW_CONTEXT ")]
        if markers:marker=json.loads(base64.b64decode(markers[-1]))
        summary.update(error=result.stderr,row_context=marker)
        journal("FAILED",summary);write_log("batch-import",{"status":"FAILED",**summary})
        raise SystemExit(result.stderr)
    write_log("batch-import",{"status":"SUCCEEDED",**summary})
    print(json.dumps({"status":"PASS",**summary},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
