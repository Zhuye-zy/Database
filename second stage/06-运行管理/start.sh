#!/usr/bin/env bash
set -euo pipefail
name="${PATENT_CONTAINER:-patentdb}"
if ! docker info >/dev/null 2>&1; then
 echo "Docker不可用。先运行 sudo service docker start，再用sudo执行本脚本。" >&2; exit 1
fi
if ! docker inspect "$name" >/dev/null 2>&1; then
 echo "未找到容器 $name；请按README的空库初始化步骤创建。" >&2; exit 1
fi
docker start "$name" >/dev/null
for _ in $(seq 1 45); do
 if docker exec "$name" pg_isready -U postgres -d patentdb >/dev/null 2>&1; then
  echo "数据库已就绪：$name / patentdb"
  echo "进入SQL终端：sudo docker exec -it $name psql -U postgres -d patentdb"
  exit 0
 fi
 sleep 1
done
echo "数据库就绪超时，请查看 docker logs $name" >&2; exit 1
