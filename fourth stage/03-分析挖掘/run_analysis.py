#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
D 角色分析挖掘执行器：读取 sql/ 下的分析脚本 → 执行 → 导出证据 → 生成图表。

用法（仓库根目录或本目录执行均可）：
    python3 "fourth stage/03-分析挖掘/run_analysis.py"            # 全部执行 + 出图
    python3 "fourth stage/03-分析挖掘/run_analysis.py" --no-charts

连接方式（依次尝试，不硬编码密码）：
    1) 环境变量 PGHOST/PGPORT/PGDATABASE/PGUSER/PGPASSWORD + psycopg2；
    2) 本地 Docker 容器（默认 patentdb）内的 psql，用 `COPY (…) TO STDOUT WITH CSV HEADER` 取回结果。

输出：
    结果/<分析名>.csv            每条查询一份，含表头（NULL 为空字符串）
    结果/analysis_results.json   全部结果的结构化汇总（行数、列名、数据、执行方式与时间）
    图表/图*.png                 报告与 PPT 用统计图（微软雅黑/黑体渲染）
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL_DIR = HERE / "sql"
RESULT_DIR = HERE / "结果"
CHART_DIR = HERE / "图表"
SCHEMA = os.environ.get("DB_SCHEMA", "patentdb")
CONTAINER = os.environ.get("PATENTDB_CONTAINER", "patentdb")
DB_NAME = os.environ.get("PGDATABASE", "patentdb")
DB_USER = os.environ.get("PGUSER", "postgres")

QUERY_RE = re.compile(r"^--\s*@query:\s*([A-Za-z0-9_]+)\s*\|\s*(.+?)\s*$")


def docker_available() -> bool:
    """容器内 psql 可用则返回 True（无需密码，走本地 socket 信任连接）。"""
    if not shutil.which("docker"):
        return False
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "psql", "-U", DB_USER, "-d", DB_NAME, "-tAc", "SELECT 1"],
        capture_output=True, text=True,
    )
    return proc.returncode == 0 and proc.stdout.strip() == "1"


def run_via_psycopg2(sql: str):
    import psycopg2  # 仅在需要时导入

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=DB_NAME, user=DB_USER,
        password=os.environ.get("PGPASSWORD"),
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            columns = [d[0] for d in cur.description]
            rows = [[("" if v is None else str(v)) for v in r] for r in cur.fetchall()]
        return columns, rows
    finally:
        conn.close()


def run_via_docker(sql: str):
    """用 COPY 把结果集直接导成 CSV，列名与 NULL 语义与 psql 一致。"""
    payload = "COPY (\n" + sql.rstrip().rstrip(";") + "\n) TO STDOUT WITH CSV HEADER;"
    proc = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "psql", "-X", "-U", DB_USER, "-d", DB_NAME,
         "-v", "ON_ERROR_STOP=1", "-c", payload],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "psql 执行失败")
    reader = csv.reader(io.StringIO(proc.stdout))
    rows = list(reader)
    if not rows:
        return [], []
    return rows[0], rows[1:]


def parse_sql_files():
    """把每个 SQL 文件切成 {分析: [(查询名, 说明, SQL文本), ...]}。"""
    analyses = []
    for path in sorted(SQL_DIR.glob("*.sql")):
        current = None
        queries = []
        for line in path.read_text(encoding="utf-8").splitlines():
            m = QUERY_RE.match(line)
            if m:
                current = [m.group(1), m.group(2), []]
                queries.append(current)
                continue
            if current is not None:
                current[2].append(line)
        for item in queries:
            item[2] = "\n".join(item[2]).strip()
        analyses.append({"file": path.name, "title": path.stem, "queries": queries})
    return analyses

def main() -> int:
    ap = argparse.ArgumentParser(description="D 角色：专利数据分析挖掘执行器")
    ap.add_argument("--no-charts", action="store_true", help="只执行 SQL，不生成图表")
    args = ap.parse_args()

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    CHART_DIR.mkdir(parents=True, exist_ok=True)

    use_docker = docker_available()
    driver = "docker exec psql (COPY TO STDOUT)" if use_docker else "psycopg2 (PG* 环境变量)"
    print(f"[信息] 连接方式：{driver}")
    if not use_docker and not os.environ.get("PGPASSWORD"):
        print("[错误] 容器不可用且未设置 PGPASSWORD，无法连接数据库。", file=sys.stderr)
        return 2

    analyses = parse_sql_files()
    if not analyses:
        print(f"[错误] {SQL_DIR} 下没有 SQL 文件。", file=sys.stderr)
        return 2

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "schema": SCHEMA,
        "driver": driver,
        "container": CONTAINER if use_docker else None,
        "analyses": [],
    }

    ok = True
    for analysis in analyses:
        record = {"file": analysis["file"], "title": analysis["title"], "queries": []}
        print(f"\n=== {analysis['title']} ({analysis['file']}) ===")
        for name, description, sql in analysis["queries"]:
            try:
                columns, rows = run_via_docker(sql) if use_docker else run_via_psycopg2(sql)
            except Exception as exc:  # noqa: BLE001 - 失败原因也要写进结果文件
                ok = False
                print(f"[失败] {name}: {exc}", file=sys.stderr)
                record["queries"].append({"name": name, "description": description,
                                          "status": "FAIL", "error": str(exc)})
                continue
            csv_path = RESULT_DIR / f"{name}.csv"
            with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.writer(fh)
                writer.writerow(columns)
                writer.writerows(rows)
            record["queries"].append({
                "name": name, "description": description, "status": "PASS",
                "columns": columns, "row_count": len(rows),
                "csv": f"结果/{csv_path.name}",
                "rows": rows,
            })
            print(f"[通过] {name}：{len(rows)} 行 → 结果/{csv_path.name}")
        summary["analyses"].append(record)

    summary["status"] = "PASS" if ok else "FAIL"
    json_path = RESULT_DIR / "analysis_results.json"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[写出] 结果/{json_path.name}（status={summary['status']}）")

    if not args.no_charts:
        sys.path.insert(0, str(HERE))
        import make_charts  # noqa: E402 - 图表模块与结果同目录
        produced = make_charts.build_all(summary, CHART_DIR)
        print("[图表] 已生成：" + ", ".join(p.name for p in produced))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
