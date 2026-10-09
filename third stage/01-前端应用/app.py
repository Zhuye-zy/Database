# -*- coding: utf-8 -*-
"""
C 角色前端展示：Flask 应用
- 首页：列出 patentdb schema 下全部业务表 + 行数
- /table/<name>：任意表分页浏览
- /patent/<pid>：专利详情（申请人/发明人/分类号/引用/权利要求/法律状态）

运行前：
  export PGPASSWORD=你的密码
  export DB_SCHEMA=patentdb
  python3 app.py
"""
import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template, request, abort, url_for

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "127.0.0.1"),
    "port": int(os.environ.get("PGPORT", "5432")),
    "dbname": os.environ.get("PGDATABASE", "patentdb"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", ""),
}
SCHEMA = os.environ.get("DB_SCHEMA", "patentdb")
PAGE_SIZE = max(1, int(os.environ.get("PAGE_SIZE", "50")))


def get_conn():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(readonly=True, autocommit=True)
    return conn


def resolve_schema(cur):
    cur.execute(
        "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s",
        (SCHEMA,),
    )
    if cur.fetchone():
        return SCHEMA
    raise RuntimeError(f"指定 schema 不存在：{SCHEMA}")


def list_tables(cur, schema):
    cur.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
        (schema,),
    )
    return [r["table_name"] for r in cur.fetchall()]


def table_exists(cur, schema, name):
    cur.execute(
        "SELECT 1 FROM information_schema.tables "
        "WHERE table_schema=%s AND table_name=%s",
        (schema, name),
    )
    return cur.fetchone() is not None


def get_columns(cur, schema, table):
    cur.execute(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema=%s AND table_name=%s
        ORDER BY ordinal_position
        """,
        (schema, table),
    )
    return cur.fetchall()


@app.route("/")
def index():
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schema = resolve_schema(cur)
            tables = list_tables(cur, schema)
            rows = []
            for t in tables:
                cur.execute(
                    sql.SQL("SELECT COUNT(*) AS c FROM {}.{}").format(
                        sql.Identifier(schema), sql.Identifier(t)
                    )
                )
                rows.append({"name": t, "count": cur.fetchone()["c"]})
    finally:
        conn.close()
    return render_template(
        "index.html", rows=rows, schema=schema, total=len(rows)
    )


@app.route("/table/<name>")
def table_view(name):
    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1
    order_by = request.args.get("order_by", "")
    order_dir = request.args.get("order_dir", "ASC").upper()
    if order_dir not in ("ASC", "DESC"):
        order_dir = "ASC"

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schema = resolve_schema(cur)
            if not table_exists(cur, schema, name):
                abort(404, "表不存在")

            cols = get_columns(cur, schema, name)
            col_names = [c["column_name"] for c in cols]
            if order_by not in col_names:
                order_by = col_names[0] if col_names else None

            cur.execute(
                sql.SQL("SELECT COUNT(*) AS c FROM {}.{}").format(
                    sql.Identifier(schema), sql.Identifier(name)
                )
            )
            total = cur.fetchone()["c"]
            total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
            if page > total_pages:
                page = total_pages
            offset = (page - 1) * PAGE_SIZE

            if order_by:
                q = sql.SQL(
                    "SELECT * FROM {}.{} ORDER BY {} {} LIMIT %s OFFSET %s"
                ).format(
                    sql.Identifier(schema),
                    sql.Identifier(name),
                    sql.Identifier(order_by),
                    sql.SQL(order_dir),
                )
            else:
                q = sql.SQL(
                    "SELECT * FROM {}.{} LIMIT %s OFFSET %s"
                ).format(sql.Identifier(schema), sql.Identifier(name))
            cur.execute(q, (PAGE_SIZE, offset))
            rows = cur.fetchall()
    finally:
        conn.close()

    return render_template(
        "table.html",
        table=name,
        schema=schema,
        rows=rows,
        cols=cols,
        page=page,
        total=total,
        total_pages=total_pages,
        order_by=order_by,
        order_dir=order_dir,
    )


def _query(cur, q, params=()):
    """SQL failures must remain failures, never masquerade as empty data."""
    cur.execute(q, params)
    return cur.fetchall()


@app.errorhandler(psycopg2.Error)
@app.errorhandler(RuntimeError)
def database_error(error):
    app.logger.error("数据库加载失败: %s", error)
    return render_template("error.html"), 503


@app.route("/patent/<int:pid>")
def patent_detail(pid):
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schema = resolve_schema(cur)

            pat = _query(
                cur,
                sql.SQL("SELECT * FROM {}.patent WHERE patent_id = %s").format(
                    sql.Identifier(schema)
                ),
                (pid,),
            )
            if not pat:
                abort(404, "未找到该专利")
            patent = pat[0]

            pubs = _query(
                cur,
                sql.SQL(
                    "SELECT * FROM stage2_meta.active_publication WHERE patent_id = %s"
                ),
                (pid,),
            )

            applicants = _query(
                cur,
                sql.SQL(
                    "SELECT pe.* FROM {s}.patent_applicant pa "
                    "JOIN {s}.person pe ON pe.person_id = pa.person_id "
                    "WHERE pa.patent_id = %s"
                ).format(s=sql.Identifier(schema)),
                (pid,),
            )
            inventors = _query(
                cur,
                sql.SQL(
                    "SELECT pe.* FROM {s}.patent_inventor pi "
                    "JOIN {s}.person pe ON pe.person_id = pi.person_id "
                    "WHERE pi.patent_id = %s"
                ).format(s=sql.Identifier(schema)),
                (pid,),
            )
            classifications = _query(
                cur,
                sql.SQL(
                    "SELECT * FROM {}.patent_classification "
                    "WHERE patent_id = %s"
                ).format(sql.Identifier(schema)),
                (pid,),
            )
            citations = _query(
                cur,
                sql.SQL(
                    "SELECT * FROM {}.patent_citation "
                    "WHERE citing_patent_id = %s"
                ).format(sql.Identifier(schema)),
                (pid,),
            )
            legal = _query(
                cur,
                sql.SQL(
                    "SELECT * FROM {}.legal_status_event "
                    "WHERE patent_id = %s"
                ).format(sql.Identifier(schema)),
                (pid,),
            )

            # claim 挂在 publication 上，通过 publication_id 关联
            claims = []
            for pub in pubs:
                claims.extend(_query(
                    cur,
                    sql.SQL(
                        "SELECT * FROM {}.claim WHERE publication_id = %s"
                    ).format(sql.Identifier(schema)),
                    (pub["publication_id"],),
                ))
    finally:
        conn.close()

    return render_template(
        "patent_detail.html",
        patent=patent,
        pubs=pubs,
        applicants=applicants,
        inventors=inventors,
        classifications=classifications,
        citations=citations,
        claims=claims,
        legal=legal,
        pid=pid,
    )


if __name__ == "__main__":
    
    app.run(host=os.environ.get("APP_HOST", "127.0.0.1"),
            port=int(os.environ.get("APP_PORT", "5000")), debug=False)
