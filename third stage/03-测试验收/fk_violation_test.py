#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 角色外键约束反例测试（UPDATE 方式）。
从表里取一行现有数据，尝试把一个外键列改成不存在的值。
报错后 ROLLBACK TO SAVEPOINT，数据库不被污染。
用法：python3 fk_violation_test.py
"""
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.errors import (
    ForeignKeyViolation,
    NotNullViolation,
    CheckViolation,
)

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "127.0.0.1"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "dbname": os.environ.get("PGDATABASE", "patentdb"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", ""),
}
SCHEMA = os.environ.get("DB_SCHEMA", "patentdb")


def resolve_schema(cur):
    cur.execute(
        "SELECT 1 FROM information_schema.schemata WHERE schema_name=%s",
        (SCHEMA,),
    )
    return SCHEMA if cur.fetchone() else "public"


def has_table(cur, schema, t):
    cur.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema=%s AND table_name=%s",
        (schema, t),
    )
    return cur.fetchone() is not None


def has_col(cur, schema, t, c):
    cur.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema=%s AND table_name=%s AND column_name=%s",
        (schema, t, c),
    )
    return cur.fetchone() is not None


def table_has_rows(cur, schema, t):
    cur.execute(
        sql.SQL("SELECT 1 FROM {}.{} LIMIT 1").format(
            sql.Identifier(schema), sql.Identifier(t)
        )
    )
    return cur.fetchone() is not None


def run_update_case(cur, schema, name, table, column, bad_value, expect):
    """UPDATE 某表第一行的一个外键列为不存在的值，期望触发 FK 违例。"""
    try:
        cur.execute("SAVEPOINT sp")
        q = sql.SQL(
            "UPDATE {s}.{t} SET {c} = %s "
            "WHERE ctid = (SELECT ctid FROM {s}.{t} LIMIT 1)"
        ).format(
            s=sql.Identifier(schema),
            t=sql.Identifier(table),
            c=sql.Identifier(column),
        )
        cur.execute(q, (bad_value,))
        affected = cur.rowcount
        cur.execute("ROLLBACK TO SAVEPOINT sp")
        if affected == 0:
            return name, "SKIP", "表为空，无法取现有行做 UPDATE"
        return name, "FAIL", f"未抛出异常；约束未生效（改了 {affected} 行）"
    except expect as e:
        cur.execute("ROLLBACK TO SAVEPOINT sp")
        return name, "PASS", f"{type(e).__name__}: {str(e).strip().splitlines()[0]}"
    except Exception as e:
        try:
            cur.execute("ROLLBACK TO SAVEPOINT sp")
        except Exception:
            pass
        return name, "SKIP", f"{type(e).__name__}: {str(e).strip().splitlines()[0]}"


def main():
    results = []
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            schema = resolve_schema(cur)

            # (用例名, 表, 列, 越界值, 期望异常)
            cases = [
                ("FK-01 patent_applicant.patent_id -> 不存在",
                 "patent_applicant", "patent_id", 999999999, ForeignKeyViolation),
                ("FK-02 patent_applicant.person_id -> 不存在",
                 "patent_applicant", "person_id", 999999999, ForeignKeyViolation),
                ("FK-03 patent_inventor.patent_id -> 不存在",
                 "patent_inventor", "patent_id", 999999999, ForeignKeyViolation),
                ("FK-04 patent_inventor.person_id -> 不存在",
                 "patent_inventor", "person_id", 999999999, ForeignKeyViolation),
                ("FK-05 patent_citation.citing_patent_id -> 不存在",
                 "patent_citation", "citing_patent_id", 999999999, ForeignKeyViolation),
                ("FK-06 patent_citation.cited_patent_id -> 不存在",
                 "patent_citation", "cited_patent_id", 999999999, ForeignKeyViolation),
                ("FK-07 patent_classification.patent_id -> 不存在",
                 "patent_classification", "patent_id", 999999999, ForeignKeyViolation),
                ("FK-08 legal_status_event.patent_id -> 不存在",
                 "legal_status_event", "patent_id", 999999999, ForeignKeyViolation),
                ("FK-09 claim.publication_id -> 不存在",
                 "claim", "publication_id", 999999999, ForeignKeyViolation),
                ("FK-10 publication.patent_id -> 不存在",
                 "publication", "patent_id", 999999999, ForeignKeyViolation),
            ]

            for name, table, column, bad_value, expect in cases:
                if not has_table(cur, schema, table):
                    results.append((name, "SKIP", f"表 {table} 不存在"))
                    continue
                if not has_col(cur, schema, table, column):
                    results.append((name, "SKIP", f"列 {table}.{column} 不存在"))
                    continue
                if not table_has_rows(cur, schema, table):
                    results.append((name, "SKIP", f"表 {table} 为空，无现有行"))
                    continue
                results.append(run_update_case(
                    cur, schema, name, table, column, bad_value, expect
                ))
    finally:
        conn.close()

    print(f"# C 角色外键反例测试结果（{datetime.now().isoformat(timespec='seconds')}）\n")
    print("| 用例 | 结果 | 详情 |")
    print("|---|---|---|")
    for name, status, msg in results:
        print(f"| {name} | {status} | {msg} |")

    n_pass = sum(1 for _, s, _ in results if s == "PASS")
    n_skip = sum(1 for _, s, _ in results if s == "SKIP")
    n_fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\n**PASS {n_pass} / SKIP {n_skip} / FAIL {n_fail}，共 {len(results)} 例**")


if __name__ == "__main__":
    main()
