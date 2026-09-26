# B角色最终交接报告：数据库实施与可复现交付

交接日期：2026-09-26  
目录：/home/zjjtju/database/Database/second stage  
完成依据：A→B正式交接说明、43表345字段字典、实体关系约束要求及本次实际验收。

## 一、B角色完成情况

**B角色的建表、来源解析、样例导入、业务键增量导入、批次记录、DOCDB软删除、错误追溯、查询验收与部署交接已完成。**

上一轮的批次/增删缺项已补齐并通过19项隔离集成测试。5条CV经EPO正式说明确认为撤回通知，已登记审计，不是需要补造申请的普通专利。保留43张业务表、345字段，另设stage2_meta的3张运行审计表。

| B任务 | 最终交付 | 实际证据 |
|---|---|---|
| PostgreSQL建表 | 43业务表，43PK、91FK、22UNIQUE、12CHECK、78辅助索引 | 空库建表、字段/约束/索引清单 |
| ISA及复合外键 | 人员子类延迟约束，复合FK、弱实体唯一键 | 含反例的隔离测试 |
| 四类样例解析导入 | 17文件18逻辑文献；额外法律样例1篇 | 来源SHA256和逐字段对照 |
| 文本/多值/日期 | EP多语言、族明细、NPL全文、raw日期 | 19,907个基础字段值、194条补充来源行核对 |
| 业务键与幂等 | 新批次取得实际ID；C新增/A修订、删除过期子记录 | 新增、修订、重复导入测试 |
| DOCDB操作 | D软删除、A恢复、过期D忽略，CV/DV仅记通知 | 真实CV及隔离C/A/D用例 |
| 批次与错误追溯 | 原XML、批次、状态和失败上下文；成功审计与业务同事务 | 解析错误及SQL回滚测试 |
| 查询/EXPLAIN | 10组简单查询、多表JOIN、执行计划 | 本文件及queries.sql |
| 下载与复现 | 下载脚本、分类原包、初始化、备份恢复 | 五类远程SHA256校验及恢复验收 |
| 仓库交接 | 实验手册、样例dump、打包脚本和上传清单 | 09-GitHub交付 |

**数据现状**：patent/publication各19行；43表中42表非空。family_citation结构与约束完整，但来源没有可确认的双端族号，合法保留0行。原LOCAL占位族已删除，不以虚构数据填满表。

样例验收完成不代表已取得网站全量专利或覆盖未来所有XML版本。原XML完整保留；来源没有提供的维表信息保持NULL。

## 二、目录与入口

| 目录 | 作用 |
|---|---|
| 01-数据库结构 | 01基线DDL、02审核修正、03批次审计 |
| 02-数据导入 | import_samples/import_enrichment为基线重放；sample_mapping/batch_extensions为映射；import_batch为新增批次；download_official为下载 |
| 03-测试验收 | verify_data基线核验；integration_test为19项隔离测试；verify_restore验证恢复；queries为示例 |
| 04-报告与基线 | 本交接报告、审核报告、实验手册和A基线 |
| 05-官方来源 | 分类ZIP/RAR、基础XML、法律及DOCDB原文、手册、下载清单 |
| 06-运行管理 | init_db、start、update_reviewed、backup_db、package_release |
| 07-验收结果 | 行数/字段/约束/索引、对照、测试、下载、恢复、清理证据 |
| 08-历史备份 | 最初及最近回退备份，不进入上传包 |
| 09-GitHub交付 | 当前dump、最终ZIP、上传清单和打包结果 |

完整步骤见《实验手册-数据库与GitHub复现.md》：下载、DBMS操作、建库导入、SQL增删改查、事务、备份恢复及仓库上传。

## 三、先启动，再进入SQL终端

以下在Ubuntu/WSL的普通终端执行，不是在psql里执行：

```bash
cd "/home/zjjtju/database/Database/second stage"
sudo bash "06-运行管理/start.sh"
sudo docker exec -it patentdb psql -U postgres -d patentdb
```

看到 `patentdb=#` 后，再输入下方SQL和psql命令。退出用 `\q`。
如果Docker服务尚未运行，先执行 `sudo service docker start`，再执行start.sh。

## 四、可直接复制的简单SQL查询与预期结果

### 测试1：确认连接、表结构与字段

```sql
SELECT current_database(), version();

\dt patentdb.*
\d+ patentdb.patent

SELECT count(*) AS table_count
FROM information_schema.tables
WHERE table_schema = 'patentdb' AND table_type = 'BASE TABLE';

SELECT count(*) AS column_count
FROM information_schema.columns
WHERE table_schema = 'patentdb';
```

