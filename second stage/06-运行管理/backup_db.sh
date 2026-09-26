#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${PATENT_CONTAINER:-patentdb}"
folder="$ROOT/09-GitHub交付/数据库备份"
mkdir -p "$folder"
docker exec "$name" pg_dump -U postgres -d patentdb -Fc --no-owner --no-acl > "$folder/patentdb-sample.dump.part"
docker exec -i "$name" pg_restore -l < "$folder/patentdb-sample.dump.part" >/dev/null
mv "$folder/patentdb-sample.dump.part" "$folder/patentdb-sample.dump"
echo "数据库逻辑备份：$folder/patentdb-sample.dump"
