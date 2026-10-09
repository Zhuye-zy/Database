# 第三阶段：数据导入、测试验证与前端展示

本阶段在远程 phase-3（442a8b9）基础上补齐，保留 phase-2 的 43 张业务表、345 字段及官方样例口径。先看 [测试报告](04-报告与基线/C角色-测试报告.md)。

## 环境与依赖

需要 Python 3.10 或更新版本、Docker、PostgreSQL 16。实际验收环境：Python 3.14、Flask 3.0.3、psycopg2-binary 2.9.11、PostgreSQL 16.15。Docker 权限按主机配置处理；以下命令均从仓库根目录运行。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r "third stage/01-前端应用/requirements.txt"
```

## 一键全新验收（推荐）

```bash
.venv/bin/python "third stage/06-运行管理/verify_fresh.py"
```

使用唯一名称的一次性容器和随机本机端口，执行原始 XML SHA256 校验、三个建库 SQL、基础/补充/批次导入、故障注入验收、全部 C 测试、查询计划、46 表内容一致性、dump 和独立数据库恢复比较。结束后自动删除自己的容器，不修改已有 patentdb。

结果写入 `third stage/07-验收结果/`，成功退出码 0、失败非零。数据库交付文件为 `08-数据库交付/patentdb-phase3.dump`。完整验收只使用官方样例；测试临时引用和边界文本均回滚。

## 已有数据库验收与前端

已部署 B 数据库时先执行 B 的 `06-运行管理/start.sh`。配置真实连接信息（不要提交密码）：

```bash
export PGHOST=127.0.0.1 PGPORT=5432 PGDATABASE=patentdb PGUSER=postgres DB_SCHEMA=patentdb
read -rsp '数据库密码: ' PGPASSWORD; echo
export PGPASSWORD
.venv/bin/python "third stage/03-测试验收/run_all.py"
.venv/bin/python "third stage/01-前端应用/app.py"
```

浏览 `http://127.0.0.1:5000/`。43 表列表展示物理追溯记录；点击 patent 表的 patent_id 打开详情，详情只展示 `stage2_meta.active_publication` 中的活动文献及其权利要求。数据库错误返回 HTTP 503 并明确显示“数据加载失败”。默认关闭 debug，远程展示可显式设置 APP_HOST。

`run_all.py` 是固定官方样例验收；新增批次库可单独执行 `smoke_test.py --extended`，只校验表集合与可查询性，不强制 19 篇行数。完整基线测试不要直接套用扩大后的数据库。反例及边界测试有事务回滚和内容校验，运行期间应避免其他程序并发改写待验收库。

## 数据与来源规则

- patent/publication 各 19；43 业务表中 42 表非空；另有 3 审计表。
- family_citation 缺少可靠的双端官方族号，保留空表。
- keyword 是 TITLE_DERIVED；引用包含专利和非专利文献，库外目标保留原始号码。
- second stage/.gitattributes 已将 XML 设为 -text，17 个基础 XML 按原始 CRLF 字节保存；原 SHA256 快照未修改。新克隆无需手动转换。
- 旧截图、performance_before.txt 是原 C 阶段历史证据；最新验收以 *_result.json、performance_current.txt 和 fresh_acceptance.json 为准。