**说明**：确认连接到正确的数据库和Schema。预期表数43、字段数345。
`\dt` 和 `\d+` 是psql元命令；普通SQL工具可以运行两个SELECT代替。

### 测试2：直接查看专利主表

```sql
SELECT patent_id, appln_auth, appln_nr, appln_kind,
       appln_filing_date, appln_filing_date_raw
FROM patentdb.patent
ORDER BY patent_id
LIMIT 10;

SELECT count(*) AS patent_count FROM patentdb.patent;
SELECT count(*) AS publication_count FROM patentdb.publication;
```

**说明**：检查确实有数据，而不只是建了空表。两个count预期都是19。
patent表示申请实体；publication表示其公布/授权文献，概念上不是同一实体，本样例恰好各19行。

### 测试3：按数据来源统计

```sql
SELECT d.dataset_code, count(p.publication_id) AS publication_count
FROM patentdb.dataset d
LEFT JOIN patentdb.publication p ON p.dataset_id = d.dataset_id
GROUP BY d.dataset_id, d.dataset_code
ORDER BY d.dataset_id;
```

预期：US_APP_PUB=4、US_GRANT=8、EP_FULLTEXT=4、EP_DOCDB_ABS=2、EP_LEGAL_STATUS=1。
第五类是为补充法律事件而引入的官方样例，不是原始四类题目范围中又增加了一个必选数据源。

### 测试4：文献与标题关联

```sql
SELECT p.publication_id, p.publn_auth, p.publn_nr, p.publn_kind,
       t.lang_code, left(t.title_text, 100) AS title_preview
FROM patentdb.publication p
LEFT JOIN patentdb.title t
  ON t.publication_id = p.publication_id AND t.lang_code = 'EN'
ORDER BY p.publication_id
LIMIT 20;
```

**说明**：展示一个简单JOIN。使用LEFT JOIN，来源没有英文标题的文献也会保留，标题为NULL不等于导入失败。

### 测试5：查看EP多语言权利要求

```sql
SELECT p.publn_nr, c.lang_code, count(*) AS claim_count
FROM patentdb.publication p
JOIN patentdb.claim c ON c.publication_id = p.publication_id
WHERE p.publn_auth = 'EP'
GROUP BY p.publn_nr, c.lang_code
ORDER BY p.publn_nr, c.lang_code;

SELECT c.claim_number, left(c.claim_text, 180) AS claim_preview
FROM patentdb.publication p
JOIN patentdb.claim c ON c.publication_id = p.publication_id
WHERE p.publn_auth = 'EP' AND p.publn_nr = '0712096'
  AND c.lang_code = 'EN'
ORDER BY c.claim_number
LIMIT 3;
```

**预期**：0712096的DE/EN/FR各10条；0890251各14条。号码前导零不能省略。

### 测试6：检查非专利引用全文

```sql
SELECT npl_id, length(npl_biblio) AS text_length,
       left(npl_biblio, 180) AS preview
FROM patentdb.non_patent_citation
ORDER BY length(npl_biblio) DESC
LIMIT 3;
```

**预期**：最长正文721字符。这里的left只截短显示，数据库保存的是完整正文。

### 测试7：查看专利的申请人

```sql
SELECT p.appln_auth, p.appln_nr,
       a.sequence_nr, n.person_name, n.person_type
FROM patentdb.patent p
JOIN patentdb.patent_applicant a ON a.patent_id = p.patent_id
JOIN patentdb.person n ON n.person_id = a.person_id
ORDER BY p.patent_id, a.sequence_nr
LIMIT 10;
```

**说明**：演示申请、角色关联表和人员实体的三表查询；同一人可通过不同关联表承担不同角色。

### 测试8：查看法律状态事件

```sql
SELECT e.event_seq_nr, e.event_auth, e.event_code,
       e.event_publn_date, left(e.event_text, 120) AS event_preview
FROM patentdb.legal_status_event e
ORDER BY e.patent_id, e.event_seq_nr;
```

**预期**：10行。这是法律样例的事件记录，不意味着系统拥有全球全部法律状态。

### 测试9：检查不完整日期没有被伪造成完整日期

```sql
SELECT cited_doc_number, cited_doc_date_raw, cited_doc_date
FROM patentdb.patent_citation
WHERE cited_doc_date_raw LIKE '%00'
ORDER BY citation_id
LIMIT 10;

SELECT count(*) AS wrongly_filled_dates
FROM patentdb.patent_citation
WHERE (cited_doc_date_raw LIKE '%00' OR cited_doc_date_raw = '99991231')
  AND cited_doc_date IS NOT NULL;
```

