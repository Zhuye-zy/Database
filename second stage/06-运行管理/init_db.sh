#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${PATENT_CONTAINER:-patentdb}"
image="${POSTGRES_IMAGE:-docker.m.daocloud.io/library/postgres:16}"
port="${PATENT_PORT:-5432}"
if ! docker info >/dev/null 2>&1; then echo "Docker未就绪，请先sudo service docker start" >&2; exit 1; fi
if ! docker inspect "$name" >/dev/null 2>&1; then
 if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then read -rsp "设置数据库密码: " POSTGRES_PASSWORD; echo; fi
 [[ -n "$POSTGRES_PASSWORD" ]] || { echo "密码不能为空" >&2; exit 1; }
 export POSTGRES_PASSWORD
 docker volume create "${name}_data" >/dev/null
 docker run -d --name "$name" -e POSTGRES_PASSWORD -e POSTGRES_DB=patentdb \
   -p "127.0.0.1:$port:5432" -v "${name}_data:/var/lib/postgresql/data" "$image"
 unset POSTGRES_PASSWORD
fi
export PATENT_CONTAINER="$name"
bash "$ROOT/06-运行管理/start.sh"
exists="$(docker exec "$name" psql -X -U postgres -d patentdb -Atqc "SELECT to_regclass('patentdb.patent') IS NOT NULL")"
if [[ "$exists" == "t" ]]; then
 echo "业务库已存在；未重新初始化。需要更新时运行update_reviewed.sh。"; exit 0
fi
docker exec -i "$name" psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$ROOT/01-数据库结构/01-create-schema.sql"
bash "$ROOT/06-运行管理/update_reviewed.sh"
