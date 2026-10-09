# 第四阶段：设计文档、汇报 PPT、分析挖掘与最终打包

本阶段由 D 角色完成，基于前三阶段的 43 张业务表、345 字段、3,576 行数据与 151 条测试用例，产出课程报告、汇报 PPT 与分析结论；所有数字由脚本从证据文件注入，报告与 PPT 同源。先看 [提交说明](05-打包/提交说明.md) 与 [问题记录](90-问题记录-D.md)。

## 交付物

| 目录                                         | 内容                                                                                                                                                                  |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01-设计文档/`                             | 课程报告`数据库实践课程报告.docx`、生成脚本（`build_report.py` / `report_content.py` / `report_lib.py`）、绘图脚本 `make_figures.py`、插图 `图/`（21 张） |
| `02-汇报PPT/`                              | 汇报 PPTX（17 页，每页备注含讲稿）与`第四阶段汇报-讲稿.md`（建议 13 分 0 秒）                                                                                       |
| `03-分析挖掘/`                             | 5 个主题 21 条分析 SQL、`run_analysis.py`、`make_charts.py`、结果 CSV/JSON 与 6 张统计图                                                                          |
| `04-流程图与框图/`                         | 用例图、总体流程图、系统框图、导入流程图、验收流程图、关键表关系图（`gen_diagrams.py` 生成）                                                                        |
| `05-打包/`                                 | `package_submission.py`（ZIP + SHA256 清单）、最终提交包与 `提交说明.md`                                                                                          |
| `90-问题记录-D.md`、`92-AI使用记录-D.md` | 本阶段 8 条问题与处理、AI 使用范围与人工核验方式                                                                                                                      |
| `95-审查报告-D.md`                         | 对照《任务分配2.md》的第四阶段独立审查：五项工作逐项比对、实测复现结果、数字一致性、问题与建议                                                                        |

## 一键复现（仓库根目录执行）

```bash
.venv/bin/python "fourth stage/03-分析挖掘/run_analysis.py"   # 21 条分析 SQL → CSV/JSON
.venv/bin/python "fourth stage/03-分析挖掘/make_charts.py"    # 6 张统计图
.venv/bin/python "fourth stage/04-流程图与框图/gen_diagrams.py"
.venv/bin/python "fourth stage/01-设计文档/make_figures.py"   # 21 张报告/PPT 插图
.venv/bin/python "fourth stage/01-设计文档/build_report.py"   # 报告 docx + 自检
.venv/bin/python "fourth stage/02-汇报PPT/build_ppt.py"       # 汇报 PPTX + 讲稿 + 自检
.venv/bin/python "fourth stage/05-打包/package_submission.py" # 提交包 ZIP + SHA256 清单
```

每个脚本结束时都会打印自检结果，失败时返回非零退出码（报告：章节/图表/关键数字；PPT：页序、插图越界与宽高比、关键数字、每页讲稿、文本框溢出估算）。

## 口径与边界

- 结论只在本批样例内成立：19 件申请、19 篇文献、3,576 行，公布年份集中在 1979 / 2014 / 2020。
- 508 条专利引用的被引目标全部在库外（库内解析 0 条）→ 只给“引用方结构”，不做“被引热度”排名。
- `family_citation` 缺少可靠双端族号而保持空表；`keyword` 是基于标题的派生数据（`TITLE_DERIVED`）。
