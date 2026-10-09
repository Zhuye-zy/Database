#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="$ROOT/../01-数据库结构/01-create-schema.sql"
CONTAINER="patentdb-schema-check-$$"
IMAGE="docker.m.daocloud.io/library/postgres:16"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker is not installed or not on PATH." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon is unavailable to this user. Run with sudo or configure Docker access." >&2
  exit 1
fi
if [[ ! -f "$SQL_FILE" ]]; then
  echo "ERROR: schema file not found: $SQL_FILE" >&2
  exit 1
fi

cleanup() {
  docker rm -f -v "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Starting disposable PostgreSQL container ($IMAGE)..."
docker run --detach --name "$CONTAINER" \
  -e POSTGRES_PASSWORD='schema-check-only' \
  -e POSTGRES_DB=patentdb \
  "$IMAGE" >/dev/null

ready=0
for _ in $(seq 1 45); do
  if docker exec "$CONTAINER" pg_isready -U postgres -d patentdb >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 1
done
if [[ "$ready" -ne 1 ]]; then
  echo "ERROR: PostgreSQL did not become ready." >&2
  docker logs "$CONTAINER" >&2 || true
  exit 1
fi

echo "Applying schema..."
docker exec -i "$CONTAINER" psql -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$SQL_FILE"

docker exec -i "$CONTAINER" psql -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$ROOT/../01-数据库结构/02-audit-migration.sql"

docker exec -i "$CONTAINER" psql -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$ROOT/../01-数据库结构/03-import-audit.sql"

tables=$(docker exec "$CONTAINER" psql -U postgres -d patentdb -Atqc "SELECT count(*) FROM information_schema.tables WHERE table_schema='patentdb' AND table_type='BASE TABLE'")
columns=$(docker exec "$CONTAINER" psql -U postgres -d patentdb -Atqc "SELECT count(*) FROM information_schema.columns WHERE table_schema='patentdb'")
fks=$(docker exec "$CONTAINER" psql -U postgres -d patentdb -Atqc "SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname='patentdb' AND c.contype='f'")
indexes=$(docker exec "$CONTAINER" psql -U postgres -d patentdb -Atqc "SELECT count(*) FROM pg_indexes WHERE schemaname='patentdb' AND indexname LIKE 'ix_%'")

printf 'Tables: %s (expected 43)\nColumns: %s (expected 345)\nForeign keys: %s (expected 91)\nSupporting indexes: %s (expected 78)\n' "$tables" "$columns" "$fks" "$indexes"
if [[ "$tables" != 43 || "$columns" != 345 || "$fks" != 91 || "$indexes" != 78 ]]; then
  echo "FAIL: schema totals differ from the expected design." >&2
  exit 1
fi
echo "PASS: PostgreSQL accepted the schema and all structural counts match."