# C角色测试报告

- 测试对象：patentdb（schema `patentdb`，43 张业务表、345 字段）
- 测试人：C
- 日期：2026-10-06
- 测试方法：只读冒烟 + 事务内回滚的反例测试；所有证据可由脚本复现。

## 1. 测试环境

- PostgreSQL 16.15（Docker 镜像 `postgres:16`，容器名 `patentdb`）
- 库来源：由 B 的 `01-create-schema.sql` + `update_reviewed.sh` 建立并导入官方样例
- 连接：`127.0.0.1:5432`，数据库 `patentdb`，schema `patentdb`

## 2. 冒烟测试

脚本：`03-测试验收/smoke_test.py`
证据：`07-验收结果/smoke_result.md`

结论：

- 业务表数量 43，逐表 `LIMIT 10` 全部 PASS
- 空表 1 张：`family_citation`（来源缺口，B 已注明，不虚构）
- `patent` 19 行、`publication` 19 行，与 B 报告一致
- 42 表非空

## 3. 简单多表 JOIN

| 查询 | 结果行数 |
|---|---|
| 申请人三表 JOIN（patent→patent_applicant→person） | 18 |
| 发明人三表 JOIN（patent→patent_inventor→person） | 32 |
| 分类号 JOIN（patent→patent_classification） | 71 |
| 引用表总行数（patent_citation） | 805 |
| 引用专利去重（citing_patent_id） | 9 |
| 权利要求 JOIN（publication→claim） | 184 |
| 法律状态 JOIN（patent→legal_status_event） | 10 |

结论：外键关联正确，行数符合预期。

## 4. 复杂测试与完整性验证

脚本：`03-测试验收/fk_violation_test.py`（UPDATE 方式，事务内 `ROLLBACK TO SAVEPOINT`）

| 用例 | 操作 | 预期 | 实际 | 结论 |
|---|---|---|---|---|
| FK-01 | `patent_applicant.patent_id` 改为不存在值 | 拒绝 | `fk_patent_applicant_patent_id` 触发 | PASS |
| FK-02 | `patent_applicant.person_id` 改为不存在值 | 拒绝 | `fk_patent_applicant_person_id` 触发 | PASS |
| FK-03 | `patent_inventor.patent_id` 改为不存在值 | 拒绝 | `fk_patent_inventor_patent_id` 触发 | PASS |
| FK-04 | `patent_inventor.person_id` 改为不存在值 | 拒绝 | `fk_patent_inventor_person_id` 触发 | PASS |
| FK-05 | `patent_citation.citing_patent_id` 改为不存在值 | 拒绝 | `fk_patent_citation_citing_patent_id` 触发 | PASS |
| FK-06 | `patent_citation.cited_patent_id` 改为不存在值 | 拒绝 | `fk_patent_citation_cited_patent_id` 触发 | PASS |
| FK-07 | `patent_classification.patent_id` 改为不存在值 | 拒绝 | `fk_patent_classification_patent_id` 触发 | PASS |
| FK-08 | `legal_status_event.patent_id` 改为不存在值 | 拒绝 | `fk_legal_status_event_patent_id` 触发 | PASS |
| FK-09 | `claim.publication_id` 改为不存在值 | 拒绝 | `fk_claim_publication_id` 触发 | PASS |
| FK-10 | `publication.patent_id` 改为不存在值 | 拒绝 | `fk_publication_patent_id` 触发 | PASS |

**PASS 10 / SKIP 0 / FAIL 0。**

数据库未被污染：所有用例在 `SAVEPOINT` 内执行，报错后 `ROLLBACK TO SAVEPOINT`，跑完 `patent` / `publication` 仍为 19 行。

## 5. 性能测试与调优

脚本：`03-测试验收/performance_test.sql`
证据：`07-验收结果/performance_before.txt`

| 查询 | 计划要点 | Execution Time |
|---|---|---|
| P1 申请人→专利 三表 JOIN | Seq Scan（patent 19、person 71） | 0.106 ms |
| P2 专利→引用热度 | Index Only Scan（ix_patent_citation_citing_patent_id，805 行） | 0.145 ms |
| P3 技术领域分布 | Seq Scan（patent_classification 71 行） | 0.041 ms |
| P4 申请时间趋势 | Seq Scan（patent 19 行） | 0.038 ms |

**优化结论**：样例数据量小，P1/P3/P4 全表扫描均在 0.2 ms 以下，P2 已由 B 的索引覆盖。当前规模下额外加索引无实际收益，本阶段不引入新索引，仅记录 EXPLAIN 计划与基线耗时。

## 6. 发现的问题与处理

| # | 问题 | 严重度 | 处理 | 状态 |
|---|---|---|---|---|
| 1 | B 快照基于 CRLF，本地 WSL 的 Git 把 XML 转为 LF，导入 SHA256 校验失败 | 中 | 临时把 `05-官方来源/01-四类基础样例/*.xml` 转 CRLF，导入后 `git checkout --` 恢复 | 已解决 |
| 2 | 脚本假设 `patent_applicant.publication_id`，实际用 `patent_id` | 低 | 对照外键清单修正 | 已解决 |
| 3 | 脚本假设 `person.name`，实际列名是 `person_name` | 低 | 对照 `\d patentdb.person` 修正 | 已解决 |
| 4 | 反例测试用 INSERT 时被 NOT NULL 列先拦下，没测到 FK | 低 | 改用 UPDATE 现有行 + `ROLLBACK TO SAVEPOINT` | 已解决 |

## 7. 前端运行证据

- 首页 43 表：`07-验收结果/截图/01-首页-43表.png`
- 专利表 19 行：`07-验收结果/截图/02-patent表-19行.png`
- 专利详情页（patent_id=1）：`07-验收结果/截图/03-专利详情-patent1.png`

## 8. 测试结论

- 冒烟：43 表全部可查询，空表口径与 B 一致
- 完整性：10 项外键反例全部被拒绝，数据库未被污染
- 性能：4 组典型查询耗时均在毫秒级，无新增索引需求
- 前端：43 表 LIST 与专利详情页均可正常运行
- **数据库可交付 D 使用**
