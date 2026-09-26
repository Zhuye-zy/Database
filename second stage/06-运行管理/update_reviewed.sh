#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
name="${PATENT_CONTAINER:-patentdb}"
bash "$ROOT/06-运行管理/start.sh"
backup="$ROOT/08-历史备份/数据库更新-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
docker exec "$name" pg_dump -U postgres -d patentdb -Fc > "$backup/patentdb.dump"
docker exec -i "$name" psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$ROOT/01-数据库结构/02-audit-migration.sql"
docker exec -i "$name" psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < "$ROOT/01-数据库结构/03-import-audit.sql"
export PATENT_CONTAINER="$name"
export PYTHONDONTWRITEBYTECODE=1
python3 -B "$ROOT/02-数据导入/import_samples.py" --refresh-reviewed
python3 -B "$ROOT/02-数据导入/import_enrichment.py" --refresh-reviewed
python3 -B "$ROOT/02-数据导入/import_batch.py" --operations-file "$ROOT/05-官方来源/02-IPDPS补充样例/02-DOCDB原文/DOCDB-201724-CreateDelete-PubDate20170609AndBefore-EP-0001.xml"
python3 -B "$ROOT/03-测试验收/verify_data.py"
echo "更新及检查完成；更新前备份：$backup/patentdb.dump"
