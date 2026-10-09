# 数据库实践实验手册：下载、建库、导入、查询、备份与GitHub复现

本手册对应B角色最终交付。所有路径均相对second stage目录；在Ubuntu/WSL终端运行Shell命令，看到patentdb=#后才输入SQL。

## 1. 实验环境

- Ubuntu 22.04 / WSL2、Docker、Python3、curl。
- PostgreSQL 16，当前使用缓存镜像docker.m.daocloud.io/library/postgres:16。
- 默认容器和数据库名称均为patentdb；业务Schema为patentdb；导入审计Schema为stage2_meta。
- 本项目使用Python标准库和Docker中的psql，不要求安装额外Python包。
- Docker未启动时执行sudo service docker start。安装Docker是操作系统准备工作，项目不包含DBMS二进制安装器。

先进入交付目录：

```bash
cd "/home/zjjtju/database/Database/second stage"
docker --version
python3 --version
curl --version
```

在另一台电脑上，请将第一行替换为解压或克隆后的实际目录。

## 2. 官方数据包如何归档与重新下载

原始ZIP与内部RAR按五类放在：

```text
05-官方来源/02-IPDPS补充样例/01-压缩原包/
├── 01-US申请公布/
├── 02-US授权公告/
├── 03-EP全文/
├── 04-EP-DOCDB摘要/
└── 05-EP法律状态/
```

四类基础解析输入在05-官方来源/01-四类基础样例；法律XML和DOCDB通知另有清楚命名的目录；手册在03-数据手册。已解包输入一起随交付包提供，正常复现不需要重新解包RAR。

```bash
# 校验现有五个原始ZIP
python3 -B "02-数据导入/download_official.py"

# 丢失某个原始ZIP时，从官网补下载
python3 -B "02-数据导入/download_official.py" --download

# 重新联网下载临时副本，与归档SHA256比较，随后删除临时副本
python3 -B "02-数据导入/download_official.py" --verify-remote
```

脚本使用官网公共样例下载接口，不包含账户、Cookie或登录密码。清单固定了数据编号、rcId、下载类型、文件位置和SHA256。官方文件若变化会报错，保留当前已审核版本，不静默覆盖。

**已经实际联网验证五类下载成功且SHA256一致**，结果在07-验收结果/官方下载校验.json。原始ZIP只负责归档和下载追溯；导入器读取已解包XML。

## 3. 首次创建数据库

仅在需要一个全新容器/空库时：

```bash
sudo bash "06-运行管理/init_db.sh"
```

脚本会提示输入密码，创建持久卷和容器，依次执行三个SQL、导入基础/补充样例、登记DOCDB通知并检查。密码不写进项目文件。若容器内已有业务表，脚本只启动服务并提示，不重新初始化现有数据。

现有库平时只启动：

```bash
sudo bash "06-运行管理/start.sh"
sudo docker exec -it patentdb psql -U postgres -d patentdb
```

部署脚本中DBMS操作已可随代码上传，包括创建容器、等待就绪、建Schema、约束和索引、导入、备份及检查。Docker运行时数据存放在持久卷中，不是项目源码文件。

## 4. 建表、修正和审计表的顺序

1. 01-create-schema.sql：43张业务表、345个字段的A基线物理实现。
2. 02-audit-migration.sql：本轮已确认的字段适配和约束修正，可重复执行。
3. 03-import-audit.sql：独立stage2_meta，包含import_batch、source_document、publication_state三张技术表及active_publication视图。

因此是**43张业务表 + 3张运行审计表**。将两个Schema混在一起统计会看到46张表，这不是A字典发生了遗漏或重复建表。

## 5. 导入原始样例与新增批次

重放本次审定样例并应用结构修正：

```bash
sudo bash "06-运行管理/update_reviewed.sh"
```

该脚本先备份再更新，是审定样例复现入口。已经建立额外批次数据后，不应把“固定19篇基线验收”误当作全量数据的行数标准。

新增数据按以下格式放入本阶段目录：

