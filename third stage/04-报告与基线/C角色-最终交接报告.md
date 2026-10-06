# C 角色最终交接报告：数据测试验证与前端展示

- 目录：/home/syl114514/database/Database/third stage
- 完成依据：B 交付的 patentdb 库（phase-2，43 表 345 字段）、B 角色最终交接报告及本次实际验收

## 一、C 角色完成情况

C 角色的全表冒烟测试、复杂查询与完整性验证、性能检查、前端列表展示与专利详情展示已完成。

| C 任务 | 最终交付 | 实际证据 |
|---|---|---|
| 冒烟测试 | 43 张业务表逐表 LIMIT 10 + 行数清单 | 03-测试验收/smoke_test.py 输出，见测试报告 §2 |
| 简单 JOIN 验证 | 申请人/发明人/分类号/引用/权利要求/法律状态 7 组查询 | smoke_test.py §3 |
| 外键约束反例 | 10 组违规 UPDATE 全部按预期拒绝，事务回滚不污染库 | fk_violation_test.py，测试报告 §4 |
| 性能调优 | 4 组典型查询 EXPLAIN ANALYZE，加索引前后结论 | performance_test.sql + performance_before.txt |
| 前端展示 | 43 表 LIST + 专利详情页（申请人/发明人/分类号/引用/权利要求/法律状态） | 01-前端应用/，运行截图 |
| Debug 与反馈 | 4 个问题，全部已修复 | 90-问题记录-C.md |

数据现状（C 接手时核验）：patent/publication 各 19 行；43 表中 42 表非空；family_citation 依 B 结论保留 0 行。C 阶段未做任何业务数据变更；全部测试只读或事务内回滚。

## 二、目录与入口

| 目录 | 作用 |
|---|---|
| 01-前端应用 | app.py 主程序、templates 模板、requirements.txt |
| 03-测试验收 | smoke_test.py 冒烟；fk_violation_test.py 约束反例；performance_test.sql 性能 |
| 04-报告与基线 | 本交接报告、C角色-测试报告.md |
| 07-验收结果 | smoke_result.md、performance_before.txt、截图/ |
| 90-问题记录-C.md | 本阶段遇到的问题与解决 |
| 92-AI使用记录-C.md | AI 辅助使用记录 |
| 93-D角色交接说明.md | 给 D 的正式交接 |

## 三、先启动，再操作

启动数据库（B 的脚本）：

    cd ~/database/Database/"second stage"
    sudo bash "06-运行管理/start.sh"

跑 C 的测试：

    cd ~/database/Database/"third stage/03-测试验收"
    export PGPASSWORD='你的密码'
    export DB_SCHEMA=patentdb
    python3 smoke_test.py
    python3 fk_violation_test.py

启前端：

    cd ../01-前端应用
    python3 app.py

## 四、验收操作（供老师/D 复现）

1. 浏览器打开 http://<WSL_IP>:5000/ ，看到 43 张业务表及行数
2. 点 patent ，看到 19 行分页列表
3. 打开 /patent/1 ，看到专利主表、公布文献、申请人、发明人、分类号、引用、权利要求、法律状态
4. python3 smoke_test.py ，输出 43 表逐表行数与 PASS
5. python3 fk_violation_test.py ，10 例全 PASS

## 五、前端设计说明

- 通用表浏览器由 information_schema 驱动，新增表无需改代码即可 LIST；表名经白名单校验（只接受 information_schema 中真实存在的表），杜绝 SQL 注入
- 详情页按 B 的 schema 关联：
  - patent 主表
  - publication 通过 patent_id
  - patent_applicant / patent_inventor 通过 patent_id + person_id
  - patent_classification 通过 patent_id
  - patent_citation 通过 citing_patent_id
  - claim 通过 publication_id
  - legal_status_event 通过 patent_id

## 六、终端检查与打包

    cd ~/database/Database/"third stage/03-测试验收"
    python3 smoke_test.py > ../../07-验收结果/smoke_result.md

## 七、如何上传仓库

- 上传前端源码、测试脚本、报告；不上传 __pycache__、不含密码
- 数据库本体仍按 B 的方案由 dump 交付
- 单文件不超过 100 MiB

## 八、下一位同学（D）负责的工作

1. 汇总 A/B/C 产出，撰写完整设计文档与汇报 PPT
2. 基于本库做 3~5 项分析查询（技术领域分布、申请人排名、引用热度、时间趋势），图表化
3. 可复用本阶段前端作为展示入口，或在其上加分析图表页
4. 流程图、伪代码、框图设计；README 与最终打包

接手顺序：phase-3 分支，启动数据库，本报告第四节五个验收操作，截图取数
