# 92 · C 角色 AI 使用记录

| # | 工具 | 用途 | 人工核对情况 |
|---|---|---|---|
| 1 | Kimi / 其他 | 生成前端 Flask 框架与三个测试脚本初稿、交接报告格式参考 | 列名、SQL 全部对照 B 的 \d 输出与 02-数据字典.csv 人工校验；报告数字由真实运行结果替换 |
| 2 | AI 助手 | 协助定位 patent_applicant.publication_id 改为 patent_id、person.name 改为 person_name、CRLF SHA256 校验失败等问题 | 每条修改都由本人在本地 psql 复现后再写入脚本 |
