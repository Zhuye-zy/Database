#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C 角色冒烟测试：43 表逐表 LIMIT 10 + 行数清单 + 简单 JOIN。
输出：标准输出 + third stage/07-验收结果/smoke_result.md
用法：python3 smoke_test.py
"""
import os
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "127.0.0.1"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "dbname": os.environ.get("PGDATABASE", "patentdb"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", ""),
}
SCHEMA = os.environ.get("DB_SCHEMA", "patentdb")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "07-验收结果")


def resolve_schema(cur):
    cur.execute(
        "SELECT 1 FROM information_schema.schemata WHERE schema_name=%s",
        (SCHEMA,),
    )
    return SCHEMA if cur.fetchone() else "public"


def list_tables(cur, schema):
    cur.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema=%s AND table_type='BASE TABLE' "
        "ORDER BY table_name",
        (schema,),
    )
    return [r["table_name"] for r in cur.fetchall()]


def main():
    out = []
    out.append(f"# 冒烟测试结果（{datetime.now().isoformat(timespec='seconds')}）\n\n")

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schema = resolve_schema(cur)
            out.append(f"- schema：`{schema}`\n")

            cur.execute("SELECT version() AS v")
            out.append(f"- PostgreSQL：`{cur.fetchone()['v']}`\n")

            tables = list_tables(cur, schema)
            out.append(f"- 业务表数量：**{len(tables)}**\n\n")

            out.append("## 1. 逐表 LIMIT 10 + 行数\n\n")
            out.append("| # | 表名 | 行数 | LIMIT 10 |\n")
            out.append("|---|---|---|---|\n")

            empty = []
            for i, t in enumerate(tables, 1):
                cur.execute(
                    sql.SQL("SELECT COUNT(*) AS c FROM {}.{}").format(
                        sql.Identifier(schema), sql.Identifier(t)
                    )
                )
                cnt = cur.fetchone()["c"]
                if cnt == 0:
                    empty.append(t)
                try:
                    cur.execute(
                        sql.SQL("SELECT * FROM {}.{} LIMIT 10").format(
                            sql.Identifier(schema), sql.Identifier(t)
                        )
                    )
                    cur.fetchall()
                    ok = "PASS"
                except Exception as e:
                    ok = f"FAIL ({e})"
                out.append(f"| {i} | {t} | {cnt} | {ok} |\n")

            out.append(f"\n- 空表数量：**{len(empty)}**\n")
            if empty:
                out.append(f"- 空表清单：{', '.join(empty)}\n")

            out.append("\n## 2. 简单 JOIN 验证\n\n")
            joins = [
                ("申请人三表 JOIN（patent→patent_applicant→person）",
                 "SELECT COUNT(*) AS c FROM {s}.patent p "
                 "JOIN {s}.patent_applicant pa ON pa.patent_id = p.patent_id "
                 "JOIN {s}.person pe ON pe.person_id = pa.person_id"),
                ("发明人三表 JOIN（patent→patent_inventor→person）",
                 "SELECT COUNT(*) AS c FROM {s}.patent p "
                 "JOIN {s}.patent_inventor pi ON pi.patent_id = p.patent_id "
                 "JOIN {s}.person pe ON pe.person_id = pi.person_id"),
                ("分类号 JOIN（patent→patent_classification）",
                 "SELECT COUNT(*) AS c FROM {s}.patent p "
                 "JOIN {s}.patent_classification pc "
                 "ON pc.patent_id = p.patent_id"),
                ("引用表行数（patent_citation）",
                 "SELECT COUNT(*) AS c FROM {s}.patent_citation"),
                ("引用热度 TOP（citing_patent_id 分组）",
                 "SELECT COUNT(DISTINCT citing_patent_id) AS c "
                 "FROM {s}.patent_citation"),
                ("权利要求 JOIN（publication→claim）",
                 "SELECT COUNT(*) AS c FROM {s}.publication p "
                 "JOIN {s}.claim c ON c.publication_id = p.publication_id"),
                ("法律状态 JOIN（patent→legal_status_event）",
                 "SELECT COUNT(*) AS c FROM {s}.patent p "
                 "JOIN {s}.legal_status_event l ON l.patent_id = p.patent_id"),
            ]
            for name, tmpl in joins:
                try:
                    cur.execute(tmpl.format(s=schema))
                    out.append(f"- {name}：{cur.fetchone()['c']} 行\n")
                except Exception as e:
                    out.append(f"- {name}：FAIL — {e}\n")
    finally:
        conn.close()

    text = "".join(out)
    print(text)

    os.makedirs(OUTDIR, exist_ok=True)
    target = os.path.join(OUTDIR, "smoke_result.md")
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n[已写入] {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
