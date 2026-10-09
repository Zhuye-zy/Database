#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按《报告模板.docx》生成第四阶段课程报告（Word）。

流程：
  1) 打开模板，复用其页面设置、样式与五个一级标题的自动编号（numId=5，格式「一、」）；
  2) 由 report_content.build_blocks(ctx) 取得五个一级标题下的正文块；
  3) 渲染每一块（段落 / 二三级标题 / 项目符号 / 代码块 / 三线表 / 居中插图）并搬到对应标题之后；
  4) 删除模板中的示例占位文字，填写封面与分工表；
  5) 重新打开生成的文件自检（章节、表格、图片、编号与数字一致性）。

ctx 中的所有数字都来自仓库内可复核的证据文件：
    * second stage/07-验收结果/现有数据库/逐表行数.json  → 43 张表的行数
    * third stage/07-验收结果/*_result.json             → 测试用例数与通过数
    * fourth stage/03-分析挖掘/结果/analysis_results.json → 分析 SQL（5 个主题 21 条）的结果
    * 结构统计（表/字段/主键/外键/唯一/检查/非空/索引）为库内实测值，见 STATS 注释中的查询。

运行：python3 "fourth stage/01-设计文档/build_report.py"
"""
from __future__ import annotations

import json
from pathlib import Path

import report_content as rc
import report_lib as rl

DIR = Path(__file__).resolve().parent
REPO = DIR.parents[1]
OUT = DIR / "数据库实践课程报告.docx"
FIGDIR = DIR / "图"

TABLES_JSON = REPO / "second stage" / "07-验收结果" / "现有数据库" / "逐表行数.json"
ANALYSIS_JSON = REPO / "fourth stage" / "03-分析挖掘" / "结果" / "analysis_results.json"
RESULT_DIR = REPO / "third stage" / "07-验收结果"
FRESH_JSON = RESULT_DIR / "fresh_acceptance.json"
DUMP = REPO / "third stage" / "08-数据库交付" / "patentdb-phase3.dump"
PROBLEM_MD = REPO / "fourth stage" / "90-问题记录-D.md"

# 库内实测结构统计（patentdb schema）：
#   tables/fields   : information_schema.tables / columns
#   pk/fk/uq/chk    : pg_constraint contype IN ('p','f','u','c')
#   复合唯一键       : pg_constraint contype='u' AND array_length(conkey,1) > 1
#   notnull         : pg_attribute.attnotnull
#   idx             : pg_index（43 主键索引 + 22 唯一索引 + 78 辅助索引 = 143）
STATS = {
    "tables": 43, "fields": 345, "pk": 43, "fk": 91, "uq": 22, "uq_multi": 18,
    "chk": 12, "notnull": 154, "idx": 143, "idx_aux": 78,
}

# 43 张业务表按 ER 六域归类（与第一阶段的域划分一致，表名之和必须等于 43）
DOMAINS = [
    ("域1 著录与文献",
     ["patent", "publication", "title", "abstract", "description_section", "drawing", "claim",
      "claim_dependency", "application_type", "kind_code", "language", "dataset"],
     "patent / publication 为属主，title、abstract、claim、drawing、description_section 为文献部件弱实体"),
    ("域2 人员与角色",
     ["person", "natural_person", "organization", "patent_applicant", "patent_inventor",
      "patent_assignee", "patent_agent", "patent_examiner"],
     "person 为父实体，natural_person / organization 为 ISA 子类，五张角色关联表区分角色"),
    ("域3 分类",
     ["classification_scheme", "classification", "patent_classification", "ipc_techn_field"],
     "IPC / CPC 双体系共存，分类号维表与专利按顺序号关联"),
    ("域4 引用",
     ["citation_category", "patent_citation_category", "patent_citation", "non_patent_citation"],
     "引用分类维表 + 专利文献引用（含库外被引号码）与非专利文献引用明细"),
    ("域5 专利族与程序关系",
     ["patent_family", "patent_family_member", "family_abstract", "family_citation",
      "family_member_application_ref", "family_member_publication_ref", "priority_claim",
      "related_application", "international_application", "designated_state", "country_office"],
     "族与族成员、族摘要/族引用、优先权与关联申请、国际申请与指定国"),
    ("域6 法律状态与关键词",
     ["legal_event_code", "legal_status_event", "keyword", "patent_keyword"],
     "法律事件码维表 + 事件明细；keyword 与 patent_keyword 为本组基于标题的派生增强表"),
]

# 测试脚本：结果文件 → 用例数与通过数从 JSON 实时统计，不手工填写
TESTS = [
    ("acceptance_failure_test.py", "acceptance_failure_result.json",
     "故障注入：缺 schema、空 schema、被引外键被绕过等，必须以非 0 退出码失败"),
    ("smoke_test.py", "smoke_result.json",
     "冒烟：43 张业务表逐表 SELECT，核对行数与样例行数"),
    ("fk_violation_test.py", "fk_result.json",
     "外键违规：14 类违反外键的写入必须被数据库拒绝（SQLSTATE 23503）"),
    ("complex_boundary_test.py", "complex_boundary_result.json",
     "复杂与边界：多表连接、专利族成员、空值、超长文本、特殊字符"),
    ("frontend_test.py", "frontend_result.json",
     "前端：首页 43 表、逐表页面、专利详情与错误路径（HTTP 503）"),
]

ENV = [
    ["操作系统 / 容器", "Linux（WSL2 发行版）+ Docker Engine；数据库以容器 patentdb 运行"],
    ["数据库管理系统", "PostgreSQL 16（镜像 postgres:16，实例版本 16.15）"],
    ["数据库对象", "业务 schema patentdb（43 表 / 345 字段）+ 审计 schema stage2_meta（3 表 1 视图）"],
    ["Python 环境", "Python 3.10.13（仓库虚拟环境 .venv，报告与 PPT 生成即在此环境完成）"],
    ["数据库驱动", "psycopg2-binary 2.9.10（third stage/01-前端应用/requirements.txt 固定；"
                   "C 阶段在 Python 3.14 下需 ≥2.9.11）"],
    ["导入与验收脚本", "second stage/02-数据导入 与 third stage/06-运行管理/verify_fresh.py"],
    ["前端应用", "Flask 3.0.3（默认 127.0.0.1:5000，只读；数据库异常返回 HTTP 503）"],
    ["分析与图表", "SQL 通过 docker exec psql 执行；图表用 matplotlib 生成（显式指定中文字体）"],
    ["报告与 PPT", "python-docx 基于《报告模板.docx》生成；python-pptx 生成汇报 PPT"],
    ["版本管理", "Git；.gitattributes 把基础 XML 标记为 -text，保留原始 CRLF 与 SHA256 指纹"],
    ["数据来源", "官方 5 类样例数据集、17 个基础 XML（导入前记录 SHA256 快照）"],
]

DELIVER = [
    ["第一阶段/", "需求分析、数据字典（43 表 345 字段）、6 张分域 E-R 图、方案设计初稿、问题记录与 AI 记录"],
    ["second stage/", "43 表建表 SQL、审计迁移 SQL、导入脚本与批次入口、设计变更说明与阶段二审核报告"],
    ["third stage/", "验收与测试脚本、Flask 前端、数据库交付（dump + 恢复说明）、验收结果 JSON 与截图"],
    ["fourth stage/01-设计文档/", "课程报告（docx）与报告用 21 张插图"],
    ["fourth stage/02-汇报PPT/", "汇报 PPT（PPTX）与讲稿"],
    ["fourth stage/03-分析挖掘/", "5 个主题 21 条分析 SQL、结果 CSV/JSON、6 张统计图"],
    ["fourth stage/04-流程图与框图/", "用例图、总体流程图、系统框图、导入流程图、验收流程图、关键表关系图"],
    ["fourth stage/05-打包/", "提交说明与最终压缩包"],
    ["README.md、run.sh", "仓库导航与一键运行入口（建库、导入、测试、前端、分析）"],
]

AI_RECORDS = [
    ["第一阶段", "资料检索与字段语义梳理草稿、E-R 图与文档措辞检查、问题记录整理",
     "逐条对照数据手册与样例 XML；图与结论由组员复核后定稿（第一阶段/92-AI使用记录.md）"],
    ["第二阶段", "建表 SQL 与导入脚本草稿、异常处理与审计表结构建议",
     "在空库重建并核对行数与约束清单；所有变更写入《数据库设计变更说明》并复跑验收"],
    ["第三阶段", "测试用例补充、前端模板与错误处理建议、问题记录整理",
     "在一次性容器复现全部测试，逐条确认 *_result.json；FAIL/SKIP 一律视为未通过"],
    ["第四阶段", "分析 SQL 草稿、图表生成、报告与 PPT 排版辅助",
     "SQL 结果与库内现场查询对照，图表数据来自导出的 CSV/JSON，数字全部由脚本注入报告"],
]

PROBLEMS = [
    ["A（数据调研）", "专利数据服务试验系统无法访问，无法获取全量数据",
     "以官方样例与数据手册为唯一事实来源，并在第一阶段/90-问题记录-A.md 中声明数据边界"],
    ["A（概念设计）", "USPTO 批量 XML 不是合法 XML，直接解析报错",
     "按逻辑根做逐段容错解析；统计 17 个 XML 的逻辑根与记录数后写入数据字典"],
    ["A（概念设计）", "日期字段存在 YYYYMMDD 与 YYYYMM00 两种精度",
     "采用「解析列 + 原文列」并存，精度不足时解析列为 NULL，绝不伪造具体日期"],
    ["A（概念设计）", "3NF 审查发现分类号分量与最早优先权日为传递依赖",
     "拆出 classification 维表；最早优先权日改为由 priority_claim 派生，不落冗余列"],
    ["A（概念设计）", "教材到手后按教材定义重做 E-R 图与族建模",
     "重画六域图、纠正来源页码与 DOCDB 族建模，形成问题 11、12 两轮修正记录"],
    ["B（物理实现）", "country_office 的成员/组织等标志被统一填 N，制造了错误事实",
     "改为可空，未查证的一律为 NULL；变更记录见《数据库设计变更说明》"],
    ["B（物理实现）", "person ISA 子类的延迟触发器只校验新键",
     "同时校验旧键与新键，避免子类主键被移动后遗留没有子类的 person 记录"],
    ["B（物理实现）", "claim、claim_dependency、publication 缺少值域检查",
     "补充正数编号、禁止自引用、非负计数等 12 个业务检查约束"],
    ["B（物理实现）", "现有数据库只更新增量 SQL，缺少可复现的批次审计",
     "新增 stage2_meta 三表与 active_publication 视图，导入批次、源文件与软删除可追溯"],
    ["C（测试验收）", "Git 换行转换导致 17 个 XML 的 SHA256 与原快照不符",
     ".gitattributes 将 XML 设为 -text 保留原始 CRLF，新 clone 严格 SHA 校验"],
    ["C（测试验收）", "缺表、SKIP、FAIL 时脚本仍以退出码 0 结束，存在假通过风险",
     "严格校验 schema、表集合、约束名与行数，任何未通过一律非 0 退出（6 条故障注入验证）"],
    ["C（测试验收）", "SQL 报错被「无数据」掩盖，且错误语句污染同一事务",
     "只读冒烟使用 autocommit，写测试使用 SAVEPOINT，报错即失败并记录原因"],
    ["C（前端展示）", "详情页把 SQL 错误显示为「无」，并展示了软删除文献",
     "错误返回 HTTP 503 并写日志；详情改为读取 active_publication，权利要求跟随活动文献"],
    ["C（运行环境）", "psycopg2-binary 2.9.9 在 Python 3.14 无法安装；交付件缺恢复包",
     "升级到 2.9.11；补充 PG16 dump 并在独立库恢复比对 46 张表（fresh_acceptance.json）"],
    ["D（文档整合）", "报告模板只定义了五个一级标题的自动编号，二级标题会丢掉编号",
     "保留模板 numId=5 的一级编号，二三级标题采用 1.1 / 1.1.1 手动编号并写入正文"],
    ["D（文档整合）", "系统缺中文字体，图表中文显示为方框；Word 不能嵌入 SVG",
     "图表显式指定中文字体族；SVG 先栅格化为 PNG 再插入 Word"],
    ["D（分析挖掘）", "库内引用解析数为 0，无法做「被引热度」或技术演化分析",
     "把分析口径改为引用方结构（类型、出度、被引国别与年代），并在 4.6.3 与 4.7 声明限制"],
    ["D（分析挖掘）", "样例内年份与申请人高度集中，容易被误读为行业结论",
     "所有结论限定在官方样例范围内，逐条标注适用范围并写入 4.7 局限性"],
]

TITLE = "数据库实践课程报告"
TODAY = "2026 年 10 月 8 日"
H1_TITLES = ["报告摘要", "需求分析", "方案设计", "结果展示", "小组总结"]
# 表1 的数据集顺序（与 dataset_id 一致，供 4.6.5 引用 d0/d1/d2/d3/d4）
DATASET_ORDER = ["US_APP_PUB", "US_GRANT", "EP_FULLTEXT", "EP_DOCDB_ABS", "EP_LEGAL_STATUS"]
DATASET_CN = {"EP_LEGAL_STATUS": "欧洲专利法律状态数据"}
ROLE_TABLE = [
    ["学号", "姓名", "角色", "任务分工"],
    ["（请填写）", "（请填写）", "A 数据调研与概念设计",
     "需求分析、数据字典（43 表 345 字段）、六域 E-R 图、方案设计初稿"],
    ["（请填写）", "（请填写）", "B 表结构设计与导入",
     "43 表建表 SQL、审计迁移、导入脚本与批次入口、设计变更说明"],
    ["（请填写）", "（请填写）", "C 测试验证与前端",
     "测试与验收脚本、Flask 前端、数据库 dump 与全新容器复现"],
    ["（请填写）", "（请填写）", "D 文档整合与分析挖掘",
     "本报告、汇报 PPT、5 个主题 21 条分析 SQL 与 6 张统计图、流程图/框图、打包"],
]


# --------------------------------------------------------------------------- 读取证据
def load_table_rows():
    data = json.loads(TABLES_JSON.read_text(encoding="utf-8"))
    return {row["table"]: int(row["rows"]) for row in data}


def load_analysis():
    """把 analysis_results.json 展开成 {查询名: [行字典, ...]}，并返回查询总数。"""
    raw = json.loads(ANALYSIS_JSON.read_text(encoding="utf-8"))
    result, count = {}, 0
    for analysis in raw["analyses"]:
        for query in analysis["queries"]:
            count += 1
            columns = query["columns"]
            result[query["name"]] = [dict(zip(columns, values)) for values in query["rows"]]
    return result, count


def count_problem_rows(path: Path) -> int:
    """统计问题记录 Markdown 首个表格的数据行数（排除表头与分隔行）。

    供报告 5.1 节与汇报 PPT 引用「本阶段 N 条问题」，避免新增条目后数字不同步。
    """
    rows, header_seen = 0, False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if rows:
                break
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if not header_seen:
            header_seen = True
            continue
        rows += 1
    return rows


def load_tests():
    """从各 *_result.json 实时统计用例数与通过数（不手工填写数字）。"""
    rows, total = [], 0
    for script, result_file, scope in TESTS:
        data = json.loads((RESULT_DIR / result_file).read_text(encoding="utf-8"))
        cases = data.get("cases", [])
        passed = sum(1 for case in cases if case.get("status") == "PASS")
        rows.append([script, len(cases), passed, scope, result_file])
        total += len(cases)
    return rows, total


def dump_fingerprint():
    """交付 dump 的 SHA256（若文件存在），用于第 4.5 节的证据描述。"""
    import hashlib

    if not DUMP.exists():
        return "（未找到交付 dump，请先执行 third stage/06-运行管理/verify_fresh.py）"
    digest = hashlib.sha256(DUMP.read_bytes()).hexdigest()
    return f"{digest}（{DUMP.stat().st_size / 1024 / 1024:.1f} MB）"


def build_ctx():
    rows_by_table = load_table_rows()
    analysis, query_count = load_analysis()
    tests, test_total = load_tests()

    row_groups, total_rows, seen = [], 0, set()
    for name, tables, note in DOMAINS:
        count, domain_rows, parts = 0, 0, []
        for table in tables:
            if table in seen:
                raise SystemExit(f"DOMAINS 中重复归类的表：{table}")
            if table not in rows_by_table:
                raise SystemExit(f"逐表行数.json 中缺少表：{table}")
            seen.add(table)
            count += 1
            domain_rows += rows_by_table[table]
            parts.append((table, rows_by_table[table]))
        total_rows += domain_rows
        parts.sort(key=lambda item: (-item[1], item[0]))
        top = "、".join(f"{t} {r} 行" for t, r in parts[:3])
        row_groups.append([name, count, domain_rows, top + " 等", note])
    missing = sorted(set(rows_by_table) - seen)
    if missing:
        raise SystemExit(f"以下业务表未在 DOMAINS 中归类：{missing}")

    datasets = []
    for code in DATASET_ORDER:
        row = next(r for r in analysis["dataset_split"] if r["数据集"] == code)
        datasets.append({"数据集": code, "中文名": DATASET_CN.get(code, row["中文名"]),
                         "文献数": int(row["文献数"]), "申请数": int(row["申请数"])})

    applicant_type = analysis["applicant_type"]
    org = next(int(r["人数"]) for r in applicant_type if r["类型"] == "机构")
    natural = next(int(r["人数"]) for r in applicant_type if r["类型"] == "自然人")
    covered = next(int(r["专利数"]) for r in analysis["role_summary"] if r["角色"] == "申请人")

    st = dict(STATS)
    st["rows"] = total_rows
    return {
        "st": st,
        "an": analysis,
        "extra": {"org_people": org, "nat_people": natural, "covered_patents": covered},
        "datasets": datasets,
        "row_groups": row_groups,
        "tests": tests,
        "test_total": test_total,
        "query_count": query_count,
        "env": ENV,
        "problems": PROBLEMS,
        "deliver": DELIVER,
        "ai": AI_RECORDS,
        "dump": dump_fingerprint(),
        "problem_rows": count_problem_rows(PROBLEM_MD),
    }


# --------------------------------------------------------------------------- 渲染
def render_blocks(doc, blocks):
    """把内容块渲染到文档末尾，返回按顺序排列的 XML 元素列表（随后统一搬位）。"""
    created = []
    for block in blocks:
        kind = block[0]
        if kind == "h2":
            created.append(rl.new_heading(doc, block[1], 2)._p)
        elif kind == "h3":
            created.append(rl.new_heading(doc, block[1], 3)._p)
        elif kind == "p":
            created.append(rl.new_para(doc, block[1])._p)
        elif kind == "bullets":
            for item in block[1]:
                created.append(rl.new_bullet(doc, item)._p)
        elif kind == "code":
            created.append(rl.new_code(doc, block[1])._p)
        elif kind == "img":
            path = FIGDIR / block[1]
            if not path.exists():
                raise SystemExit(f"缺少插图：{path}（请先运行 make_figures.py）")
            created.extend(rl.new_picture(doc, path, block[2], block[3]))
        elif kind == "table":
            caption, header, rows, widths = block[1], block[2], block[3], block[4]
            center_cols = block[5] if len(block) > 5 else None
            created.append(rl.new_caption(doc, caption, above=True)._p)
            created.append(rl.new_table(doc, header, rows, widths, center_cols=center_cols)._tbl)
        else:
            raise SystemExit(f"未知的内容块类型：{kind}")
    return created


def is_h1(paragraph) -> bool:
    """模板的一级标题：Normal 样式 + numPr(numId=5, ilvl=0)。"""
    pPr = paragraph._p.pPr
    if pPr is None or pPr.numPr is None or pPr.numPr.numId is None:
        return False
    if pPr.numPr.numId.val != 5:
        return False
    ilvl = pPr.numPr.ilvl
    return ilvl is None or ilvl.val == 0


def set_paragraph_text(paragraph, text):
    """复用模板既有段落：改写第一个 run 的文字并删除其余 run，保留原格式。"""
    runs = paragraph.runs
    if not runs:
        paragraph.add_run(text)
        return paragraph
    runs[0].text = text
    for run in runs[1:]:
        run._r.getparent().remove(run._r)
    return paragraph


def fill_cover(doc):
    """填写封面：小组序号 / 小组题目 / 日期（学号姓名保留占位由组员补全）。"""
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text.startswith("小组序号"):
            set_paragraph_text(paragraph, "小组序号              （请填写）")
        elif text.startswith("小组题目"):
            set_paragraph_text(paragraph, "小组题目   题目 5：专利数据关系数据库设计与实践")
        elif "年" in text and "月" in text and "日" in text and len(text) <= 12:
            set_paragraph_text(paragraph, TODAY)


# --------------------------------------------------------------------------- 自检
def self_check(path, ctx, blocks_by_h1, cover_images=0):
    from docx import Document

    doc = Document(str(path))
    problems = []

    titles = [p.text.strip() for p in doc.paragraphs if is_h1(p)]
    if titles != H1_TITLES:
        problems.append(f"一级标题不一致：{titles}")

    texts = [p.text for p in doc.paragraphs]
    joined = "\n".join(texts)
    for marker in ["【", "详细介绍需要解决的实际工程问题", "提出自己的解决方案，以用例图"]:
        if marker in joined:
            problems.append(f"仍残留模板占位文字：{marker}")

    # 图题 / 表题 / 插图数 / 表格数都由内容块推导，避免手工维护期望值
    captions, table_captions, figures = [], [], 0
    for blocks in blocks_by_h1.values():
        for block in blocks:
            if block[0] == "img":
                captions.append(block[2])
                figures += 1
            elif block[0] == "table":
                table_captions.append(block[1])
    for caption in captions:
        if caption not in joined:
            problems.append(f"缺少图题：{caption}")
    for caption in table_captions:
        if caption not in joined:
            problems.append(f"缺少表题：{caption}")

    images = len(doc.inline_shapes)
    tables = len(doc.tables)
    if images != figures + cover_images:
        problems.append(f"插图数量为 {images}，期望 {figures + cover_images}（含封面校徽 {cover_images} 张）")
    if tables != len(table_captions) + 1:
        problems.append(f"表格数量为 {tables}，期望 {len(table_captions) + 1}（含小组分工表）")

    print(f"[自检] 段落 {len(doc.paragraphs)} 个、表格 {tables} 个、插图 {images} 张、"
          f"图题 {len(captions)} 条、表题 {len(table_captions)} 条")
    print(f"[自检] 一级标题：{' / '.join(titles)}")
    print(f"[自检] 业务表 {ctx['st']['tables']} 张、字段 {ctx['st']['fields']} 个、"
          f"数据 {ctx['st']['rows']} 行、测试用例 {ctx['test_total']} 条、"
          f"分析 SQL {ctx['query_count']} 条")
    if problems:
        print("[自检] 发现问题：" + "；".join(problems))
        return False
    print("[自检] 全部通过：章节、图表、数字与模板格式一致。")
    return True


def main() -> int:
    for path in (TABLES_JSON, ANALYSIS_JSON, FRESH_JSON):
        if not path.exists():
            raise SystemExit(f"缺少证据文件：{path}")

    ctx = build_ctx()
    blocks = rc.build_blocks(ctx)
    doc = rl.open_template()
    cover_images = len(doc.inline_shapes)  # 模板封面自带的校徽图片

    h1 = [p for p in doc.paragraphs if is_h1(p)]
    if [p.text.strip() for p in h1] != H1_TITLES:
        raise SystemExit("模板结构与预期不符，请检查 报告模板.docx")

    # 先记录模板中需要删除的示例文字（第一个一级标题之后、且不是一级标题本身）
    first = h1[0]._p
    passed_first = False
    placeholders = []
    for paragraph in doc.paragraphs:
        if paragraph._p is first:
            passed_first = True
            continue
        if passed_first and not is_h1(paragraph):
            placeholders.append(paragraph._p)

    fill_cover(doc)
    duty_table = doc.tables[0] if doc.tables else None
    if duty_table is not None:
        rl.fill_table(duty_table, ROLE_TABLE)

    # 逐章插入正文内容，并搬移到对应一级标题之后
    for paragraph, title in zip(h1, H1_TITLES):
        created = render_blocks(doc, blocks[title])
        last = rl.move_after(paragraph._p, *created)
        if title == "报告摘要" and duty_table is not None:
            rl.move_after(last, duty_table._tbl)

    for element in placeholders:
        rl.drop(element)

    doc.save(str(OUT))
    ok = self_check(OUT, ctx, blocks, cover_images=cover_images)
    print(f"[输出] {OUT.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


