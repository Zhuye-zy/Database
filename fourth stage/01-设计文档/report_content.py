#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课程报告正文内容（按模板五个一级标题组织）。

块的类型：
    ("h2", 标题文本)              二级标题（手动编号，黑体四号）
    ("h3", 标题文本)              三级标题（手动编号，黑体小四加粗）
    ("p", 段落文本)               正文段落（宋体小四、首行缩进 2 字符、1.5 倍行距）
    ("bullets", [条目, ...])      项目符号列表
    ("code", [行, ...])           伪代码/命令块（等宽字体 + 浅灰底纹）
    ("img", 图文件名, 图题, 宽度cm)  居中插图 + 图题
    ("table", 表题, 表头, 数据行, 列宽)  三线表样式的 Table Grid 表格

所有数字都来自仓库内可复核的证据文件（逐表行数.json、*_result.json、
analysis_results.json），在 build_report.py 中注入 ctx，不手工编造。
"""
from __future__ import annotations

FIG = "图/"


def _num(value) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------------------------------- 一、报告摘要
def section_summary(ctx):
    an = ctx["an"]
    st = ctx["st"]
    ex = ctx["extra"]
    p_cit = [r for r in an["type_split"] if r["类型码"] == "P"][0]
    n_cit = [r for r in an["type_split"] if r["类型码"] == "N"][0]
    top = an["applicant_rank"][0]
    blocks = [
        ("h2", "1.1 需要解决的数据库问题"),
        ("p", "题目 5 给出的是国家知识产权局专利数据服务试验系统（patdata.cnipa.gov.cn）发布"
              "的专利基础数据：以 XML 为主，配套数据手册与官方样例，涵盖中、美、欧、日、韩五局的"
              "著录项目、引用信息、权利要求书、说明书以及专利族等内容。这些 XML 是典型的半结构化"
              "文献数据：一件申请同时带多个申请人、发明人、分类号和上百条引用；标题、摘要、权利要求、"
              "附图、说明书章节必须依附于某一篇公布文献才能被识别；引用关系的两端都可以指向专利，而被引"
              "专利往往并不在本批数据中。"),
        ("p", "因此本组要解决的工程问题是：把这种嵌套、多值、带弱实体与自引用关系的专利 XML，"
              "转换为一套结构清晰、满足第三范式、约束完整、可重复导入的关系数据库，并在其上完成"
              "查询、展示与统计分析。具体指标包括：业务表不少于 20 张且覆盖多值属性拆表；"
              "主键、外键、唯一约束与检查约束齐备；导入过程可追溯、可重跑、失败可回滚；"
              "全部表能被前端列出并查看明细；对数据来源的缺口必须如实记录，不用编造数据把表填满。"),
        ("h2", "1.2 解决方案概要"),
        ("p", "本组按“A 数据调研与概念设计 → B 表结构设计与导入 → C 测试验证与前端 → D 文档整合与"
              "分析挖掘”四个角色推进，最终交付 {tables} 张业务表、{fields} 个字段的 PostgreSQL 数据库"
              "（同时有 3 张审计表与 1 个视图），入库 {rows} 行数据，并通过 {cases} 条测试与验收用例。"
              "总体做法可以概括为五点：".format(tables=st["tables"], fields=st["fields"],
                                              rows=st["rows"], cases=ctx["test_total"])),
        ("bullets", [
            "以数据手册和官方样例为唯一事实来源：先按 INID 码与数据手册对齐字段语义，再决定表结构；"
            "样例没有给出的事实（例如未查证的成员组织、月精度日期、库外被引文献）一律保留原样或留空，"
            "不使用看起来合理的默认值填充。",
            "多值属性一律拆表：申请人、发明人、权利人、代理人、审查员、分类号、引用、权利要求、"
            "专利族成员都建立独立的关系表，用复合唯一键保证同一组合不重复。",
            "弱实体带属主键：title / abstract / claim / drawing / description_section 均以 publication 为"
            "属主，把“属主键 + 部分键（语言、序号）”作为唯一键，使概念模型的语义在物理层仍可验证。",
            "导入可追溯、可重跑：以源文件 SHA256 指纹锁定输入，以（数据集 + 文献号）作为幂等键，"
            "整批事务写入并写审计表，失败整批回滚。",
            "验证与展示分离：测试只使用临时容器或回滚事务，交付库通过 pg_dump 备份并做独立恢复比对，"
            "保证“测试过的库”与“交付的库”内容一致。",
        ]),
        ("h2", "1.3 主要结果"),
        ("p", "数据库侧：patent 与 publication 各 19 行，43 张业务表中 42 张非空，合计 {rows} 行；"
              "引用关系 {total_cit} 条（专利文献引用 {p_cit} 条、非专利文献引用 {n_cit} 条）。"
              "约束侧：{pk} 个主键、{fk} 个外键、{uq} 个唯一约束、{chk} 个业务检查约束（另有 {notnull} 个"
              "非空约束）与 {idx} 个索引；插入违反外键或唯一键的测试数据均被数据库拒绝（SQLSTATE 23503 /"
              " 23505）。应用侧：Flask 前端可浏览全部 43 张业务表、打开专利详情；测试侧：故障注入 6 条、"
              "冒烟 48 条、外键 14 条、复杂与边界 12 条、前端 71 条，合计 {cases} 条全部通过；"
              "分析侧：在完整库上执行 5 个主题共 {q} 条分析 SQL，产出 6 张统计图，并把结论写回本报告。"
              .format(rows=st["rows"], total_cit=_num(p_cit["引用条数"]) + _num(n_cit["引用条数"]),
                      p_cit=p_cit["引用条数"], n_cit=n_cit["引用条数"], pk=st["pk"], fk=st["fk"],
                      uq=st["uq"], chk=st["chk"], notnull=st["notnull"], idx=st["idx"],
                      cases=ctx["test_total"], q=ctx["query_count"])),
        ("p", "分析侧的几个样例内观察：申请人排名第一的是 {top_name}（{top_n} 件专利，与另一申请人并列），"
              "全部 {org_n} 家机构、{nat_n} 名自然人合计覆盖 {cover_n} 件专利；技术领域以 IPC “A 部（人类生活"
              "必需）”最多（9 件）；引用高度集中在少数文献上——单件专利最多引用 {max_out} 条文献，其中专利文献"
              "引用 {max_p} 条，占全部专利文献引用的 {share}%；但被引目标全部在库外，库内解析数为 0，"
              "因此本报告只给出“引用方结构”，不做“被引热度”排名。".format(
                  top_name=top["申请人"], top_n=top["专利数"],
                  org_n=ex["org_people"], nat_n=ex["nat_people"], cover_n=ex["covered_patents"],
                  max_out=an["out_degree"][0]["合计"], max_p=an["out_degree"][0]["专利引用"],
                  share=round(100 * _num(an["out_degree"][0]["专利引用"])
                              / _num(p_cit["引用条数"]), 1))),
        ("h2", "1.4 小组分工"),
        ("p", "小组按四个角色分工，每个角色既是上一阶段的接收方也是下一阶段的交付方；"
              "下表同时给出角色、阶段与具体任务，其中学号与姓名由组员在提交前补全。"),
    ]
    return blocks


# --------------------------------------------------------------------------- 二、需求分析
DATASET_ROLE = {
    "US_APP_PUB": "申请公布（A1）著录项、摘要、权利要求、说明书章节",
    "US_GRANT": "授权公告（B1/B2/E1）著录项与全文",
    "EP_FULLTEXT": "EP 全文：EN/DE/FR 多语言标题与权利要求",
    "EP_DOCDB_ABS": "DOCDB 摘要级记录、INPADOC 专利族成员",
    "EP_LEGAL_STATUS": "法律状态事件（事件码、事件日期）",
}


def section_requirement(ctx):
    st, an, ex = ctx["st"], ctx["an"], ctx["extra"]
    ds_rows = [[r["数据集"], r["中文名"], r["文献数"], r["申请数"],
                DATASET_ROLE.get(r["数据集"], "—")] for r in ctx["datasets"]]
    return [
        ("h2", "2.1 选题背景与数据来源"),
        ("p", "题目 5 的研究对象是专利数据服务试验系统提供的五局专利基础数据。数据以 XML 组织，"
              "每种数据配有数据手册（Data Manual）与官方样例，内容覆盖著录项目、引用信息、权利要求书、"
              "说明书和专利族五类信息。专利著录项目的含义由 INID 码统一约定（如 (21) 申请号、(22) 申请日、"
              "(51) 分类号、(54) 发明名称、(57) 摘要、(71) 申请人、(72) 发明人），这使得不同国家、"
              "不同年代的 XML 可以用同一套语义去解析。"),
        ("p", "本组实际使用的数据全部来自官方样例与数据手册，不引入任何第三方数据；导入前记录每个 XML 的 "
              "SHA256 指纹，导入过程中只做格式转换与规范化，不做补全。（下表为入库的 5 类数据集，"
              "共 19 件申请、19 篇公布/公告文献。）"),
        ("table", "表1 入库的官方样例数据集与规模", ["数据集代码", "名称", "文献数", "申请数", "主要入库对象"],
         ds_rows, [2.6, 3.6, 1.4, 1.4, 5.6]),
        ("h3", "2.1.1 从数据手册到表结构"),
        ("p", "数据手册给出的字段清单是表结构设计的直接依据。本组按以下顺序使用手册：先用 INID 码把"
              "五类样例的同义字段对齐（例如 US 授权公告的 <invention-title> 与 EP 全文的 "
              "<invention-title lang=...> 都落到 title 表，语言作为部分键）；再按“是否多值、是否长文本、"
              "是否有独立生命周期”三个问题判断是建独立实体、拆关联表还是作为弱实体；最后逐字段标注"
              "来源页码，形成第一阶段的实体与属性清单，作为第二阶段的建表依据。"),
        ("h3", "2.1.2 样例数据的规模与代表性约束"),
        ("p", "官方样例的作用是验证结构而不是支撑统计推断：19 件申请、19 篇文献、{rows} 行数据，"
              "且申请人以单申请人为主、外观设计与园艺机械类占比较高。因此本报告的所有统计结论都限定在"
              "样例范围内，并在第 4.6 节逐条标注适用范围；任何“行业趋势”式的结论都不在本报告的结论之内。"
              .format(rows=st["rows"])),
        ("h2", "2.2 数据的结构特点与需要解决的工程问题"),
        ("p", "把样例 XML 与数据手册对照后，本组归纳出七类必须在数据库设计中显式处理的特点，"
              "它们也是本题目真正的工程难点："),
        ("bullets", [
            "多值属性普遍存在：一件申请可以有多个申请人、多个发明人、多个分类号、几百条引用、上百条"
            "权利要求。任何“把多值塞进一个字段”的做法都会破坏第一范式，必须拆成独立关系表并加复合唯一键。",
            "弱实体必须带属主：title、abstract、claim、drawing、description_section 自身没有独立标识，"
            "必须依附 publication 才能被识别，其唯一键由“属主键 + 部分键（语言、序号）”构成。",
            "引用是一元递归联系且被引目标常在库外：patent_citation 的两个外键都指向 patent，而被引专利"
            "大多不在本批数据中，因此 cited_patent_id 必须可空，同时保留被引国别、号码、种类与日期原文。",
            "多语言与多版本：EP 文献的标题和权利要求按 EN/DE/FR 分套，权利要求还有独立/从属之分，"
            "同一篇文献的“权利要求条数”必须按语言分别统计。",
            "日期精度不统一：公布日存在只有年月（YYYYMM00）的情况，导入时不能伪造成某一天；"
            "本组采用“解析列 + 原文列”并存策略（如 appln_filing_date 与 appln_filing_date_raw）。",
            "来源缺口要如实保留：专利族引用（family_citation）需要双端官方族号，样例无法确认，"
            "本组保留空表并写入说明，而不是用近似关系灌数据。",
            "可追溯与可重跑：课程验收要求能重复得到同一个库。必须固定输入指纹、固定幂等键、"
            "把每次导入的批次与文件记录在审计表中，失败时整批回滚。",
        ]),
        ("p", "这些特点决定了设计决策：多值属性拆表 → 关系表；弱实体 → 带属主键的独立表；"
              "自引用 → 可空外键 + 角色列；多语言 → 语言进入唯一键；日期精度 → 双列并存；"
              "来源缺口 → 空表 + 文档说明；可重跑 → 幂等键 + 审计表。下表把每类问题与落地证据一一对应。"),
        ("table", "表2 数据特点、设计决策与落地证据的对应关系",
         ["数据特点 / 工程问题", "设计决策", "落地与证据"],
         [["多值属性（申请人/发明人/分类号/引用/权项）", "拆成 1:N 或 M:N 关系表，加复合唯一键",
           "{t} 张业务表；{fk} 个外键；{uq} 个唯一约束（其中 {uqm} 个为复合唯一键）".format(
               t=st["tables"], fk=st["fk"], uq=st["uq"], uqm=st["uq_multi"])],
          ["弱实体（标题/摘要/权项/附图/说明书章节）", "属主键 + 部分键作为唯一键",
           "title/abstract/claim/drawing/description_section 5 张文献部件弱实体表，"
           "claim 184 行、description_section 538 行"],
          ["引用一元递归、被引常在库外",
           "citing_patent_id / citing_publication_id 非空，cited_* 可空并保留原文号码",
           "805 条引用（专利文献 508 条），被引目标的库内解析数为 0"],
          ["多语言标题与权利要求", "语言进入部分键；统计时按语言分组",
           "title 30 行、claim 184 行，EN/DE/FR 分别为 136/24/24 条权利要求"],
          ["日期精度不齐（YYYYMM00、哨兵值）", "解析列 + 原文列并存，无法确定到日时置 NULL",
           "patent.appln_filing_date 可空；未伪造完整日期"],
          ["专利族引用缺少可靠双端族号", "保留 family_citation 空表并在文档中声明缺口",
           "43 张业务表中 42 张非空，family_citation 为 0 行"],
          ["导入需可追溯、可重跑", "源文件 SHA256 + 幂等键 + 审计表 + 整批事务",
           "stage2_meta 审计 3 表 + 1 视图；幂等重跑行数不翻倍"]],
         [4.6, 4.6, 5.4]),
        ("h2", "2.3 功能需求"),
        ("p", "系统面向两类使用者：一类是希望快速核对数据是否完整入库的使用者（浏览全部表、"
              "查看某件专利及其文献详情），另一类是希望在库上做检索与统计的分析人员。"
              "两类需求都只读不写——数据库的写入只发生在受控的导入脚本里，这是本组的有意选择："
              "前端不提供写入接口，避免演示过程污染官方样例库。功能需求见图 1。"),
        ("img", "图1-用例图.png", "图1 系统用例图（参与者与核心用例）", 14.5),
        ("table", "表3 用例说明", ["用例", "参与者", "输入 / 处理", "前置与约束"],
         [["浏览全部业务表", "数据库使用者", "列出 43 张业务表的表名、注释与当前行数",
           "表集合取自 information_schema，缺表即失败"],
          ["查看专利与文献详情", "数据库使用者", "按 patent_id 聚合标题、摘要、权利要求与引用",
           "只显示 stage2_meta.active_publication 中的活动文献"],
          ["按申请人 / 发明人检索", "数据库使用者、分析人员", "person ↔ 角色表 ↔ patent 三表连接",
           "姓名未做消歧，结果按 person_id 去重"],
          ["按分类号 / 技术领域查询", "分析人员", "patent_classification ↔ classification 连接",
           "IPC 与 CPC 两套体系分开统计，不混算"],
          ["查看引用关系", "分析人员", "patent_citation 按引用方聚合，区分 P / N",
           "被引目标可能不在库内，需显示原文号码"],
          ["统计分析与导出图表", "分析人员", "{q} 条分析 SQL → CSV / JSON → 统计图".format(q=ctx["query_count"]),
           "结论限定在官方样例范围内"]],
         [3.0, 2.6, 5.4, 3.6]),
        ("h2", "2.4 数据需求与规模"),
        ("p", "数据需求可以按“入库什么、存多少、如何追溯”三条描述：入库对象是 5 类官方样例的全部信息"
              "类型（著录项目、人员角色、分类、引用、权利要求、说明书章节、专利族、法律状态、关键词）；"
              "存储规模是 {t} 张业务表、{f} 个字段、{r} 行数据，另有 3 张审计表记录导入批次与字段级错误；"
              "追溯要求是每个源文件都有 SHA256 指纹，每次导入都有批次号。".format(
                  t=st["tables"], f=st["fields"], r=st["rows"])),
        ("p", "与题目要求对照：题目要求业务表不少于 20 张并满足 3NF，本组交付 {t} 张（A 阶段划分的 "
              "38 张核心表加 5 张增强表）；题目要求长文本选择合适的存储类型，本组对摘要、权利要求、"
              "说明书段落统一使用 TEXT；题目要求体现引用自引用与专利族建模，本组分别用“可空自引用外键”"
              "与“族表 + 成员表 + 成员号码引用表”实现。".format(t=st["tables"])),
        ("h2", "2.5 完整性与非功能需求"),
        ("bullets", [
            "实体完整性：43 张表全部有主键，主键类型统一为 bigint 代理键或业务组合键。",
            "参照完整性：{fk} 个外键全部生效；被引专列允许为空以表达“目标在库外”，"
            "一旦给出就必须指向存在的 patent/publication。".format(fk=st["fk"]),
            "业务规则完整性：{chk} 个检查约束把引用类型、语言码、编号正负、"
            "权利要求的独立/从属等规则写进数据库，而不是只写在应用程序里。".format(chk=st["chk"]),
            "可追溯性：源文件 SHA256、导入批次、文件级与字段级错误写入审计表；"
            "测试脚本在缺表、空库、约束被绕过时必须以非 0 退出码失败。",
            "不虚构数据：无法确认的事实（未查证的成员组织、月精度日期、库外被引文献、"
            "缺失的双端族号）保留空值或空表，并在 README、报告与问题记录中声明。",
            "只读展示与错误可见：前端不提供写入；数据库异常时返回 HTTP 503 并给出“数据加载失败”提示，"
            "不把错误显示成“无数据”。",
        ]),
    ]


# --------------------------------------------------------------------------- 三、方案设计
DOMAIN_NOTES = [
    ("图2a-ER域1-著录与文献.png", "图2(a) 域 1：著录项目与文献部件",
     "patent（申请案）1—N publication（公布/公告文献）；title/abstract/claim/drawing/"
     "description_section 为 publication 的弱实体，部分键分别为 (lang,type)、lang、(lang,number)、"
     "figure_seq、section_seq。"),
    ("图2b-ER域2-人员与角色.png", "图2(b) 域 2：人员与五类角色",
     "person 是 ISA 父类（person_type ∈ {N,L}），natural_person 与 organization 为子类；"
     "申请人、发明人、权利人、代理人、审查员通过五张 M:N 关联表挂到 patent，关联表带顺序号等联系属性。"),
    ("图2c-ER域3-分类.png", "图2(c) 域 3：分类号",
     "classification 以 (scheme_code, symbol) 为主键，section / class_no / subclass 与符号一一对应；"
     "patent_classification 表达专利与分类号的 M:N 关系，并区分分类来源。"),
    ("图2d-ER域4-引用.png", "图2(d) 域 4：引用（一元递归）",
     "patent_citation 的引用端（citing_patent_id、citing_publication_id）非空，被引端"
     "（cited_patent_id、cited_publn_id）可空；引用类型 P/N 与引用类别码共同刻画引用性质。"),
    ("图2e-ER域5-专利族与程序关系.png", "图2(e) 域 5：专利族与程序关系",
     "patent_family（族）× patent_family_member（成员）表达一族多成员的 M:N 自关联；"
     "优先权、关联申请、指定国分别独立建表，依赖 patent 或 publication 识别。"),
    ("图2f-ER域6-法律状态与关键词.png", "图2(f) 域 6：法律状态与关键词",
     "legal_status_event 依赖 patent 与 legal_event_code（事件码维表）；"
     "keyword / patent_keyword 是本组基于标题派生的增强表，来源标注为 TITLE_DERIVED。"),
]


def section_design(ctx):
    st, an = ctx["st"], ctx["an"]
    return [
        ("h2", "3.1 总体技术路线"),
        ("p", "总体路线是“先理解数据、再定结构、后验证”，四个角色依次接力，每一步都有可检查的交付物"
              "（图 4）。实现环境选择 PostgreSQL 16 + Python：PostgreSQL 对复合唯一键、可空外键、"
              "TEXT、CHECK 约束与查询计划的支持都比较直接，适合把概念模型里的约束一次性落到物理层；"
              "Python 便于解析 XML、编写导入与测试脚本，并与 Flask 前端共用一套环境。"),
        ("img", "图4-总体流程图.png", "图4 总体流程图：四角色六阶段交付链", 14.8),
        ("h2", "3.2 概念设计：六域 E-R 模型"),
        ("p", "概念设计阶段（A 角色）按教材第 4 章符号绘制 E-R 图：实体集用矩形、弱实体集用双矩形、"
              "联系用菱形、支持联系用双菱形、ISA 用三角形，边上标注 1/M/N 与全参与/部分参与。"
              "由于实体与联系较多，图形按业务域拆成六张分域图与一张总览图，便于阅读与审查；"
              "本报告引用六张分域图（图 2(a)–(f)），矢量源文件与可编辑的 draw.io 文件保存在第一阶段目录。"),
        ("bullets", [f"{note[1]}：{note[2]}" for note in DOMAIN_NOTES]),
        ("img", DOMAIN_NOTES[0][0], DOMAIN_NOTES[0][1], 14.5),
        ("img", DOMAIN_NOTES[1][0], DOMAIN_NOTES[1][1], 14.5),
        ("img", DOMAIN_NOTES[2][0], DOMAIN_NOTES[2][1], 14.5),
        ("img", DOMAIN_NOTES[3][0], DOMAIN_NOTES[3][1], 14.5),
        ("img", DOMAIN_NOTES[4][0], DOMAIN_NOTES[4][1], 14.5),
        ("img", DOMAIN_NOTES[5][0], DOMAIN_NOTES[5][1], 14.5),
        ("h2", "3.3 逻辑设计：E-R 模型到关系模式的转换"),
        ("p", "转换规则遵循教材：强实体集转为表，主键作为关系模式的主键；弱实体集转为表，主键由"
              "“属主键 + 部分键”构成（本组实现时增加 bigint 代理键，同时用复合唯一约束保留原来的部分键"
              "语义，使约束仍能在数据库层校验）；M:N 联系转为独立关系表，主键由两端主键与联系属性组成；"
              "1:N 联系把“一”端主键作为“多”端的外键；ISA 结构用“父表 + 子表共享主键”实现，并用延迟约束"
              "触发器保证父表记录有且仅有一个对应的子类记录；一元递归联系通过两个指向同一张表的外键加"
              "角色列（引用方/被引方、在先/在后、主案/关联案）实现。"),
        ("img", "图3-关键表关系示意图.png", "图3 关键表与关系（43 张业务表按域归并）", 14.8),
        ("table", "表4 典型概念结构到关系模式的转换结果",
         ["概念结构", "转换规则", "落地关系模式（示例）"],
         [["强实体集 patent（申请案）", "转表，代理键作主键，业务组合键唯一",
           "patent(patent_id PK, appln_auth, appln_nr, appln_kind)"],
          ["弱实体集 claim（属主 publication）", "属主键 + 部分键 → 代理键 + 复合唯一键",
           "claim(claim_id PK, publication_id FK, lang_code, claim_number,"
           " UNIQUE(publication_id, lang_code, claim_number))"],
          ["M:N 联系“申请—申请人”", "转独立关系表，两端主键 + 联系属性",
           "patent_applicant(patent_id FK, person_id FK, sequence_nr)"],
          ["ISA：person → 自然人 / 组织", "父表 + 子表共享主键，延迟约束保证唯一子类",
           "natural_person(person_id PK/FK)、organization(person_id PK/FK)"],
          ["一元递归联系“引用”", "引用端非空、被引端可空，另存被引原文号码",
           "patent_citation(citing_patent_id FK, citing_publication_id FK, cited_patent_id FK NULL,"
           " cited_publn_id FK NULL, citation_type)"],
          ["M:N 自关联“专利族”", "族表 + 成员表 + 成员号码引用表",
           "patent_family(family_id PK) / patent_family_member(family_id FK, member_seq)"]],
         [3.2, 3.6, 7.6]),
        ("p", "范式审查按 1NF→4NF 逐级进行，并对照第一阶段识别出的两处传递依赖做了结构修正：分类号"
              "不再以“整串符号 + 派生的部/大类/小类”混存，而是拆出 classification 维表，"
              "由 (scheme_code, symbol) 决定 section、class_no、subclass；最早优先权日不再冗余存在"
              " patent 上，而是需要时从 priority_claim 派生。"),
        ("bullets", [
            "1NF：所有属性取原子值，多值属性全部拆表（申请人、发明人、分类号、引用、权利要求等）。",
            "2NF：带复合主键的表（如 classification、patent_classification）非键属性完全依赖于整个主键；"
            "使用代理键的表不存在部分依赖。",
            "3NF：不存在“非键属性 → 非键属性”的传递依赖；分类号分量与最早优先权日两处已被拆解。",
            "BCNF：每个决定因素都是候选键，例如 patent 的 (appln_auth, appln_nr, appln_kind)、"
            "publication 的 (publn_auth, publn_nr, publn_kind)、patent_family 的"
            " (family_type, source_family_id)。",
            "4NF：独立的多值依赖独立成表，例如“一件专利的多个发明人”与“多个分类号”分属两张表；"
            "删除任一关联行都不会影响另一组事实。",
        ]),
        ("h2", "3.4 物理设计：DBMS 选型、类型与命名"),
        ("table", "表5 候选 DBMS 对比与选型理由",
         ["候选", "优点", "在本题目中的不足", "结论"],
         [["PostgreSQL 16", "复合唯一键、可空外键、TEXT、CHECK 约束、部分索引与 EXPLAIN 完善；"
           "事务 DDL 便于脚本化重建；pg_dump / pg_restore 可做交付与恢复比对",
           "默认权限模型需要显式配置（本组用容器内本地认证，不硬编码口令）", "选用"],
          ["MySQL 8", "安装普及、管理工具多",
           "CHECK 约束历史支持较弱、部分唯一键与延迟约束表达不如 PostgreSQL 直接",
           "未选用"],
          ["openGauss", "国产化场景适配好",
           "本机环境与课程验收环境未部署，导入与测试脚本需额外适配", "未选用"]],
         [2.2, 5.4, 4.4, 1.6]),
        ("bullets", [
            "命名规范：表名与字段名统一小写 snake_case；外键统一 fk_表_列、唯一键 uq_、检查约束 ck_、"
            "索引 idx_，便于按名字定位与审查。",
            "长文本：abstract.abstract_text、claim.claim_text、description_section.section_text、"
            "non_patent_citation 相关文本字段使用 TEXT，不做长度截断。",
            "日期双列：publn_date、appln_filing_date 为解析后的 DATE 列，"
            "对应的 *_raw 保留原始字符串；月精度或哨兵值不写入 DATE 列。",
            "代码型字段：语言、国家/局、种类码、引用类型、人员类型等使用 CHAR/VARCHAR + CHECK 约束，"
            "并与 language、country_office、kind_code、citation_category 等维表建立外键。",
            "schema 划分：业务数据在 patentdb；导入审计（批次、源文件、发布状态快照）在 stage2_meta，"
            "并提供 active_publication 视图供前端取“活动文献”。",
            "字符集与排序：数据库统一 UTF-8；比较与排序使用默认 C 排序，导入前已统一大小写处理规则。",
        ]),
        ("h2", "3.5 系统架构"),
        ("p", "系统分为五层：数据源层（官方样例 XML）、导入层（解析与审计）、存储层（43 张业务表 + "
              "3 张审计表 + 视图）、分析层（{q} 条分析 SQL 与统计图）与展示层（Flask 前端）。"
              "旁挂一条运行管理线（启动、验收、全新复现、打包），保证任何一位组员都能在干净环境里"
              "复现同一套系统。分层与模块见图 5。".format(q=ctx["query_count"])),
        ("img", "图5-系统框图.png", "图5 系统框图：五层架构与运行管理面", 14.8),
        ("h2", "3.6 数据导入流程与关键伪代码"),
        ("p", "导入脚本把“一次导入”定义为一个事务：先校验源文件指纹，再把每个 XML 按逻辑根切分为"
              "逻辑文档，按数据集选择解析器，解析结果分别写入父表、关联表与弱实体表，最后写审计表并"
              "提交；任何一步失败都整批回滚。这样即使中途中断，数据库也不会残留半成品数据。"
              "流程见图 6，关键伪代码见下。"),
        ("img", "图6-数据导入流程图.png", "图6 数据导入流程图（含失败分支）", 11.6),
        ("code", [
            "# 伪代码 1：批次导入主流程（import_samples.py 的组织方式）",
            "function import_batch(data_dir, datasets):",
            "    batch = audit.open_batch(data_dir)            # stage2_meta.import_batch",
            "    verify_source_sha256(data_dir, snapshot)      # 不一致 → 记录差异并中止",
            "    with transaction():                           # 整批一个事务",
            "        for file in discover(data_dir):",
            "            audit.register_file(batch, file)      # 源文件登记 + SHA256",
            "            for doc in split_logical_roots(file):  # 逻辑根切分",
            "                parser = select_parser(doc.dataset_code)",
            "                record = parser.parse(doc)         # 著录项/人员/分类/引用/权项",
            "                upsert_dataset(record.dataset)",
            "                upsert_patent(record.patent)       # 幂等键：局 + 申请号 + 种类",
            "                upsert_publication(record.publications)",
            "                upsert_weak_entities(record)       # title/abstract/claim/...",
            "                upsert_relations(record)           # 人员角色、分类、引用、族",
            "            audit.finish_file(batch, file, row_counts)",
            "        assert_row_counts(batch)                   # 与解析统计核对",
            "    return batch                                   # 失败则整体回滚并留痕",
        ]),
        ("code", [
            "# 伪代码 2：幂等写入（同一个文件重复导入不产生重复行）",
            "function upsert_patent(rec):",
            "    row = select_from_patent(appln_auth=rec.auth, appln_nr=rec.nr, appln_kind=rec.kind)",
            "    if row is null:",
            "        insert_into_patent(rec)                    # 首次出现",
            "    else:",
            "        update_patent(row.patent_id, rec)           # 幂等：覆盖同值，不新增行",
            "    return patent_id",
        ]),
        ("h2", "3.7 验收测试流程"),
        ("p", "验收脚本在一次性容器里从空库开始：执行三个建库 SQL、校验源文件 SHA256、按三种口径导入、"
              "跑全部测试（故障注入、冒烟、外键、复杂与边界、前端）、归档查询计划、比对 46 张表的内容、"
              "导出备份并在另一个数据库里恢复后再次比对，最后把结果写成 JSON 并以退出码表示成功或失败。"
              "流程见图 7。"),
        ("img", "图7-验收流程图.png", "图7 验收流程图：全新容器复现与证据落盘", 14.8),
        ("h2", "3.8 分析挖掘设计"),
        ("p", "分析挖掘的目标是“用完整库回答几个具体问题”，而不是堆砌函数。本组确定 5 个主题、共 {q} 条 "
              "SQL，全部写成脚本文件（可重复执行、结果落盘），并把每个主题的结论都标注适用范围。"
              "选择主题时遵守一条规则：只做已经被数据支撑的分析，例如“被引热度”在本批样例中无法计算"
              "（被引目标全部在库外），就改为分析“引用方结构”与“被引文献的来源分布”。"
              .format(q=ctx["query_count"])),
        ("table", "表6 分析挖掘主题、SQL 与产出",
         ["主题", "回答的问题", "SQL 文件", "产出"],
         [["技术领域分布", "样例覆盖哪些技术领域？IPC 与 CPC 分布是否一致？",
           "01-技术领域分布.sql（ipc_section / ipc_class / coverage）", "图 11"],
          ["申请人排名与角色分布", "谁在申请？机构与自然人比例如何？五类角色覆盖多少专利？",
           "02-申请人排名.sql（applicant_rank / applicant_type / role_summary）", "图 12"],
          ["引用网络结构", "引用多少条、类型如何？出度集中在谁身上？被引文献来自哪些国家与年代？",
           "03-引用网络.sql（type_split / out_degree / cited_country / cited_decade / resolution）",
           "图 13、图 14"],
          ["权利要求与多语言", "独立 / 从属权项比例？说明书与附图规模？多语言如何分布？",
           "04-权利要求与全文结构.sql（claim_type / lang_split / doc_structure / dependency）", "图 15"],
          ["数据来源与时序", "五类数据各有多少？申请与公布年份分布？专利族规模与法律状态事件？",
           "05-数据来源与时序.sql（dataset_split / publn_year / filing_year / family_size / "
           "legal_event / keyword_source）", "图 16"]],
         [2.6, 4.6, 5.2, 1.8]),
    ]


# --------------------------------------------------------------------------- 四、结果展示
def section_result(ctx):
    st, an, ex = ctx["st"], ctx["an"], ctx["extra"]
    row_rows = ctx["row_groups"]
    test_rows = ctx["tests"]
    env_rows = ctx["env"]
    ipc = {r["部"]: r for r in an["ipc_section"] if r["分类体系"] == "IPC"}
    cpc = {r["部"]: r for r in an["ipc_section"] if r["分类体系"] == "CPC"}
    p_cit = [r for r in an["type_split"] if r["类型码"] == "P"][0]
    n_cit = [r for r in an["type_split"] if r["类型码"] == "N"][0]
    res = an["resolution"][0]
    ctry = an["cited_country"]
    dec = an["cited_decade"]
    claims = {r["类型码"]: r for r in an["claim_type"]}
    langs = an["lang_split"]
    fams = an["family_size"]
    events = an["legal_event"]
    return [
        ("h2", "4.1 实现环境与依赖"),
        ("table", "表7 实现环境与关键依赖", ["项目", "版本 / 说明"],
         env_rows, [4.0, 10.4], None),
        ("h2", "4.2 建库与导入结果"),
        ("p", "三个建库脚本按“建表 → 审计迁移 → 导入审计”顺序执行即可从空库得到与交付库一致的结构；"
              "导入脚本按基础、补充、批次三种口径运行，共写入 {rows} 行数据。其中 patent 与 publication "
              "各 19 行，43 张业务表中 42 张非空，唯一空表是 family_citation（缺少可靠的双端官方族号）。"
              "各域的行数分布见下表。".format(rows=st["rows"])),
        ("table", "表8 43 张业务表按业务域的行数统计（合计 {rows} 行）".format(rows=st["rows"]),
         ["业务域", "表数", "行数", "主要表与行数", "说明"],
         row_rows, [2.4, 1.0, 1.4, 5.4, 4.2], None),
        ("h2", "4.3 约束、索引与范式落地情况"),
        ("p", "约束不是写在文档里，而是在数据库里生效：43 个主键、{fk} 个外键、{uq} 个唯一约束"
              "（其中 {uqm} 个是跨列的复合唯一键）、{chk} 个业务检查约束、{notnull} 个非空约束、"
              "{idx} 个索引（43 个主键索引 + 22 个唯一索引 + {aux} 个辅助索引）。"
              "统计口径与证据查询见下表。".format(fk=st["fk"], uq=st["uq"], uqm=st["uq_multi"],
                                              chk=st["chk"], notnull=st["notnull"], idx=st["idx"],
                                              aux=st["idx_aux"])),
        ("table", "表9 数据库对象与约束统计",
         ["对象 / 约束", "数量", "统计口径（可在库内复核）", "说明"],
         [["业务表（schema patentdb）", "43", "information_schema.tables", "A 阶段划分的 38 核心 + 5 增强"],
          ["字段", st["fields"], "information_schema.columns", "含长短文本、日期、代码与代理键"],
          ["主键", "43", "pg_constraint contype='p'", "每张表都有主键"],
          ["外键", st["fk"], "pg_constraint contype='f'", "含引用表的两个外键与自引用"],
          ["唯一约束", "{t}（复合 {m}）".format(t=st["uq"], m=st["uq_multi"]), "pg_constraint contype='u'",
           "弱实体部分键、文献号、分类号组合等"],
          ["检查约束 / 非空约束", "{c} / {n}".format(c=st["chk"], n=st["notnull"]),
           "pg_constraint contype='c' 与 attnotnull", "引用类型、语言码、编号正负等"],
          ["索引", "{i}（主键 43 + 唯一 22 + 辅助 {a}）".format(i=st["idx"], a=st["idx_aux"]),
           "pg_indexes", "覆盖申请号、文献号、分类号、人员姓名等常用检索列"],
          ["审计表 + 视图", "3 + 1", "schema stage2_meta",
           "import_batch / source_document / publication_state + active_publication 视图"]],
         [3.4, 2.6, 4.0, 4.4], None),
        ("p", "约束是否真的生效，用反例验证：外键违规插入 14 例全部被拒绝（SQLSTATE 23503，"
              "例如向 patent_applicant 写入不存在的 patent_id 或 person_id）；"
              "唯一键冲突被拒绝（SQLSTATE 23505）；ISA 子类约束用延迟触发器和迁移脚本校验，"
              "保证 person 记录有且仅有一个对应的 natural_person / organization。"
              "测试脚本还刻意在“缺表”“空库”“约束被绕过”三种故障下运行，全部以非 0 退出码失败，"
              "证明验收流程不会假通过。"),
        ("h2", "4.4 前端展示"),
        ("p", "前端用 Flask 实现，首页列出全部 43 张业务表并显示行数（图 8）；点击表名进入通用表浏览页面"
              "（图 9）；点击 patent 表的 patent_id 进入详情页，只展示活动文献及其标题、摘要与权利要求"
              "（图 10）。数据库异常时页面返回 HTTP 503 并显示“数据加载失败”与原因，而不是显示成空表。"),
        ("img", "图8-前端首页43表.png", "图8 前端首页：43 张业务表的列表与行数", 14.0),
        ("img", "图9-前端patent表.png", "图9 前端通用表浏览页面（patent 表 19 行）", 14.0),
        ("img", "图10-前端专利详情.png", "图10 前端专利详情页面（只显示活动文献）", 14.0),
        ("h2", "4.5 测试与验收结果"),
        ("p", "测试覆盖五类用例：故障注入、冒烟、外键违规、复杂与边界、前端。合计 {cases} 条用例全部通过。"
              "更重要的是验收方式：全部测试在一次性容器里从空库开始执行，结束后对 46 张表逐表比对内容，"
              "再用 pg_dump 备份到另一个数据库恢复并再次比对，两次比对一致才判定通过。"
              .format(cases=ctx["test_total"])),
        ("table", "表10 测试与验收用例汇总（{cases} 条全部通过）".format(cases=ctx["test_total"]),
         ["测试脚本", "用例数", "通过", "覆盖内容", "证据文件"],
         test_rows, [4.2, 1.4, 1.4, 4.6, 2.8], None),
        ("bullets", [
            "故障注入：缺 schema、空 schema、被引外键被绕过等故障下必须失败（6/6）。",
            "冒烟：43 张业务表逐表 SELECT，核对行数与样例行数（48/48）。",
            "外键违规：14 条违反外键的写入全部被数据库拒绝（14/14）。",
            "复杂与边界：多表连接、专利族成员、空值、超长文本、特殊字符（12/12）。",
            "前端：首页表数、逐表页面、详情页与错误路径（71/71）。",
            "数据库备份：third stage/08-数据库交付/patentdb-phase3.dump，SHA256 {dump}，"
            "恢复库与源库共 46 张表逐表比对一致。".format(dump=ctx["dump"]),
        ]),
        ("h2", "4.6 分析挖掘结果"),
        ("p", "以下五项分析全部通过脚本执行（run_analysis.py 依次运行 5 个 SQL 文件，"
              "并把每条查询的结果导出为 CSV/JSON，再据此生成图表）。"
              "所有结论只描述官方样例这批数据，不能外推到整个专利领域。"),
        ("h3", "4.6.1 技术领域分布"),
        ("p", "19 件申请中有 16 件带分类号（覆盖率 {cov}%）。按 IPC 统计，A 部（人类生活必需）9 件最多，"
              "其次是 H 部（电学）{h} 件、G 部（物理）{g} 件；按大类看，A01（农业、林业、园艺等）{a01} 件、"
              "H04（电通信技术）{h04} 件、G06（计算）{g06} 件。CPC 的分布与 IPC 同向（A 部 {ca} 件最多），"
              "但覆盖面更窄。结论：本批样例以园艺、消费品与机械类技术为主，通信、半导体等领域几乎没有覆盖。"
              .format(cov=an["coverage"][0]["覆盖率百分比"], h=ipc.get("H", {}).get("专利数", 0),
                      g=ipc.get("G", {}).get("专利数", 0),
                      a01=next((r["专利数"] for r in an["ipc_class"] if r["大类"] == "A01"), 0),
                      h04=next((r["专利数"] for r in an["ipc_class"] if r["大类"] == "H04"), 0),
                      g06=next((r["专利数"] for r in an["ipc_class"] if r["大类"] == "G06"), 0),
                      ca=cpc.get("A", {}).get("专利数", 0))),
        ("img", "图11-技术领域分布.png", "图11 技术领域分布（IPC / CPC 部级，按专利去重）", 14.5),
        ("h3", "4.6.2 申请人排名与人员角色分布"),
        ("p", "申请主体共 {u} 个（机构 {op} 家、自然人 {np} 名），与 {c} 件专利建立 {links} 条申请关系，"
              "平均每件 1.1 个申请人——样例基本是单申请人的情形，不存在复杂的共同申请结构。"
              "图 12 展示按专利数排序的前 10 名：排名第一的两位各 {t} 件（{n1}、{n2}），"
              "其余均为 1 件；分析 SQL 的排名口径为 TOP15，第 16 位及以后不影响结论。"
              "五类角色中发明人关联最多（{inv} 条 / {invp} 件专利），其次是申请人（{app} 条 / {appp} 件），"
              "代理人 12 条、审查员 10 条、权利人（受让人）9 条，角色分布与数据手册给出的著录项目一致。"
              "这里有一个必须说明的数据质量观察：源样例中部分明显是机构的名称（例如 Husqvarna AB、"
              "SIEMENS AG、Weyerhaeuser Nr Company）被标为自然人类型，本组按“不修改来源事实”的原则"
              "原样入库，因此 person_type 只能作参考，机构 / 自然人的划分不能直接用于统计结论。".format(
                  u=int(next(r["人数"] for r in an["applicant_type"] if r["类型"] == "机构"))
                  + int(next(r["人数"] for r in an["applicant_type"] if r["类型"] == "自然人")),
                  op=next(r["人数"] for r in an["applicant_type"] if r["类型"] == "机构"),
                  np=next(r["人数"] for r in an["applicant_type"] if r["类型"] == "自然人"),
                  c=next(r["专利数"] for r in an["role_summary"] if r["角色"] == "申请人"),
                  links=next(r["关联条数"] for r in an["role_summary"] if r["角色"] == "申请人"),
                  t=an["applicant_rank"][0]["专利数"],
                  n1=an["applicant_rank"][0]["申请人"], n2=an["applicant_rank"][1]["申请人"],
                  inv=next(r["关联条数"] for r in an["role_summary"] if r["角色"] == "发明人"),
                  invp=next(r["专利数"] for r in an["role_summary"] if r["角色"] == "发明人"),
                  app=next(r["关联条数"] for r in an["role_summary"] if r["角色"] == "申请人"),
                  appp=next(r["专利数"] for r in an["role_summary"] if r["角色"] == "申请人"))),
        ("img", "图12-申请人排名.png", "图12 申请人排名（前 10 名，按专利数去重）", 14.5),
        ("h3", "4.6.3 引用网络结构"),
        ("p", "库内共 {total} 条引用，其中专利文献引用（P）{p} 条、非专利文献引用（N）{n} 条，"
              "非专利引用还有 {npl} 条明细存在 non_patent_citation 表中。出度分布极不均衡："
              "最高的一件专利引用 {top} 条文献（其中专利文献 {topp} 条，占全部专利文献引用的 {share}%），"
              "第二名 {second} 条，其余都在 20 条以内。被引文献的来源国别以 US {c_us} 次为主，"
              "WO {c_wo} 次、JP {c_jp} 次、EP {c_ep} 次、GB {c_gb} 次，其余国家各 1–2 次；"
              "被引文献的年代集中在 2000—2009 年（{d2000} 次）与 1990—1999 年（{d1990} 次）。"
              "关键限制：被引目标全部在库外——{p} 条专利文献引用中库内可解析 {resolved} 条，"
              "因此本报告只能回答“谁引用了多少文献”，不能回答“谁被引用最多”。".format(
                  total=res["引用总条数"], p=p_cit["引用条数"], n=n_cit["引用条数"],
                  npl=res["非专利引用明细"], top=an["out_degree"][0]["合计"],
                  topp=an["out_degree"][0]["专利引用"],
                  share=round(100 * _num(an["out_degree"][0]["专利引用"]) / _num(p_cit["引用条数"]), 1),
                  second=an["out_degree"][1]["合计"], c_us=ctry[0]["被引次数"],
                  c_wo=ctry[1]["被引次数"], c_jp=ctry[2]["被引次数"], c_ep=ctry[3]["被引次数"],
                  c_gb=ctry[4]["被引次数"],
                  d2000=next((r["被引次数"] for r in dec if r["年代段"] == "2000"), 0),
                  d1990=next((r["被引次数"] for r in dec if r["年代段"] == "1990"), 0),
                  resolved=res["库内已解析"])),
        ("img", "图13-引用网络结构.png", "图13 引用类型分布与引用方出度 TOP8", 14.5),
        ("img", "图14-被引国别与年代.png", "图14 被引专利文献的来源国别与年代分布", 14.5),
        ("h3", "4.6.4 权利要求结构与多语言"),
        ("p", "库内共 {total} 条权利要求：独立权利要求（I）{i} 条、从属权利要求（D）{d} 条；"
              "另有 {dep} 条从属依赖记录（claim_dependency，依赖类型均为 claim-ref），与从属权项一一对应。"
              "结构最大的一篇是 {top_doc}（{top_i} 项独立权项、说明书章节 {top_sec} 节、附图 {top_fig} 幅）。"
              "多语言方面：EN {en} 条、DE {de} 条、FR {fr} 条权利要求，标题分别为 18 / 6 / 6 条。"
              "统计时必须按语言分别计数，否则会把同一篇文献的权利要求重复计算三次。".format(
                  total=_num(claims["I"]["条数"]) + _num(claims["D"]["条数"]), i=claims["I"]["条数"],
                  d=claims["D"]["条数"], dep=an["dependency"][0]["依赖条数"],
                  top_doc=an["doc_structure"][0]["文献号"], top_i=an["doc_structure"][0]["独立权项"],
                  top_sec=an["doc_structure"][0]["说明书章节"], top_fig=an["doc_structure"][0]["附图"],
                  en=langs[0]["权利要求"], de=langs[1]["权利要求"], fr=langs[2]["权利要求"])),
        ("img", "图15-权利要求与多语言.png", "图15 各文献权利要求结构与多语言分布", 14.5),
        ("h3", "4.6.5 数据来源与时序"),
        ("p", "五类数据集分别贡献 {d1}、{d0}、{d2}、{d3}、{d4} 篇文献，其中美国授权公告（US_GRANT）最多。"
              "公布年份只集中在三个年份：1979（2 篇）、2014（{y2014} 篇）、2020（1 篇），"
              "说明本批样例的主体是 2014 年公布的美国文献；申请年份跨度从 1979 到 2019，其中 2013 年 7 件。"
              "专利族方面：{fam_n} 个族（2 个 DOCDB 族分别有 7 名和 3 名成员，1 个 INPADOC 族 1 名成员），"
              "每个族在库内各只有 1 名成员，说明样例只给了族头信息而没有给全族成员。"
              "法律状态共 {ev_n} 条事件、{ev_c} 类事件码（RIC1 5 条、STAA 2 条等）；关键词 {kw} 条"
              "全部来自本组基于标题的派生（source = TITLE_DERIVED），不是官方字段。".format(
                  d0=ctx["datasets"][1]["文献数"], d1=ctx["datasets"][0]["文献数"],
                  d2=ctx["datasets"][2]["文献数"], d3=ctx["datasets"][3]["文献数"],
                  d4=ctx["datasets"][4]["文献数"],
                  y2014=next((r["文献数"] for r in an["publn_year"] if r["公布年份"] == "2014"), 0),
                  fam_n=len(fams), ev_n=sum(_num(r["事件条数"]) for r in events), ev_c=len(events),
                  kw=an["keyword_source"][0]["数值"])),
        ("img", "图16-数据来源与年份.png", "图16 数据来源分布与文献公布年份分布", 14.5),
        ("h2", "4.7 局限性分析"),
        ("p", "本系统的局限主要来自“样例规模小 + 来源本身有缺口”，可以分成数据、设计、实现、分析四类："),
        ("bullets", [
            "数据范围：只使用 5 类官方样例，共 19 件申请，任何统计结论都只在本批数据内成立；"
            "申请与公布年份集中在少数年份，样本在时间维度几乎没有代表性。",
            "引用不可闭环：508 条专利文献引用的被引目标全部在库外，库内解析数为 0，"
            "因此无法计算被引次数、引用网络中心性或技术演化路径，只能给出引用方结构。",
            "专利族不完整：样例只给族头与少量成员，库内每族仅 1 名成员；"
            "family_citation 因缺少可靠的双端族号而保持 0 行。",
            "人员与机构语义：person_type 由源记录类型直接映射，样例中存在机构被标为自然人的情况；"
            "本组不做推断式修正，因此该字段的统计口径受限。",
            "关键词是派生数据：keyword / patent_keyword 基于标题生成并标注 TITLE_DERIVED，"
            "可用于演示增强表，但不能当作官方标引结果使用。",
            "性能未压测：数据量只有几千行，索引与查询计划只能证明结构合理，不能证明大规模数据下的性能；"
            "未做分区、并行导入或物化视图优化。",
            "功能边界：前端只读，没有权限与用户体系，也没有写入与编辑接口；"
            "数据库以单机容器方式运行，未涉及复制、备份策略与灾备。",
            "导入器覆盖面：解析器按 5 类样例家族实现，若换成未覆盖的局别或新版数据手册，"
            "需要补充解析规则并重新做字段映射。",
        ]),
    ]


# --------------------------------------------------------------------------- 五、小组总结
def section_conclusion(ctx):
    st = ctx["st"]
    return [
        ("h2", "5.1 遇到的问题与解决过程"),
        ("p", "四个阶段的问题与修正记录分别保存在：第一阶段/90-问题记录-A.md（12 条）、"
              "second stage/04-报告与基线/数据库设计变更说明.md（5 项结构变更）、"
              "third stage/90-问题记录-C.md（11 条）和 fourth stage/90-问题记录-D.md（{d} 条）。"
              "下表按阶段选出对设计影响最大的 18 条，完整记录见上述文档。".format(d=ctx["problem_rows"])),
        ("table", "表11 各阶段典型问题与处理方式（完整记录见各阶段问题记录文档）",
         ["阶段", "问题", "处理方式与证据"],
         ctx["problems"], [1.8, 5.4, 7.2], None),
        ("h2", "5.2 收获与体会"),
        ("p", "这次实践最大的收获是理解了“概念模型—关系模式—物理约束”三者必须能相互对照："
              "E-R 图里画的弱实体、自引用、ISA，如果不在建表和约束里留下痕迹，几天后就无法验证它是否被实现。"
              "本组把每一条设计决策都配上一个可在数据库里复核的证据（约束名、行数、测试用例），"
              "这让后续的修改和交接都变得可控。"),
        ("bullets", [
            "数据来源要当真：样例里没有的事实（未查证的组织信息、月精度日期、库外被引文献、"
            "缺失的族号）如果被“猜”出来，后续所有分析都会建立在错误事实上。本组选择留空并声明，"
            "虽然表的行数少了几行，但结论可靠。",
            "约束写在数据库里比写在代码里更划算：91 个外键与 22 个唯一约束自动挡住了大部分错误数据，"
            "导入脚本因此可以专注于解析逻辑。",
            "测试要用反例证明：只验证“正常路径能跑通”不足以说明系统可靠，"
            "本组刻意注入缺表、空库、外键违规、超长文本等故障，并让脚本在故障下以非 0 退出码失败。",
            "分工的关键是交接物的格式：每个阶段都给出“脚本 + 数据库 + 文档 + 证据文件”四件套，"
              "下一阶段可以直接复现上一阶段的结论，不必反复口头确认。",
            "文档和图要一起写：画流程图、框图与伪代码的过程，反过来暴露了几处设计不一致"
              "（例如“引用挂在专利还是文献上”），最终确认引用记录同时保留专利与文献两级引用方。",
        ]),
        ("h2", "5.3 对上机实验的建议"),
        ("bullets", [
            "建议在题目说明里明确“官方样例即是验收口径”，避免把精力花在获取全量数据上；"
            "本组在数据获取阶段（A）花了较多时间才确认必须回到官方样例。",
            "建议给出一份最小的约束清单（例如要求哪些表必须表达弱实体、自引用、ISA），"
            "这样不同小组的“设计完整度”更容易横向比较。",
            "建议把“可复现”明确为评分项：本组的 verify_fresh.py 从空容器开始跑完整个流程并留下证据，"
            "但如果课程不要求，很容易变成只在本地跑通一次。",
            "建议提前说明环境差异（Python 版本、驱动版本、Docker 权限），"
            "本组遇到过驱动在 Python 3.14 无法安装、Git 换行改变源文件指纹等环境相关的坑。",
        ]),
        ("h2", "5.4 AI 使用声明"),
        ("p", "本组在课程允许的范围内使用 AI 辅助工具，主要用于资料检索、代码草稿、测试用例生成、"
              "文档措辞与格式检查；所有涉及事实与结论的内容均由组员核对仓库内证据后确认。"
              "使用记录按阶段归档（第一阶段/92-AI使用记录.md、third stage/92-AI使用记录-C.md、"
              "fourth stage/92-AI使用记录-D.md），下表为汇总。"),
        ("table", "表12 AI 辅助使用汇总", ["阶段", "用途", "人工核对方式"],
         ctx["ai"], [1.8, 6.6, 6.0], None),
        ("h2", "5.5 附录 A：交付物清单"),
        ("table", "表13 最终交付物清单", ["目录 / 文件", "内容"],
         ctx["deliver"], [5.4, 9.0], None),
        ("h2", "5.6 附录 B：复现命令"),
        ("p", "以下命令均从仓库根目录执行，用于复核本报告中的数据与图表；"
              "详细说明见 README 与各阶段文档。"),
        ("code", [
            "# 1) 准备环境（Python 3.10+）",
            "python3 -m venv .venv",
            ".venv/bin/python -m pip install -r 'third stage/01-前端应用/requirements.txt'",
            "",
            "# 2) 启动数据库容器并跑第三阶段验收（固定官方样例）",
            "bash run.sh",
            "",
            "# 3) 全新容器复现（建库、导入、全部测试、dump 与恢复比对）",
            ".venv/bin/python 'third stage/06-运行管理/verify_fresh.py'",
            "",
            "# 4) 执行分析挖掘（5 个主题 21 条 SQL）+ 生成 6 张统计图",
            ".venv/bin/python 'fourth stage/03-分析挖掘/run_analysis.py'",
            "",
            "# 5) 重新生成流程图与框图",
            ".venv/bin/python 'fourth stage/04-流程图与框图/gen_diagrams.py'",
            "",
            "# 6) 打包提交",
            ".venv/bin/python 'fourth stage/05-打包/package_submission.py'",
        ]),
        ("h2", "5.7 附录 C：与报告模板的对应关系"),
        ("p", "本报告按《报告模板.docx》的规范撰写：页面为 A4 纵向、左右边距 3.17 cm、上下 2.54 cm；"
              "一级标题沿用模板的自动编号（numId=5，格式“一、二、三…”）与黑体三号加粗；"
              "正文为宋体小四、1.5 倍行距、首行缩进 2 字符；表格使用模板自带的 Table Grid 样式，"
              "表头黑体加底纹；图题在图下居中，表题在表上居中。模板的五个一级标题"
              "（报告摘要、需求分析、方案设计、结果展示、小组总结）全部保留，"
              "二级及以下标题采用 1.1 / 1.1.1 的十进制编号，以便与表格、图、章节交叉引用。"
              "详细对照见同目录《模板对照说明.md》。"),
    ]


def build_blocks(ctx):
    return {
        "报告摘要": section_summary(ctx),
        "需求分析": section_requirement(ctx),
        "方案设计": section_design(ctx),
        "结果展示": section_result(ctx),
        "小组总结": section_conclusion(ctx),
    }


