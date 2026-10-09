# 专利数据关系数据库实践

题目 5：美国申请公布、授权公告、EP 全文、DOCDB 及法律状态官方样例。

- [第一阶段：概念设计](第一阶段/00-README.md)：实体、字典、ER 图与来源说明。
- [第二阶段：建库与导入](<second stage/README.md>)：43 业务表、3 审计表、带注释导入器与样例。
- [第三阶段：验证与展示（补齐版）](<third stage/README.md>)：严格验收、复杂与边界测试、全表前端、数据库恢复包。
- [第四阶段：设计文档、汇报 PPT、分析挖掘与最终打包](<fourth stage/README.md>)：课程报告 docx、17 页汇报 PPT 与讲稿、21 条分析 SQL、流程图与提交包。

## 一键运行（已部署数据库）

环境需要 **Python 3.10 或更新版本**（第二阶段导入脚本使用 `Path.is_relative_to` 等 3.9+ 接口）、Docker（可访问 PostgreSQL 16 镜像）。

```bash
# 1. 只用一次：建立虚拟环境并安装依赖（python3.10 按本机实际路径替换）
python3.10 -m venv .venv
.venv/bin/python -m pip install -r "third stage/01-前端应用/requirements.txt"

# 2. 启动容器 patentdb -> 第三阶段验收 -> 启动前端（http://127.0.0.1:5000/）
bash run.sh
```

`run.sh` 自动启动 `patentdb` 容器、等待数据库就绪、设置连接参数（未显式给出 `PGPASSWORD` 时从容器配置读取，不硬编码密码）、执行 `run_all.py` 验收，最后前台运行前端；`SKIP_TESTS=1 bash run.sh` 可只启动前端。

第三阶段完整复现（一次性容器：建库、导入、全部测试、dump 与独立恢复比对）从仓库根目录执行：

```bash
.venv/bin/python "third stage/06-运行管理/verify_fresh.py"
```

第三阶段数据基线为 patent/publication 各 19，42/43 业务表非空；family_citation 为空是可靠来源缺口，不虚构。测试只使用临时容器或回滚事务。最新验收及数据库恢复说明见第三阶段目录。

第四阶段（D 角色）的课程报告、汇报 PPT 与讲稿、分析挖掘结果、流程图与最终提交包见 [fourth stage/README.md](<fourth stage/README.md>)；报告与 PPT 的数字均取自前三阶段的结果文件，口径同源。
