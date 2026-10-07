#!/usr/bin/env python3
"""Exact FK violations (ten UPDATE and three INSERT); savepoints, rollback, no SKIP, nonzero on failure."""
from test_support import *
from psycopg2.errors import ForeignKeyViolation
CASES=[("patent_applicant","patent_id"),("patent_applicant","person_id"),
       ("patent_inventor","patent_id"),("patent_inventor","person_id"),
       ("patent_citation","citing_patent_id"),("patent_citation","cited_patent_id"),
       ("patent_classification","patent_id"),("legal_status_event","patent_id"),
       ("claim","publication_id"),("publication","patent_id")]
def main():
    report=Report("fk_result");conn=None
    try:
        conn=connect()
        with conn.cursor() as cur:
            require_schema(cur); before=fingerprint(cur)
            for table,column in CASES:
                def check(table=table,column=column):
                    expected=f"fk_{table}_{column}"
                    cur.execute("SELECT conrelid::regclass::text,confrelid::regclass::text,confkey FROM pg_constraint WHERE conname=%s AND contype='f' AND connamespace=(SELECT oid FROM pg_namespace WHERE nspname=%s)",(expected,SCHEMA));fk=cur.fetchone()
                    require(fk is not None,"缺少指定外键: "+expected)
                    cur.execute(sql.SQL("SELECT 1 FROM {} LIMIT 1").format(sql.Identifier(table)));require(cur.fetchone() is not None,"必测表为空: "+table)
                    cur.execute("SAVEPOINT fk_case")
                    try:
                        cur.execute(sql.SQL("UPDATE {} SET {}=%s WHERE ctid=(SELECT ctid FROM {} LIMIT 1)").format(sql.Identifier(table),sql.Identifier(column),sql.Identifier(table)),(-9223372036854775807,))
                        require(False,"违规 UPDATE 未被外键拒绝")
                    except ForeignKeyViolation as error:
                        require(error.diag.constraint_name==expected,"触发了其他约束: "+str(error.diag.constraint_name))
                        return {"constraint":expected,"sqlstate":error.pgcode}
                    finally:cur.execute("ROLLBACK TO SAVEPOINT fk_case");cur.execute("RELEASE SAVEPOINT fk_case")
                report.case(table+"."+column,check)
            # INSERT cases supply all required fields so FK, rather than NOT NULL,
            # is what rejects the row. Explicit negative IDs do not consume sequences.
            cur.execute("SELECT publication_id,patent_id FROM publication ORDER BY publication_id LIMIT 1")
            publication_id,patent_id=cur.fetchone()
            inserts=[
                ("insert_invalid_family", "fk_patent_family_member_family_id",
                 "INSERT INTO patent_family_member(member_id,family_id,member_seq) VALUES(-990001,-9223372036854775807,1)",()),
                ("insert_invalid_citing_patent", "fk_patent_citation_citing_patent_id",
                 "INSERT INTO patent_citation(citation_id,citing_patent_id,citing_publication_id,citation_type,citn_seq) VALUES(-990002,-9223372036854775807,%s,'P',990002)",(publication_id,)),
                ("insert_invalid_cited_patent", "fk_patent_citation_cited_patent_id",
                 "INSERT INTO patent_citation(citation_id,citing_patent_id,citing_publication_id,cited_patent_id,citation_type,citn_seq) VALUES(-990003,%s,%s,-9223372036854775807,'P',990003)",(patent_id,publication_id))]
            for name,constraint,query,params in inserts:
                def check(constraint=constraint,query=query,params=params):
                    cur.execute("SAVEPOINT insert_fk")
                    try:
                        cur.execute(query,params)
                        require(False,"违规 INSERT 未被外键拒绝")
                    except ForeignKeyViolation as error:
                        require(error.diag.constraint_name==constraint,"INSERT 触发了其他约束")
                        return {"constraint":constraint,"sqlstate":error.pgcode,"operation":"INSERT"}
                    finally:cur.execute("ROLLBACK TO SAVEPOINT insert_fk");cur.execute("RELEASE SAVEPOINT insert_fk")
                report.case(name,check)
            report.case("all_table_contents_unchanged",lambda:require(fingerprint(cur)==before,"反例测试改变业务内容"))
        conn.rollback()
    except Exception as error:report.case("setup",lambda:require(False,str(error)))
    finally:
        if conn:conn.rollback();conn.close()
    return report.finish()
if __name__=="__main__":raise SystemExit(main())
