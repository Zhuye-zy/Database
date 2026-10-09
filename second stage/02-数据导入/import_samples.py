#!/usr/bin/env python3
"""Reviewed fixed-sample replay. For new batches use import_batch.py."""
from sample_mapping import *
from import_support import write_log, assert_source_snapshot
assert_source_snapshot(SAMPLES)
globals().update(prepare_sources(SAMPLES))
# Produce transaction; dimensions precede FK-bearing rows; all identities remain explicit/repeatable.
ORDER=["country_office","language","dataset","kind_code","application_type","classification_scheme","patent","publication","title","abstract","description_section","drawing","claim","claim_dependency","person","natural_person","organization","patent_applicant","patent_inventor","patent_assignee","patent_agent","patent_examiner","classification","patent_classification","patent_citation","non_patent_citation","priority_claim"]
chunks=["BEGIN;","SET CONSTRAINTS ALL DEFERRED;","SET search_path TO patentdb, public;"]
if "--refresh-reviewed" in sys.argv:
    chunks.append("DELETE FROM patentdb.abstract WHERE publication_id IN (SELECT publication_id FROM patentdb.publication WHERE dataset_id BETWEEN 1 AND 4);")
if "--rebuild-text" in sys.argv:
    chunks.append("DELETE FROM patentdb.claim_dependency WHERE dependent_claim_id IN (SELECT claim_id FROM patentdb.claim WHERE publication_id IN (SELECT publication_id FROM patentdb.publication WHERE dataset_id BETWEEN 1 AND 4));")
    chunks.append("DELETE FROM patentdb.claim WHERE publication_id IN (SELECT publication_id FROM patentdb.publication WHERE dataset_id BETWEEN 1 AND 4);")
    chunks.append("DELETE FROM patentdb.description_section WHERE publication_id IN (SELECT publication_id FROM patentdb.publication WHERE dataset_id BETWEEN 1 AND 4);")
for table in ORDER:
    if not tables[table]: continue
    cols=tables[table][0][0]
    for offset in range(0,len(tables[table]),250):
        batch=tables[table][offset:offset+250]
        values=",\n".join("("+", ".join(q(x) for x in row)+")" for _,row in batch)
        conflict = {"person":["person_id"]}.get(table, unique_cols[table])
        updates = [c for c in cols if c not in conflict and not (c.endswith("_id") and c==cols[0])]
        action = "DO UPDATE SET " + ", ".join(c+"=EXCLUDED."+c for c in updates) if updates else "DO NOTHING"
        chunks.append(f"INSERT INTO patentdb.{table} ({', '.join(cols)}) VALUES\n{values}\nON CONFLICT ({', '.join(conflict)}) {action};")
for table,col in [("dataset","dataset_id"),("patent","patent_id"),("publication","publication_id"),("title","title_id"),("abstract","abstract_id"),("description_section","section_id"),("drawing","drawing_id"),("claim","claim_id"),("person","person_id"),("patent_classification","patent_classification_id"),("patent_citation","citation_id"),("non_patent_citation","npl_id"),("priority_claim","priority_id")]:
    chunks.append(f"SELECT setval(pg_get_serial_sequence('patentdb.{table}','{col}'), GREATEST(COALESCE((SELECT max({col}) FROM patentdb.{table}),1),1), EXISTS(SELECT 1 FROM patentdb.{table}));")
chunks.append("COMMIT;")
sql="\n".join(chunks)+"\n"
write_log("base-parse", {"files":len(set(d["source"] for d in parsed)),"logical_documents":len(parsed),
 "datasets":{k:sum(d["bucket"]==k for d in parsed) for k in DATASETS},
 "records":[{"dataset":d["bucket"],"source_file":d["source"],"logical_document":"-".join(d["pubkey"]),
 "xml_path":"/"+local(d["root"]),"status":"parsed"} for d in parsed],"errors":parse_errors})
if "--dry-run" in sys.argv:
    print(f"Parsed logical docs={len(parsed)}; files={len(set(d['source'] for d in parsed))}; parse_errors={len(parse_errors)}")
    print("Rows: "+", ".join(f"{t}={len(tables[t])}" for t in ORDER if tables[t]))
    if parse_errors:
        for e in parse_errors: print("PARSE ERROR",e)
    sys.exit(0 if len(parsed)==18 and not parse_errors else 2)
if len(parsed)!=18 or parse_errors:
    for e in parse_errors: print("PARSE ERROR",e,file=sys.stderr)
    raise SystemExit(f"Refusing import: expected 18 official logical documents, parsed {len(parsed)}")
proc=subprocess.run(["docker","exec","-i",CONTAINER,"psql","-U","postgres","-d","patentdb","-v","ON_ERROR_STOP=1"],input=sql,text=True,capture_output=True)
write_log("base-import", {"container":CONTAINER,"returncode":proc.returncode,"prepared_rows":{k:len(v) for k,v in tables.items()},"database_error":proc.stderr if proc.returncode else None})
if proc.returncode:
    print(proc.stdout); print(proc.stderr,file=sys.stderr); raise SystemExit(proc.returncode)
print(f"Imported official sample files={len(set(d['source'] for d in parsed))}; logical documents={len(parsed)}")
for table in ORDER:
    if tables[table]: print(f"{table}: {len(tables[table])} prepared rows")
print("PostgreSQL transaction: committed")