```text
05-官方来源/04-新增批次/批次名称/
├── us-application/     美国申请XML
├── us-grant/           美国授权XML
├── ep-fulltext/        EP全文XML
└── ep-docdb/           DOCDB完整记录/增删通知XML
```

只需创建实际有数据的子目录。然后：

```bash
sudo python3 -B "02-数据导入/import_batch.py" \
  --source-root "$PWD/05-官方来源/04-新增批次/批次名称"
```

该入口通过业务键取得实际数据库ID，不使用新批次中的局部编号覆盖旧记录。支持重复导入、更新已映射字段、去掉修订后不再存在的文献子记录；原XML、操作类型、文件、逻辑标识和错误上下文保留在审计表。每批成功日志与业务修改同事务提交；失败时业务写入回滚并单独记录失败原因。

DOCDB处理：A/C按键更新或新增；D软删除；CV/DV记录为撤回通知，不伪造申请。DeleteRekey批次应先处理。依据：[EPO官方ST36说明，第27—36页](https://link.epo.org/web/T09.01%20ST36%20User%20Documentation%20vs%202.5.8.pdf)。官方5条CV已登记，不再属于“未处理数据”。

## 6. SQL查询实验

详细10组查询及预期值在《B角色-最终交接报告.md》。也可在普通终端一并运行：

```bash
sudo docker exec -i patentdb psql -X -U postgres -d patentdb \
  -v ON_ERROR_STOP=1 < "03-测试验收/queries.sql"
```

在psql中查看批次和正常可见文献：

```sql
SELECT batch_id, started_at, status, summary
FROM stage2_meta.import_batch
ORDER BY started_at DESC LIMIT 5;

SELECT raw_operation, disposition, count(*)
FROM stage2_meta.source_document
GROUP BY raw_operation, disposition
ORDER BY raw_operation, disposition;

SELECT publication_id, publn_auth, publn_nr, publn_kind
FROM stage2_meta.active_publication
ORDER BY publication_id LIMIT 10;
```

展示端应优先使用active_publication以排除软删除记录。直接查询patentdb.publication可以看到保留用于追溯的物理记录。

## 7. 简单增删改查与事务实验

以下使用专门的实验键，并最终ROLLBACK，不保留演示数据：

```sql
BEGIN;
INSERT INTO patentdb.keyword(keyword_id, keyword_text, lang_code, source)
VALUES (-999999, 'stage2_lab_demo', 'EN', 'LAB_TEST');

SELECT * FROM patentdb.keyword WHERE keyword_id = -999999;

UPDATE patentdb.keyword
SET keyword_text = 'stage2_lab_updated'
WHERE keyword_id = -999999;

SELECT * FROM patentdb.keyword WHERE keyword_id = -999999;

DELETE FROM patentdb.keyword WHERE keyword_id = -999999;
ROLLBACK;

SELECT count(*) AS demo_rows
FROM patentdb.keyword WHERE keyword_id = -999999;
```

预期最终demo_rows为0。负数实验ID避免消耗生产序列；不要把演示词当作官方关键词。

## 8. 验收与错误定位

```bash
# 固定官方样例快照：43业务表、345字段、19申请/文献
sudo python3 -B "03-测试验收/verify_data.py"

# 独立临时容器：19项结构、幂等、增量、软删除、回滚测试
sudo python3 -B "03-测试验收/integration_test.py"
```

测试中的新增、修改、删除样例明确是测试输入，只进入一次性数据库，测试后清理；不会混入官网样例库。

失败定位SQL：

```sql
SELECT b.batch_id, d.dataset, d.source_file, d.logical_identifier,
       d.xml_path, d.error_type, d.error_message
FROM stage2_meta.import_batch b
JOIN stage2_meta.source_document d USING(batch_id)
WHERE b.status = 'FAILED'
ORDER BY b.started_at DESC, d.source_file, d.document_index;
```

技术表保留原XML用于追溯；根路径加表名/业务键是当前SQL错误定位上下文，并不意味着所有字段都已提供逐叶节点XPath。

## 9. 数据库备份、恢复与可移植性

```bash
sudo bash "06-运行管理/backup_db.sh"
sudo python3 -B "03-测试验收/verify_restore.py"
```

备份文件：09-GitHub交付/数据库备份/patentdb-sample.dump。它是PostgreSQL自定义格式逻辑备份，包含结构、数据、索引、触发器及审计记录；使用pg_restore恢复，不能当普通SQL直接交给psql。[PostgreSQL官方pg_dump说明](https://www.postgresql.org/docs/16/app-pgdump.html)

在接收方已运行PostgreSQL容器、但目标库为空时，可以这样恢复到**独立的新数据库**：

```bash
sudo docker exec patentdb createdb -U postgres patentdb_restore
sudo docker exec -i patentdb pg_restore -U postgres -d patentdb_restore \
  --no-owner --no-acl --exit-on-error \
  < "09-GitHub交付/数据库备份/patentdb-sample.dump"

sudo docker exec -it patentdb psql -U postgres -d patentdb_restore
```

恢复测试脚本会额外创建临时容器，逐表比较43业务表和3审计表的内容指纹，通过后移除。共享dump不包含角色密码或本机Docker卷文件。

## 10. 数据库和DBMS操作能不能一起上传GitHub

**可以上传可复现的数据库交付文件和DBMS操作脚本。GitHub仓库不会替你运行PostgreSQL服务。**

| 内容 | 本次如何交付 |
|---|---|
| SQL结构、约束、索引、查询 | SQL文件随源码上传 |
| 数据库数据 | 样例dump随包提供，也可由官方XML重新导入 |
| DBMS创建/启动/导入/备份操作 | init_db.sh、start.sh、update_reviewed.sh、backup_db.sh和恢复命令 |
| 官方数据原包 | 按五类存放ZIP/RAR并附SHA256、官方下载脚本 |
| 运行中的容器/进程 | 在接收方按脚本启动，不是Git仓库对象 |
| PostgreSQL镜像 | 使用已注明的镜像版本拉取；不必把镜像二进制作为源码提交 |
| 本机Docker数据卷 | 不上传；使用可恢复的逻辑备份代替 |
| 密码、缓存、中间备份 | 已通过忽略规则及打包白名单排除 |

GitHub普通Git拒绝超过100MiB的单文件；较大的后续数据集可使用Git LFS、Releases或其他数据存储，不要反复提交大型数据库转储。[GitHub官方文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

若确需离线移交DBMS镜像，可另行docker save导出压缩镜像作为离线附件；它不属于本次小型GitHub源码包，也不需要接收方上传自己的运行数据卷。

## 11. 打包与仓库上传

```bash
sudo python3 -B "06-运行管理/package_release.py"
```

输出：

- 09-GitHub交付/patentdb-stage2-github.zip：可解压为仓库目录的完整交付包。
- 09-GitHub交付/上传文件清单.json：逐文件路径、大小与SHA256。
- 09-GitHub交付/打包结果.json：ZIP大小、SHA256、CRC检查。
- 09-GitHub交付/数据库备份/patentdb-sample.dump：当前实际数据库快照。

建议把ZIP解压后的目录内容提交为仓库文件，这样GitHub可以直接浏览源码和报告。ZIP也可作为Release附件。文件清单已检查普通Git的100MiB单文件限制。

本次只准备本地交付包，没有创建远程仓库、提交或推送。准备上传时，从解压后的目录按实际仓库地址执行：

```bash
git init
git add .
git commit -m "Complete role B PostgreSQL implementation and reproducible handover"
git branch -M main
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

如果已在现有Git仓库中，不需要重复git init或添加已有origin。原始样例保留来源标识；扩大公开分发范围时按官网数据使用条款处理。

## 12. 下一位同学负责什么

B的建表、来源解析/导入、业务键增量、批次追溯、软删除、验收及实验复现已交付。后续同学继续完成：

- 展示端的列表、分页、检索、多语言选择和软删除过滤；
- 专利分析/挖掘与可视化；
- 更多年份与大规模数据的字段扩展、性能评估及数据维护；
- 全组最终报告整合、答辩演示。

这些是后续扩展和应用工作，不把B的批次处理或数据库验收缺项转交给下一位。
