#!/usr/bin/env bash
# 专利数据库项目一键运行：启动 patentdb 容器 -> 第三阶段验收 -> 启动前端展示
# 依据：README.md、second stage/06-运行管理/*.sh、third stage/README.md
# 用法：bash run.sh            （验收通过后前台运行前端，Ctrl+C 退出）
#       SKIP_TESTS=1 bash run.sh  （跳过验收，只启动前端）
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
name="${PATENT_CONTAINER:-patentdb}"

if ! docker info >/dev/null 2>&1; then
  echo "Docker 未就绪；请先启动 Docker（如 sudo service docker start）。" >&2; exit 1
fi
if ! docker inspect "$name" >/dev/null 2>&1; then
  echo "未找到容器 $name。请先按 second stage/06-运行管理/init_db.sh 初始化空库，" >&2
  echo "或按 third stage/08-数据库交付/README.md 从 patentdb-phase3.dump 恢复。" >&2; exit 1
fi

docker start "$name" >/dev/null
ready=""
for _ in $(seq 1 45); do
  if docker exec "$name" pg_isready -U postgres -d patentdb >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
[[ -n "$ready" ]] || { echo "数据库就绪超时，请查看 docker logs $name" >&2; exit 1; }
echo "数据库已就绪：$name / patentdb（PostgreSQL 16）"

# 连接参数：PGPASSWORD 未设置时从容器自身配置读取，避免硬编码密码
export PGHOST="${PGHOST:-127.0.0.1}" PGPORT="${PGPORT:-5432}"
export PGDATABASE="${PGDATABASE:-patentdb}" PGUSER="${PGUSER:-postgres}"
export DB_SCHEMA="${DB_SCHEMA:-patentdb}"
if [[ -z "${PGPASSWORD:-}" ]]; then
  PGPASSWORD="$(docker inspect "$name" --format '{{range .Config.Env}}{{println .}}{{end}}' \
    | sed -n 's/^POSTGRES_PASSWORD=//p' | head -n 1)"
fi
export PGPASSWORD
[[ -n "$PGPASSWORD" ]] || { echo "无法取得数据库密码，请显式设置 PGPASSWORD。" >&2; exit 1; }

PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  py="$(command -v python3.10 || command -v python3)"
  echo "缺少虚拟环境 .venv，请先执行：" >&2
  echo "  $py -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install -r \"third stage/01-前端应用/requirements.txt\"" >&2
  exit 1
fi

if [[ "${SKIP_TESTS:-0}" != "1" ]]; then
  echo "运行第三阶段验收（smoke / 外键反例 / 复杂边界 / 前端）..."
  "$PY" -B "$ROOT/third stage/03-测试验收/run_all.py"
fi

echo "启动前端：http://127.0.0.1:${APP_PORT:-5000}/  （Ctrl+C 停止）"
exec "$PY" "$ROOT/third stage/01-前端应用/app.py"
