# 第三阶段：C 角色数据测试验证与前端展示

先看：04-报告与基线/C角色-最终交接报告.md。B 已交付 43 表库与导入程序（phase-2），本阶段在此基础上完成测试验证与前端展示。

- 数据库：沿用 B 的 patentdb Docker 容器，本阶段脚本均为只读或事务内回滚
- 前端：01-前端应用/app.py（Flask），首页列出全部 43 张业务表，支持任意表分页浏览与专利详情多表关联展示
- 测试：03-测试验收 冒烟、外键反例、性能测试，证据粘入 04-报告与基线/C角色-测试报告.md

## 快速开始

启动数据库（B 的环境）：

    cd ~/database/Database/"second stage"
    sudo bash "06-运行管理/start.sh"

跑 C 的测试（导出真实结果后粘入测试报告）：

    cd ~/database/Database/"third stage/03-测试验收"
    export PGPASSWORD=你的密码
    python3 smoke_test.py
    python3 fk_violation_test.py
    sudo docker exec -i patentdb psql -X -U postgres -d patentdb -v ON_ERROR_STOP=1 < performance_test.sql

启动前端：

    cd ../01-前端应用
    pip3 install -r requirements.txt
    python3 app.py

## 目录结构

    01-前端应用/        Flask 前端（app.py + templates）
    03-测试验收/        三个测试脚本
    04-报告与基线/      C角色-测试报告.md、C角色-最终交接报告.md
    07-验收结果/        smoke_result.md、performance_before.txt、截图/
    90-问题记录-C.md
    92-AI使用记录-C.md
    93-D角色交接说明.md

## 数据口径

- patent/publication 各 19 行；43 表中 42 表非空
- family_citation 为空表，来源缺口，禁止虚构
- keyword 系 TITLE_DERIVED

## 注意

- 不上传 __pycache__、不含密码
- 若重跑 update_reviewed.sh，需先把 05-官方来源/01-四类基础样例 下的 XML 转 CRLF（详见 90-问题记录-C.md）
