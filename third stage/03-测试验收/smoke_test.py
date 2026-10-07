#!/usr/bin/env python3
"""Validate exact B baseline or explicitly selected extended data; read only."""
import argparse
from test_support import *

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--extended", action="store_true", help="新增批次库：仅校验表集合和可查询性，不比较固定样例行数")
    args=parser.parse_args(); report=Report("smoke_result")
    conn=None
    try:
        conn=connect(readonly=True); conn.autocommit=True
        with conn.cursor() as cur:
            require_schema(cur)
            for table, expected in sorted(BASELINE.items()):
                def check(table=table, expected=expected):
                    cur.execute(sql.SQL("SELECT * FROM {}.{} LIMIT 10").format(sql.Identifier(SCHEMA),sql.Identifier(table))); sample=cur.fetchall()
                    cur.execute(sql.SQL("SELECT count(*) FROM {}.{}").format(sql.Identifier(SCHEMA),sql.Identifier(table))); count=cur.fetchone()[0]
                    if not args.extended: require(count==expected,f"{table}: expected={expected}, actual={count}")
                    return {"rows":count,"sample_rows":len(sample),"expected":None if args.extended else expected}
                report.case(table,check)
            joins=[("applicants",18,"SELECT count(*) FROM patent p JOIN patent_applicant a USING(patent_id) JOIN person n USING(person_id)"),
                   ("inventors",32,"SELECT count(*) FROM patent p JOIN patent_inventor a USING(patent_id) JOIN person n USING(person_id)"),
                   ("classifications",71,"SELECT count(*) FROM patent p JOIN patent_classification c USING(patent_id) JOIN classification d USING(scheme_code,symbol)"),
                   ("claims",184,"SELECT count(*) FROM publication p JOIN claim c USING(publication_id)"),
                   ("legal_status",10,"SELECT count(*) FROM patent p JOIN legal_status_event e USING(patent_id)")]
            for name,expected,query in joins:
                def check(expected=expected,query=query):
                    cur.execute(query);count=cur.fetchone()[0]
                    if not args.extended:require(count==expected,f"JOIN expected={expected}, actual={count}")
                    return {"rows":count}
                report.case(name,check)
    except Exception as error: report.case("setup",lambda:require(False,str(error)))
    finally:
        if conn:conn.close()
    return report.finish()
if __name__=="__main__":raise SystemExit(main())
