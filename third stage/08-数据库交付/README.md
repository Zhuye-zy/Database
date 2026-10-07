# 第三阶段数据库交付

`patentdb-phase3.dump` 是 PostgreSQL 16 自定义格式逻辑备份，含 43 张业务表、3 张审计表、视图、约束、索引和数据；不含角色密码。SHA256 见 `../07-验收结果/fresh_acceptance.json`。

使用 PostgreSQL 16 容器恢复到一个独立的空数据库（以下 patentdb 是接收方容器名）：

```bash
docker exec patentdb createdb -U postgres patentdb_phase3_restore
docker exec -i patentdb pg_restore -U postgres -d patentdb_phase3_restore \
  --no-owner --no-acl --exit-on-error < "third stage/08-数据库交付/patentdb-phase3.dump"
```

恢复后配置 PGDATABASE=patentdb_phase3_restore，再执行 C 的 run_all.py 和启动前端。不能将自定义格式 dump 直接交给 psql。复现备份与恢复验收使用 `06-运行管理/verify_fresh.py`；它自动逐表比较业务及审计数据内容。