**预期**：第二个查询为0；月精度原值仍在raw列，DATE为空。

### 测试10：确认外键状态与真实族数据

```sql
SELECT count(*) AS foreign_keys,
       count(*) FILTER (WHERE convalidated) AS validated_foreign_keys
FROM pg_constraint
WHERE contype = 'f' AND connamespace = 'patentdb'::regnamespace;

SELECT family_id, family_type, source_family_id
FROM patentdb.patent_family
ORDER BY family_id;

SELECT count(*) AS family_citation_count FROM patentdb.family_citation;
```

**预期**：外键91/91；真实族3个；族引用0条。族引用空表是已记录的来源缺口，原来的负数来源族号和LOCAL占位族已移除。

## 五、批次审计与软删除查询

在psql执行：

~~~sql
SELECT batch_id, started_at, status, summary
FROM stage2_meta.import_batch ORDER BY started_at DESC LIMIT 5;

SELECT raw_operation, disposition, count(*)
FROM stage2_meta.source_document
WHERE batch_id = (
 SELECT batch_id FROM stage2_meta.import_batch
 WHERE status='SUCCEEDED' ORDER BY started_at DESC LIMIT 1
)
GROUP BY raw_operation, disposition ORDER BY raw_operation;

SELECT publication_id, publn_auth, publn_nr, publn_kind
FROM stage2_meta.active_publication ORDER BY publication_id LIMIT 10;
~~~

标准批次包含18篇正常文献和5条CV；法律样例由补充导入器处理。重复导入增加审计批次，不增加重复业务记录。展示端使用active_publication，物理表保留软删除记录供追溯。

操作依据：[EPO官方ST36说明，第27—36页](https://link.epo.org/web/T09.01%20ST36%20User%20Documentation%20vs%202.5.8.pdf)。CV/DV不补造文献；D软删除。B已经实现，不再交给下一位补做。

## 六、终端检查与打包

用\\q退出psql后运行：

~~~bash
cd "/home/zjjtju/database/Database/second stage"
sudo python3 -B "03-测试验收/verify_data.py"
sudo python3 -B "03-测试验收/integration_test.py"
python3 -B "02-数据导入/download_official.py"
sudo bash "06-运行管理/backup_db.sh"
sudo python3 -B "03-测试验收/verify_restore.py"
sudo python3 -B "06-运行管理/package_release.py"
~~~

verify_data核验固定基线，不把19篇当作新增批次总数要求。integration_test的合成测试只进临时库；verify_restore比较43业务表和3审计表。最终ZIP和上传清单位于09-GitHub交付。

## 七、数据库和DBMS操作如何上传仓库

**可以上传SQL、导入/运行脚本、官方样例和数据库逻辑备份。运行中的PostgreSQL服务与Docker数据卷不作为Git仓库服务上传；接收方按脚本启动。**

样例dump使用pg_restore恢复，脚本负责创建、启动、导入、备份和测试。[PostgreSQL官方pg_dump说明](https://www.postgresql.org/docs/16/app-pgdump.html)

原包已分US申请、US授权、EP全文、DOCDB摘要、EP法律五类；可从官网重下校验，包内也保留已解包输入。无需将PostgreSQL镜像二进制或本机数据卷加入源码仓库。

GitHub普通Git限制单文件100MiB，打包脚本会检查；后续大数据可用LFS或Release附件。[GitHub文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)

本次未创建远程仓库、commit或push。交付包排除真实密码、历史回退备份、Python缓存和下载临时文件。

## 八、下一位同学负责的工作

以下为应用和扩展，B的批次导入与验收已完成：

1. 各表列表、分页、筛选、详情关联、多语言切换。
2. 展示端使用active_publication，按需查看物理记录及批次历史。
3. 专利统计、引用/族分析、关键词检索及可视化。
4. 更多年份与大规模数据、性能评估、参考字典维护；新XML版本先做回归。
5. 整合全组报告、运行截图和答辩演示。

接手顺序：解压/克隆 → 实验手册 → 初始化或恢复 → 基线检查 → 本报告10组SQL → 批次检查 → 展示与分析。

数据解释：
- keyword/patent_keyword为TITLE_DERIVED，不能称为官方直接提供的关键词。
- 未知国别标志为NULL，image_file为来源文件名，不能声称图片已全部下载。
- family_citation空表是来源缺口，禁止恢复虚构族号。
- 43业务表与3审计表分开统计，业务字段仍345。
- 合成测试变更不进入正式样例库。
