# 专利数据关系数据库实践

题目 5：美国申请公布、授权公告、EP 全文、DOCDB 及法律状态官方样例。

- [第一阶段：概念设计](第一阶段/00-README.md)：实体、字典、ER 图与来源说明。
- [第二阶段：建库与导入](<second stage/README.md>)：43 业务表、3 审计表、带注释导入器与样例。
- [第三阶段：验证与展示（补齐版）](<third stage/README.md>)：严格验收、复杂与边界测试、全表前端、数据库恢复包。

第三阶段完整复现从仓库根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r "third stage/01-前端应用/requirements.txt"
.venv/bin/python "third stage/06-运行管理/verify_fresh.py"
```

环境需要 Docker（可访问 PostgreSQL 16 镜像）。第三阶段数据基线为 patent/publication 各 19，42/43 业务表非空；family_citation 为空是可靠来源缺口，不虚构。测试只使用临时容器或回滚事务。最新验收及数据库恢复说明见第三阶段目录。课程 PPT、分析图表及总设计文档仍由 D 角色整合。
