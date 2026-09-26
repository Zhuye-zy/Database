# 第二阶段：B 角色 PostgreSQL 实施与核验

**先看：** [B角色最终交接报告](04-报告与基线/B角色-最终交接报告.md)，技术核验细节见 [审核报告](04-报告与基线/B角色-阶段二审核报告.md)。修正版在本 WSL 目录内，当前四类基础样例及法律样例已落库。43 张业务表、345 字段；42 表非空。族引用没有可靠的双端官方族号，保留空表。

B角色建表、样例导入、业务键增量、批次追溯及DOCDB软删除已完成，19项隔离检查通过。详见交接报告和[实验手册](04-报告与基线/实验手册-数据库与GitHub复现.md)。业务表43张，另有审计表3张；没有声称下载网站全量数据。

## 目录与文件用途

| 目录 | 文件及作用 |
|---|---|
| 01-数据库结构 | 01-create-schema.sql基线建表；02-audit-migration.sql审核修正；03-import-audit.sql三张审计表及视图 |
| 02-数据导入 | import_samples.py：四类基础样例；import_enrichment.py：族、法律事件等补充映射；import_support.py公共工具；sample_mapping.py/batch_extensions.py映射；import_batch.py增量；download_official.py下载；source_snapshot.json基线SHA256 |
| 03-测试验收 | verify_data.py：现有库只读核验并输出证据；integration_test.py：临时容器集成验收；verify_schema.sh：只测空库DDL；queries.sql：查询与执行计划；audit_source_status.py源文献清单；verify_restore.py备份恢复验收 |
| 04-报告与基线 | 最终审核报告、设计变更记录；设计基线子目录保存A的字典和交接要求 |
| 05-官方来源 | 四类基础样例、新官网下载包及解包XML、五份数据手册；来源README逐类解释 |
| 06-运行管理 | start.sh启动；init_db.sh首次初始化；update_reviewed.sh备份更新；backup_db.sh备份；package_release.py打包 |
| 07-验收结果 | 现有数据库 / 临时数据库：表数、逐字段对照、约束和索引清单、字段覆盖、查询计划、集成测试；导入日志及源文献清单 |
| 08-历史备份 | 原代码、旧报告、最初及最近回退备份；不进入上传包 |
| 09-GitHub交付 | 当前dump、最终ZIP、上传清单和SHA256 |

## 现有数据库：启动、检查、查看

以下命令均在 **Ubuntu / WSL 终端**执行：

```bash
cd "/home/zjjtju/database/Database/second stage"

# 启动已有 patentdb 容器
sudo bash "06-运行管理/start.sh"

# 只读检查现有数据库，证据输出到07-验收结果
sudo python3 -B "03-测试验收/verify_data.py"

# 执行多表查询及EXPLAIN
sudo docker exec -i patentdb psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < "03-测试验收/queries.sql"

# 进入交互SQL终端
sudo docker exec -it patentdb psql -U postgres -d patentdb
```

进入 psql 后：

```sql
\dt patentdb.*
\d+ patentdb.patent
SELECT patent_id, appln_auth, appln_nr, appln_kind, appln_filing_date
FROM patentdb.patent ORDER BY patent_id LIMIT 10;
\q
```

## 重跑验收 / 重新应用本次修正

```bash
# 一次性临时数据库：建表、两次导入、全表内容比对、约束反例、日期与XML边界
sudo python3 -B "03-测试验收/integration_test.py"

# 仅生成源文件处理状态清单
python3 -B "03-测试验收/audit_source_status.py"

# 已有库需要重新应用修正时才执行：自动备份，随后更新及核验
sudo bash "06-运行管理/update_reviewed.sh"
```

审定样例重放锁定SHA256；新增批次使用import_batch.py --source-root，按业务键取得实际ID。目录布局与操作规则见实验手册。

## 从全新数据库部署

已有 `patentdb` 容器时使用上面的启动命令。以下只用于容器不存在的环境：

```bash
cd "/home/zjjtju/database/Database/second stage"
read -rsp "设置PostgreSQL密码: " POSTGRES_PASSWORD
echo
export POSTGRES_PASSWORD
sudo docker volume create patentdb_data
sudo --preserve-env=POSTGRES_PASSWORD docker run -d --name patentdb \
  -e POSTGRES_PASSWORD -e POSTGRES_DB=patentdb \
  -p 127.0.0.1:5432:5432 -v patentdb_data:/var/lib/postgresql/data \
  docker.m.daocloud.io/library/postgres:16
unset POSTGRES_PASSWORD
sudo bash "06-运行管理/start.sh"
sudo docker exec -i patentdb psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < "01-数据库结构/01-create-schema.sql"
sudo bash "06-运行管理/update_reviewed.sh"
```

使用现有缓存镜像以避免此前的 Docker Hub 超时。数据库内容位于 Docker 持久卷；代码、来源材料、报告和备份均在本阶段目录。

## GitHub交付包

运行 sudo python3 -B "06-运行管理/package_release.py" 可重新打包。最终包、数据库dump和上传清单位于09-GitHub交付；完整步骤见实验手册。
