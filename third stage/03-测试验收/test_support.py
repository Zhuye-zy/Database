"""Shared C acceptance utilities; transaction rollback and content checks."""
from pathlib import Path
import os, json, hashlib, datetime
import psycopg2
from psycopg2 import sql
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SCHEMA = os.environ.get("DB_SCHEMA", "patentdb")
BASELINE = {r["table"]: r["rows"] for r in json.loads(
    (REPO / "second stage/07-验收结果/现有数据库/逐表行数.json").read_text())}

def connect(readonly=False):
    conn = psycopg2.connect(host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"), dbname=os.environ.get("PGDATABASE", "patentdb"),
        user=os.environ.get("PGUSER", "postgres"), password=os.environ.get("PGPASSWORD", ""), connect_timeout=10)
    conn.set_session(readonly=readonly)
    return conn

def require_schema(cur):
    cur.execute("SELECT 1 FROM information_schema.schemata WHERE schema_name=%s", (SCHEMA,))
    if not cur.fetchone(): raise AssertionError("指定 schema 不存在: " + SCHEMA)
    cur.execute(sql.SQL("SET search_path TO {}, public").format(sql.Identifier(SCHEMA)))
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'", (SCHEMA,))
    actual = {r[0] for r in cur.fetchall()}
    if actual != set(BASELINE): raise AssertionError(f"业务表集合不匹配: missing={sorted(set(BASELINE)-actual)}, extra={sorted(actual-set(BASELINE))}")

def fingerprint(cur):
    result = {}
    for table in sorted(BASELINE):
        cur.execute(sql.SQL("SELECT count(*), md5(coalesce(string_agg(row_to_json(x)::text, E'\\n' ORDER BY row_to_json(x)::text),'')) FROM {}.{} x").format(sql.Identifier(SCHEMA), sql.Identifier(table)))
        result[table] = cur.fetchone()
    return result

class Report:
    def __init__(self, name): self.name, self.results = name, []
    def case(self, name, function):
        try:
            detail = function()
            self.results.append({"case": name, "status": "PASS", "detail": detail})
        except Exception as error:
            self.results.append({"case": name, "status": "FAIL", "detail": str(error)})
    def finish(self):
        ok = bool(self.results) and all(r["status"] == "PASS" for r in self.results)
        payload = {"timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "PASS" if ok else "FAIL", "cases": self.results}
        out = ROOT / "07-验收结果"; out.mkdir(exist_ok=True)
        (out / (self.name + ".json")).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if ok else 1

def require(condition, message):
    if not condition: raise AssertionError(message)
