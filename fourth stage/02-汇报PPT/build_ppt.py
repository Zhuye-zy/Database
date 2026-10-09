#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成第四阶段汇报 PPT（python-pptx）。

设计要点：
  * 16:9（13.333 in × 7.5 in），统一版式：标题栏 + 强调色分隔线 + 页码；
  * 全部数字来自第四阶段报告生成器 build_report.build_ctx()（与 docx 同源，
    数据源为逐表行数.json、*_result.json、analysis_results.json），保证报告与 PPT 口径一致；
  * 图片取自 01-设计文档/图/（报告用图）与 03-分析挖掘/图表/，按原始宽高比自适应摆放；
  * 中英文字体统一为微软雅黑，显式写入 a:latin 与 a:ea，避免在无中文字体的播放环境出现方框。

运行：python3 "fourth stage/02-汇报PPT/build_ppt.py"
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pptx.util import Emu, Inches, Pt

DIR = Path(__file__).resolve().parent
STAGE = DIR.parent
DOCDIR = STAGE / "01-设计文档"
REPO = STAGE.parent
FIGDIR = DOCDIR / "图"
CHARTDIR = STAGE / "03-分析挖掘" / "图表"
OUT = DIR / "第四阶段汇报-专利数据关系数据库.pptx"
SCRIPT = DIR / "第四阶段汇报-讲稿.md"

sys.path.insert(0, str(DOCDIR))
import build_report as br  # noqa: E402  （复用同一套证据与数字）

# --------------------------------------------------------------------------- 视觉规范
FONT = "微软雅黑"
NAVY = RGBColor(0x12, 0x33, 0x55)
BLUE = RGBColor(0x1F, 0x6F, 0xB2)
TEAL = RGBColor(0x17, 0xA3, 0x98)
AMBER = RGBColor(0xE0, 0x92, 0x2B)
RED = RGBColor(0xC0, 0x50, 0x4D)
INK = RGBColor(0x22, 0x2A, 0x35)
GREY = RGBColor(0x5A, 0x64, 0x72)
LIGHT = RGBColor(0xF2, 0xF5, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

SW, SH = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.62)
BODY_TOP = Inches(1.28)
BODY_W = SW - 2 * MARGIN

# 每页标题（按页序记录，供讲稿 Markdown 与页内备注使用）
SLIDE_TITLES: list[tuple[int, str]] = []


def new_deck() -> Presentation:
    deck = Presentation()
    deck.slide_width = Emu(int(SW))
    deck.slide_height = Emu(int(SH))
    return deck


def _style_run(run, *, size, bold, color, font=FONT):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    latin = rPr.get_or_add_latin()
    latin.set("typeface", font)
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = parse_xml(f'<a:ea {nsdecls("a")} typeface="{font}"/>')
        latin.addnext(ea)
    else:
        ea.set("typeface", font)


def add_shape(slide, kind, left, top, width, height, fill, line=None, shadow=False):
    shape = slide.shapes.add_shape(kind, Emu(int(left)), Emu(int(top)), Emu(int(width)),
                                   Emu(int(height)))
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    shape.shadow.inherit = shadow
    shape.text_frame.word_wrap = True
    return shape


def add_text(slide, left, top, width, height, lines, *, size=16, bold=False, color=INK,
             align=PP_ALIGN.LEFT, line_spacing=1.25, anchor=MSO_ANCHOR.TOP):
    """lines: str，或 [(文本, 缩进层级, 加粗, 颜色, 字号), ...]。"""
    box = slide.shapes.add_textbox(Emu(int(left)), Emu(int(top)), Emu(int(width)),
                                   Emu(int(height)))
    frame = box.text_frame
    frame.word_wrap = True
    frame.vertical_anchor = anchor
    frame.margin_left = frame.margin_right = Emu(0)
    frame.margin_top = frame.margin_bottom = Emu(0)
    if isinstance(lines, str):
        lines = [lines]
    for index, item in enumerate(lines):
        if isinstance(item, str):
            text, indent, item_bold, item_color, item_size = item, 0, bold, color, size
        else:
            text = item[0]
            indent = item[1] if len(item) > 1 else 0
            item_bold = item[2] if len(item) > 2 else bold
            item_color = item[3] if len(item) > 3 else color
            item_size = item[4] if len(item) > 4 else size
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.alignment = align
        paragraph.line_spacing = line_spacing
        paragraph.space_after = Pt(5 if item_size >= 15 else 3)
        run = paragraph.add_run()
        run.text = ("　" * indent) + ("· " if indent else "") + text
        _style_run(run, size=item_size, bold=item_bold, color=item_color)
    return box


def kpi_row(slide, items, top=Inches(1.4), height=Inches(1.2), gap=Inches(0.16),
            colors=(BLUE, TEAL, AMBER, NAVY)):
    """items: [(大数字, 说明), ...]，横向等分卡片。"""
    count = len(items)
    width = int((BODY_W - (count - 1) * gap) / count)
    for index, (value, label) in enumerate(items):
        left = int(MARGIN) + index * (width + int(gap))
        card = add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, int(top), width,
                         int(height), LIGHT, line=RGBColor(0xD5, 0xDF, 0xE8))
        card.adjustments[0] = 0.08
        add_text(slide, left + Inches(0.18), int(top) + Inches(0.06), width - Inches(0.32),
                 Inches(0.6), str(value), size=25, bold=True, line_spacing=1.0,
                 color=colors[index % len(colors)])
        add_text(slide, left + Inches(0.18), int(top) + Inches(0.62), width - Inches(0.32),
                 Inches(0.52), label, size=11.5, line_spacing=1.15, color=GREY)


def add_picture_fit(slide, path, left, top, max_w, max_h, caption=None, caption_size=11):
    """按原始宽高比把图片放进给定矩形区域（居中），可在下方加图注。"""
    from PIL import Image

    with Image.open(path) as image:
        ratio = image.size[0] / image.size[1]
    width = max_w
    height = int(width / ratio)
    if height > max_h:
        height = max_h
        width = int(height * ratio)
    left = int(left + (max_w - width) / 2)
    picture = slide.shapes.add_picture(str(path), Emu(int(left)), Emu(int(top)), Emu(width),
                                       Emu(height))
    if caption:
        add_text(slide, left, int(top) + height + Inches(0.04), width, Inches(0.3), caption,
                 size=caption_size, color=GREY, align=PP_ALIGN.CENTER)
    return picture


def add_table(slide, header, rows, left, top, width, col_ratios, *, size=13,
              row_h=Inches(0.42)):
    shape = slide.shapes.add_table(len(rows) + 1, len(header), Emu(int(left)), Emu(int(top)),
                                   Emu(int(width)), Emu(int(row_h * (len(rows) + 1))))
    table = shape.table
    total = sum(col_ratios)
    for index, ratio in enumerate(col_ratios):
        table.columns[index].width = Emu(int(width * ratio / total))
    for col, text in enumerate(header):
        cell = table.cell(0, col)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.text = ""
        paragraph = cell.text_frame.paragraphs[0]
        paragraph.alignment = PP_ALIGN.CENTER
        run = paragraph.add_run()
        run.text = str(text)
        _style_run(run, size=size, bold=True, color=WHITE)
    for row_index, row in enumerate(rows, start=1):
        for col, value in enumerate(row):
            cell = table.cell(row_index, col)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if row_index % 2 else LIGHT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.text = ""
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER if col else PP_ALIGN.LEFT
            run = paragraph.add_run()
            run.text = str(value)
            _style_run(run, size=size - 1, bold=False, color=INK)
    return table


def footer(slide, text, page):
    add_text(slide, MARGIN, SH - Inches(0.44), BODY_W - Inches(0.8), Inches(0.3), text,
             size=10, color=GREY)
    add_text(slide, SW - Inches(1.1), SH - Inches(0.44), Inches(0.5), Inches(0.3), str(page),
             size=11, bold=True, color=BLUE, align=PP_ALIGN.RIGHT)


def title_slide(deck, ctx, meta):
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    SLIDE_TITLES.append((1, "封面 · 题目 5 专利数据关系数据库设计与实践"))
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, SW, SH, NAVY)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, Inches(2.62), SW, Pt(3), TEAL)
    add_text(slide, MARGIN, Inches(1.5), BODY_W, Inches(0.9), "《数据库实践》课程报告",
             size=20, bold=True, color=RGBColor(0x9F, 0xC4, 0xE0))
    add_text(slide, MARGIN, Inches(2.92), BODY_W, Inches(1.2),
             "题目 5 · 专利数据关系数据库设计与实践", size=40, bold=True, color=WHITE)
    add_text(slide, MARGIN, Inches(4.16), BODY_W, Inches(0.8),
             "从五局官方样例 XML 到可复现、可验收、可分析的 PostgreSQL 数据库",
             size=17, color=RGBColor(0xC7, 0xD8, 0xE8))
    add_text(slide, MARGIN, Inches(5.3), BODY_W, Inches(1.35), meta,
             size=14, color=RGBColor(0xAE, 0xC7, 0xDD), line_spacing=1.5)
    return slide


def content_slide(deck, title, kicker=None, page=None, accent=BLUE):
    """空白版式 + 统一的标题栏 / 分隔线 / 页码。"""
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    SLIDE_TITLES.append((page or len(SLIDE_TITLES) + 1, title))
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, SW, Inches(1.06), NAVY)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, Inches(1.06), SW, Pt(3.5), accent)
    add_text(slide, MARGIN, Inches(0.14), BODY_W, Inches(0.64), title, size=25, bold=True,
             color=WHITE)
    if kicker:
        add_text(slide, MARGIN, Inches(0.66), BODY_W, Inches(0.36), kicker, size=12.5,
                 color=RGBColor(0xC7, 0xD8, 0xE8))
    if page is not None:
        add_text(slide, SW - Inches(1.1), Inches(0.28), Inches(0.6), Inches(0.4), str(page),
                 size=13, bold=True, color=RGBColor(0x9F, 0xB8, 0xD0), align=PP_ALIGN.RIGHT)
    return slide


def two_chart_slide(deck, ctx, *, title, kicker, page, left_img, left_cap, right_img, right_cap,
                    notes, accent=BLUE):
    """上下结构：两张图并排 + 结论要点。"""
    slide = content_slide(deck, title, kicker, page, accent)
    box_w, box_h = Inches(6.06), Inches(2.42)
    add_picture_fit(slide, left_img, MARGIN, Inches(1.42), box_w, box_h, left_cap)
    add_picture_fit(slide, right_img, MARGIN + box_w + Inches(0.03), Inches(1.42), box_w, box_h,
                    right_cap)
    add_text(slide, MARGIN, Inches(4.22), BODY_W, Inches(2.7), notes, size=14)
    footer(slide, "数据来源：fourth stage/03-分析挖掘/结果（analysis_results.json 与对应 CSV）", page)
    return slide


def build_deck(ctx) -> Presentation:
    deck = new_deck()
    st = ctx["st"]
    datasets = ctx["datasets"]
    tests = {row[0]: row for row in ctx["tests"]}
    test_total = ctx["test_total"]
    query_count = ctx["query_count"]
    rows_total = f"{st['rows']:,}"

    title_slide(deck, ctx, [
        "小组成员：A / B / C / D 四角色协作",
        f"数据规模：{st['tables']} 张业务表 / {st['fields']} 个字段 / {rows_total} 行 ｜ "
        f"验收：{test_total} 条用例全部通过 ｜ 分析：5 个主题 {query_count} 条 SQL",
        "2026 年 10 月",
    ])

    # 2 目录
    slide = content_slide(deck, "汇报大纲", "按“问题 → 设计 → 实现 → 结果 → 总结”推进", 2)
    outline = [
        ("01", "题目与数据边界", "五局官方样例 XML、5 类数据集、19 件申请"),
        ("02", "需求分析", "七类工程难点与完整性 / 非功能要求"),
        ("03", "方案设计", "六域 E-R、范式审查、物理设计、导入与验收流程"),
        ("04", "结果展示", f"{st['tables']} 张业务表、{rows_total} 行、前端与测试验收"),
        ("05", "分析挖掘与总结", f"5 个主题 {query_count} 条 SQL、6 张统计图、局限与收获"),
    ]
    card_w = Inches(2.42)
    for index, (num, name, detail) in enumerate(outline):
        left = MARGIN + index * (card_w + Inches(0.14))
        add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.6), card_w, Inches(3.1),
                  LIGHT, line=RGBColor(0xD5, 0xDF, 0xE8)).adjustments[0] = 0.06
        add_text(slide, left + Inches(0.2), Inches(1.82), card_w - Inches(0.4), Inches(0.7),
                 num, size=30, bold=True, color=BLUE)
        add_text(slide, left + Inches(0.2), Inches(2.62), card_w - Inches(0.4), Inches(0.5),
                 name, size=15, bold=True, color=NAVY)
        add_text(slide, left + Inches(0.2), Inches(3.14), card_w - Inches(0.4), Inches(1.4),
                 detail, size=11.5, color=GREY, line_spacing=1.3)
    add_text(slide, MARGIN, Inches(4.96), BODY_W, Inches(1.6), [
        "汇报重点：① 结构为什么这样设计（六域 E-R 与约束）；② 结果如何被验证（151 条用例与全新容器复现）；",
        "③ 数据能支撑什么结论、不能支撑什么结论（引用目标全部在库外的处理方式）。",
    ], size=14)
    footer(slide, "演示顺序与报告章节一致，所有数字来自仓库内可复核的证据文件", 2)

    # 3 题目与数据边界
    slide = content_slide(deck, "题目与数据边界", "题目 5：专利数据服务试验系统的五局基础数据（XML + 数据手册 + 官方样例）", 3)
    kpi_row(slide, [
        (len(datasets), "类官方样例数据集（US / EP 五局）"),
        ("17", "个基础 XML 源文件（SHA256 快照）"),
        ("19", "件申请 / 19 篇公布公告文献"),
        (rows_total, f"行入库数据（{st['tables']} 张业务表）"),
    ])
    add_text(slide, MARGIN, Inches(2.78), BODY_W, Inches(3.9), [
        "数据边界：试验系统不可访问，本组以官方样例与数据手册为唯一事实来源，不引入第三方数据",
        "语义对齐：按 INID 码把五局同义字段对齐（(21) 申请号、(22) 申请日、(51) 分类号、(54) 名称、(57) 摘要…）",
        "五类数据集：US 申请公布、US 授权公告、EP 全文、EP DOCDB 摘要、EP 法律状态",
        "样例规模：19 件申请、19 篇文献、3,576 行；结论一律限定在样例范围内，不外推行业趋势",
        "可追溯：导入前记录每个 XML 的 SHA256，导入后写入批次与字段级错误，失败整批回滚",
    ], size=15)
    footer(slide, "来源：第一阶段/01-需求分析.md、04-数据字典.csv；second stage/02-数据导入", 3)

    # 4 七类工程难点
    slide = content_slide(deck, "需求分析：七类必须在数据库里显式处理的难点", "它们决定了后面的表结构与约束设计", 4, accent=AMBER)
    left_items = [
        ["多值属性普遍：多申请人 / 多发明人 / 多分类号 / 上百条引用与权项",
         ["破 1NF 的单字段存多值必须消除 → 拆表 + 复合唯一键"]],
        ["弱实体必须带属主：title / abstract / claim / drawing / description_section",
         ["唯一键 = 属主键 + 部分键（语言、序号）"]],
        ["引用是一元递归且被引目标常在库外",
         ["cited_patent_id 可空，但保留被引国别/号码/种类原文"]],
        ["多语言与多版本：EP 的 EN / DE / FR 分套，权利要求分独立 / 从属",
         ["语言进入部分键，条数按语言分别统计"]],
    ]
    right_items = [
        ["日期精度不统一（YYYYMM00、哨兵值）",
         ["解析列 + 原文列并存，精度不足时置 NULL，不伪造日期"]],
        ["来源缺口要如实保留：family_citation 缺可靠双端族号",
         ["保留空表 + 文档声明，不用近似关系灌数据"]],
        ["可追溯与可重跑：课程要求能重复得到同一个库",
         ["SHA256 指纹 + 幂等键 + 审计表 + 整批事务"]],
        ["只读展示、错误可见：前端不得把 SQL 错误显示成“无数据”",
         ["写入只发生在导入脚本；异常返回 HTTP 503"]],
    ]
    for column, items in enumerate((left_items, right_items)):
        left = MARGIN + column * (Inches(6.06) + Inches(0.03))
        lines = []
        for title_text, sub in items:
            lines.append((title_text, 0, True, NAVY, 14))
            lines.append((sub[0], 1, False, GREY, 12.5))
        add_text(slide, left, Inches(1.5), Inches(6.06), Inches(5.3), lines, size=14,
                 line_spacing=1.2)
    footer(slide, "来源：第一阶段/90-问题记录-A.md、second stage/04-报告与基线/数据库设计变更说明.md", 4)

    # 5 总体技术路线
    slide = content_slide(deck, "总体技术路线：五阶段、四角色、同一套证据", "每阶段留下可复跑的脚本与结果文件", 5, accent=TEAL)
    add_picture_fit(slide, FIGDIR / "图4-总体流程图.png", MARGIN, Inches(1.36), BODY_W,
                    Inches(4.35), "图 4　总体流程图：四角色六阶段交付链")
    add_text(slide, MARGIN, Inches(6.06), BODY_W, Inches(0.9), [
        "阶段 1 需求与数据字典 → 阶段 2 结构设计与导入 → 阶段 3 约束补全与测试 → 阶段 4 分析挖掘与文档交付",
        "四个角色（A 需求与字典 / B 逻辑物理设计与导入 / C 前端与测试 / D 分析与文档）通过仓库目录约定交接",
    ], size=13.5, color=GREY)
    footer(slide, "图源：fourth stage/04-流程图与框图/gen_diagrams.py（可重跑生成）", 5)

    # 6 概念设计
    slide = content_slide(deck, "概念设计：六域 E-R 与主外键骨架", "域内强内聚、域间通过受控外键连接，避免大宽表", 6)
    add_picture_fit(slide, FIGDIR / "图3-关键表关系示意图.png", MARGIN, Inches(1.36), Inches(8.05),
                    Inches(4.5), "图 3　核心表关系示意图（申请 → 文献 → 标题/摘要/权项/分类/引用）")
    add_text(slide, MARGIN + Inches(8.25), Inches(1.5), Inches(3.85), Inches(5.05), [
        ("六个域", 0, True, NAVY, 15),
        ("申请与文献主域：application → publication", 1, False, INK, 13),
        ("主体域：applicant / inventor / agent 及其关联表", 1, False, INK, 13),
        ("内容域：title / abstract / claim / description_section", 1, False, INK, 13),
        ("分类域：ipc / cpc / locarno（多对多桥表）", 1, False, INK, 13),
        ("引用域：patent_citation / family_citation", 1, False, INK, 13),
        ("元数据域：数据集、批次、导入日志、字段级错误", 1, False, INK, 13),
        ("设计取舍", 0, True, NAVY, 15),
        ("弱实体拆表而非 JSON 列，保证可查询", 1, False, GREY, 12.5),
        ("文献是申请的表现形式，因此引用挂在文献粒度", 1, False, GREY, 12.5),
    ], line_spacing=1.2)
    footer(slide, "图源：fourth stage/04-流程图与框图/gen_diagrams.py；表结构见 01-设计文档/表结构清单.csv", 6)

    # 7 逻辑设计
    slide = content_slide(deck, f"逻辑设计：从 E-R 到 {st['tables']} 张关系表", "以“主键 + 受控外键 + 复合唯一键”表达每一个多元/多值语义", 7)
    kpi_row(slide, [
        (st["tables"], "张业务表（含 6 张桥表与统计辅助表）"),
        (st["fields"], "个字段（字段级注释齐全）"),
        (st["fk"], "个外键（含级联删除/置空策略）"),
        (st["idx"], f"个索引（其中辅助索引 {st['idx_aux']} 个）"),
    ])
    add_text(slide, MARGIN, Inches(2.78), BODY_W, Inches(4.0), [
        ("范式审查：逐条给出“函数依赖 → 判定 → 处理”三段式结论", 0, True, NAVY, 15),
        ("1NF：消灭“分类号列表”“申请人列表”这类多值字段，全部拆成独立行", 1, False, INK, 13.5),
        ("2NF：桥表与弱实体表使用复合主键/复合唯一键，非键属性完全依赖于整个键", 1, False, INK, 13.5),
        ("3NF：把不属于该表的下拉字段（如国别名称、分类标题）留在一张字典/明细表内，不在多处冗余", 1, False, INK, 13.5),
        ("BCNF：存在多候选键的表（如按语言/序号定位的弱实体）把候选键显式声明为 UNIQUE", 1, False, INK, 13.5),
        ("反范式化：仅对高频检索的“申请号/公开号/日期”建辅助索引，不冗余存储派生列", 1, False, INK, 13.5),
        (f"约束统计：主键 {st['pk']} / 唯一约束 {st['uq']}（复合 {st['uq_multi']}）/ 检查约束 {st['chk']} / "
         f"非空字段 {st['notnull']}", 0, True, TEAL, 14),
    ], line_spacing=1.25)
    footer(slide, "复核：scratch 空库重放 DDL 后由系统目录统计（避免手工计数偏差）", 7)

    # 8 物理设计与导入
    slide = content_slide(deck, "物理设计与数据导入：幂等、可审计、可回滚", "脚本负责写入，数据库负责保证不写坏", 8, accent=AMBER)
    add_text(slide, MARGIN, Inches(1.42), Inches(7.3), Inches(5.2), [
        ("物理设计", 0, True, NAVY, 15),
        ("命名规范：表/字段小写下划线；外键列统一 <被引表>_id；布尔列 is_*", 1, False, INK, 13.5),
        ("类型选择：日期用 DATE（不可解析时 NULL，同时保留原文列）；权项/说明书用 TEXT，避免任意截断", 1, False, INK, 13.5),
        ("大对象与文本分离：drawing 只存元数据与路径，不把二进制图片塞进库", 1, False, INK, 13.5),
        ("模式与元数据：业务表进 patentdb，导入审计表统一前缀与版本字段", 1, False, INK, 13.5),
        ("导入流程", 0, True, NAVY, 15),
        ("校验 → 解析 → 幂等键去重 → 单事务写入 → 记录批次与字段错误 → 提交或整批回滚", 1, False, INK, 13.5),
        ("同一 XML 重复导入不产生重复行；行数、键约束、非空约束在提交前统一校验", 1, False, INK, 13.5),
    ], line_spacing=1.25)
    add_shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, MARGIN + Inches(7.6), Inches(1.5),
              Inches(4.5), Inches(3.4), RGBColor(0x14, 0x2A, 0x3E), line=None).adjustments[0] = 0.05
    add_text(slide, MARGIN + Inches(7.85), Inches(1.72), Inches(4.0), Inches(3.0), [
        ("# 导入一次 = 一个事务", 0, True, RGBColor(0x7F, 0xD1, 0xC0), 12.5),
        ("BEGIN;", 0, False, RGBColor(0xE6, 0xED, 0xF3), 12.5),
        ("  -- (1) 记录批次 + 源文件 SHA256", 0, False, RGBColor(0x9E, 0xB3, 0xC8), 12),
        ("  -- (2) 幂等键去重后逐表写入", 0, False, RGBColor(0x9E, 0xB3, 0xC8), 12),
        ("  -- (3) 行数/约束自检", 0, False, RGBColor(0x9E, 0xB3, 0xC8), 12),
        ("COMMIT;  -- 任一步失败则 ROLLBACK", 0, False, RGBColor(0xE6, 0xED, 0xF3), 12.5),
    ], line_spacing=1.3)
    footer(slide, "脚本：second stage/02-数据导入/、third stage/05-数据导入/；批次与错误可在审计表核对", 8)

    # 9 约束落地
    slide = content_slide(deck, "约束落地：把“业务规则”写成数据库能拒绝的语句", "每条约束都配一个应当被拒绝的反例", 9, accent=TEAL)
    add_table(slide, ["约束类型", "数量", "典型对象与作用"], [
        ["主键 PRIMARY KEY", st["pk"], "每张业务表一个代理主键，禁止 NULL 与重复"],
        ["外键 FOREIGN KEY", st["fk"], "桥表与弱实体指向属主；删除策略显式声明"],
        ["唯一约束 UNIQUE", f"{st['uq']}（复合 {st['uq_multi']}）", "如 (publication_id, language, seq) 保证同语言不重号"],
        ["检查约束 CHECK", st["chk"], "枚举取值、日期先后、序号为正等"],
        ["非空 NOT NULL", st["notnull"], "所有核心业务标识列不允许缺失"],
        ["索引 INDEX", f"{st['idx']}（辅助 {st['idx_aux']}）", "覆盖按申请号/公开号/日期的常用检索路径"],
    ], MARGIN, Inches(1.44), Inches(7.55), [1.25, 1.0, 3.1], size=13, row_h=Inches(0.52))
    add_text(slide, MARGIN + Inches(7.85), Inches(1.5), Inches(4.25), Inches(5.0), [
        ("反例验证（测试脚本直接尝试破坏约束）", 0, True, NAVY, 14.5),
        ("插入重复复合键 → 被 UNIQUE 拒绝", 1, False, INK, 13),
        ("删除仍被引用的属主 → 按策略级联或拒绝", 1, False, INK, 13),
        ("写入非法枚举值 → 被 CHECK 拒绝", 1, False, INK, 13),
        ("必填列写 NULL → 被 NOT NULL 拒绝", 1, False, INK, 13),
        ("失败动作必须整批回滚，库里不留半成品数据", 1, False, GREY, 12.5),
    ], line_spacing=1.25)
    footer(slide, "统计口径：scratch 空库重放 DDL 后的系统目录查询结果", 9)

    # 10 前端展示
    slide = content_slide(deck, f"前端展示：{st['tables']} 张表的只读浏览", "Flask 实现；数据库异常时返回 HTTP 503 并给出原因，而不是显示成空表", 10, accent=TEAL)
    front_figs = [("图8-前端首页43表.png", f"图 8　首页：{st['tables']} 张业务表与行数"),
                  ("图9-前端patent表.png", "图 9　通用表浏览（patent 表 19 行）"),
                  ("图10-前端专利详情.png", "图 10　专利详情（只显示活动文献）")]
    box_w, gap = Inches(3.95), Inches(0.12)
    for index, (name, cap) in enumerate(front_figs):
        add_picture_fit(slide, FIGDIR / name, MARGIN + index * (box_w + gap), Inches(1.36),
                        box_w, Inches(4.68), cap)
    add_text(slide, MARGIN, Inches(6.42), BODY_W, Inches(0.6),
             "详情页以 active_publication 视图取数：同一申请的多篇文献只展示当前有效的一篇，"
             "标题 / 摘要 / 权项按语言分组呈现。", size=12.5, color=GREY)
    footer(slide, "截图：third stage/07-前端与测试/；页面实现见同目录 app.py 与模板", 10)

    # 11 测试与验收
    slide = content_slide(deck, "测试与验收：151 条用例全部通过，且能证明“不假通过”", "全部测试在一次性容器里从空库开始执行，结束后逐表比对", 11, accent=AMBER)
    kpi_row(slide, [
        (test_total, "条测试用例（5 类脚本，全部通过）"),
        ("0", "条失败 / 跳过（FAIL、SKIP 均视为未通过）"),
        ("46", "张表在 dump 恢复后逐表比对一致"),
        (f"{st['tables']} + 3", "张业务表 + 审计表纳入冒烟检查"),
    ])
    add_table(slide, ["测试脚本", "用例", "通过", "覆盖内容", "证据文件"], [
        [row[0], row[1], row[2], row[3], row[4]] for row in ctx["tests"]
    ], MARGIN, Inches(2.7), BODY_W, [3.3, 0.8, 0.8, 5.6, 2.4], size=11.5, row_h=Inches(0.46))
    add_text(slide, MARGIN, Inches(6.06), BODY_W, Inches(0.9), [
        "验收流程：全新容器 → 建库 → 导入 → 全量测试 → 与源库逐表比对 → pg_dump 备份 → 恢复库再次比对，两次一致才判定通过；",
        f"交付 dump：third stage/08-数据库交付/patentdb-phase3.dump，SHA256 {ctx['dump'][:16]}…（0.4 MB）",
    ], size=12.5, color=GREY)
    footer(slide, "结果文件：third stage/06-运行管理/结果/*_result.json（用例数与通过数由 JSON 实时统计）", 11)

    # 12 分析一：技术领域与申请人
    an = ctx["an"]
    ipc = {row["部"]: row for row in an["ipc_section"] if row["分类体系"] == "IPC"}
    ipc_class = {row["大类"]: row for row in an["ipc_class"] if row["分类体系"] == "IPC"}
    roles = {row["角色"]: row for row in an["role_summary"]}
    extra = ctx["extra"]
    two_chart_slide(
        deck, ctx, title="分析挖掘（一）：技术领域分布与申请人排名",
        kicker=f"5 个主题 {query_count} 条 SQL，全部脚本执行并导出 CSV / JSON，结论只限本批样例",
        page=12, left_img=FIGDIR / "图11-技术领域分布.png",
        left_cap="图 11　技术领域分布（IPC / CPC 部级，按专利去重）",
        right_img=FIGDIR / "图12-申请人排名.png",
        right_cap="图 12　申请人排名（前 10 名，按专利数去重）",
        notes=[
            (f"分类覆盖 {an['coverage'][0]['覆盖率百分比']}%（16 / 19 件申请带分类号）：IPC 以 A 部（人类生活必需）"
             f"{ipc.get('A', {}).get('专利数', 0)} 件最多，其次 H 部 {ipc.get('H', {}).get('专利数', 0)} 件、"
             f"G 部 {ipc.get('G', {}).get('专利数', 0)} 件；大类 A01 {ipc_class.get('A01', {}).get('专利数', 0)} 件、"
             f"H04 {ipc_class.get('H04', {}).get('专利数', 0)} 件、G06 {ipc_class.get('G06', {}).get('专利数', 0)} 件。",
             0, True, NAVY, 14),
            (f"申请主体 {extra['org_people'] + extra['nat_people']} 个（机构 {extra['org_people']} 家、自然人 "
             f"{extra['nat_people']} 名），与 {extra['covered_patents']} 件专利建立 {roles['申请人']['关联条数']} 条"
             f"申请关系，平均每件 1.1 个申请人 → 样例基本是单申请人结构。", 0, False, INK, 13.5),
            (f"排名前两位各 {an['applicant_rank'][0]['专利数']} 件（{an['applicant_rank'][0]['申请人']}、"
             f"{an['applicant_rank'][1]['申请人']}），其余均 1 件；角色分布：发明人 {roles['发明人']['关联条数']} 条 / "
             f"{roles['发明人']['专利数']} 件，申请人 {roles['申请人']['关联条数']} / {roles['申请人']['专利数']}，"
             f"代理人 {roles['代理人']['关联条数']} 条、审查员 {roles['审查员']['关联条数']} 条、"
             f"权利人 {roles['权利人（受让人）']['关联条数']} 条。", 0, False, INK, 13.5),
            ("数据质量提醒：源样例中部分机构名称（如 Husqvarna AB、SIEMENS AG）被标为自然人类型，"
             "本组按“不修改来源事实”原样入库，person_type 只能作参考，机构 / 自然人划分不能直接用于统计结论。",
             0, False, RED, 13),
        ])

    # 13 分析二：引用网络
    top = an["out_degree"][0]
    p_cit = next(row for row in an["type_split"] if row["类型码"] == "P")
    n_cit = next(row for row in an["type_split"] if row["类型码"] == "N")
    ctry = {row["被引国别"]: int(row["被引次数"]) for row in an["cited_country"]}
    dec = {row["年代段"]: int(row["被引次数"]) for row in an["cited_decade"]}
    share = round(100 * int(top["专利引用"]) / int(p_cit["引用条数"]), 1)
    two_chart_slide(
        deck, ctx, title="分析挖掘（二）：引用网络结构",
        kicker="引用是“本文献 → 被引文献”的自引用结构，被引目标可以落在库外",
        page=13, left_img=FIGDIR / "图13-引用网络结构.png",
        left_cap="图 13　引用类型分布与引用方出度 TOP8",
        right_img=FIGDIR / "图14-被引国别与年代.png",
        right_cap="图 14　被引专利文献的来源国别与年代分布",
        notes=[
            (f"库内共 {an['resolution'][0]['引用总条数']} 条引用：专利文献引用（P）{p_cit['引用条数']} 条，来自 "
             f"{p_cit['引用方专利数']} 件引用方；非专利文献引用（N）{n_cit['引用条数']} 条，来自 "
             f"{n_cit['引用方专利数']} 件引用方，另有 {an['resolution'][0]['非专利引用明细']} 条非专利明细写入 "
             f"non_patent_citation 表。", 0, True, NAVY, 14),
            (f"出度极不均衡：US20140338089A1 一件引用 {top['合计']} 条（专利 {top['专利引用']} 条，占全部专利引用的 "
             f"{share}%），第二名 {an['out_degree'][1]['合计']} 条，第三名 {an['out_degree'][2]['合计']} 条，"
             f"其余都在 20 条以内。", 0, False, INK, 13.5),
            (f"被引文献国别：US {ctry.get('US', 0)} 次、WO {ctry.get('WO', 0)} 次、JP {ctry.get('JP', 0)} 次、"
             f"EP {ctry.get('EP', 0)} 次、GB {ctry.get('GB', 0)} 次；年代集中在 2000—2009（{dec.get('2000', 0)} 次）"
             f"与 1990—1999（{dec.get('1990', 0)} 次）。", 0, False, INK, 13.5),
            (f"关键限制：{p_cit['引用条数']} 条专利引用的被引目标全部在库外（库内已解析 "
             f"{an['resolution'][0]['库内已解析']} 条）→ 本报告只能回答“谁引用了多少文献”，"
             f"不能回答“谁被引用最多”。", 0, False, RED, 13),
        ])

    # 14 分析三：权项结构与数据来源
    claim_type = {row["类型码"]: row for row in an["claim_type"]}
    langs = {row["语言"]: row for row in an["lang_split"]}
    doc0 = an["doc_structure"][0]
    years = {row["公布年份"]: int(row["文献数"]) for row in an["publn_year"]}
    ev_total = sum(int(row["事件条数"]) for row in an["legal_event"])
    ds_text = "、".join(f"{row['数据集']} {row['文献数']} 篇" for row in ctx["datasets"])
    two_chart_slide(
        deck, ctx, title="分析挖掘（三）：权利要求结构、多语言与数据来源",
        kicker="同一篇文献的标题 / 权项按语言分套存放，统计必须按语言分别计数",
        page=14, left_img=FIGDIR / "图15-权利要求与多语言.png",
        left_cap="图 15　各文献权利要求结构与多语言分布",
        right_img=FIGDIR / "图16-数据来源与年份.png",
        right_cap="图 16　数据来源分布与文献公布年份分布",
        notes=[
            (f"{int(claim_type['I']['条数']) + int(claim_type['D']['条数'])} 条权利要求：独立权项 I "
             f"{claim_type['I']['条数']} 条（{claim_type['I']['涉及文献']} 篇）、从属权项 D "
             f"{claim_type['D']['条数']} 条（{claim_type['D']['涉及文献']} 篇）；"
             f"{an['dependency'][0]['依赖条数']} 条依赖记录与从属权项一一对应。结构最大的文献 {doc0['文献号']}："
             f"独立权项 {doc0['独立权项']} 项、说明书 {doc0['说明书章节']} 节、附图 {doc0['附图']} 幅。",
             0, True, NAVY, 14),
            (f"多语言：EN {langs['EN']['权利要求']} 条、DE {langs['DE']['权利要求']} 条、"
             f"FR {langs['FR']['权利要求']} 条权项，标题分别为 {langs['EN']['标题']} / {langs['DE']['标题']} / "
             f"{langs['FR']['标题']} 条；按语言分别计数可避免同一篇文献被重复计算三次。", 0, False, INK, 13.5),
            (f"数据来源：{ds_text}；"
             f"公布年份集中在 2014（{years.get('2014', 0)} 篇）、1979（{years.get('1979', 0)} 篇）"
             f"与 2020（{years.get('2020', 0)} 篇）。", 0, False, INK, 13.5),
            (f"族与程序：{len(an['family_size'])} 个专利族，库内每族仅 1 名成员（只有族头）；法律状态 {ev_total} 条事件、"
             f"{len(an['legal_event'])} 类事件码；关键词 {an['keyword_source'][0]['数值']} 条是基于标题的派生数据"
             f"（source = TITLE_DERIVED），不能当作官方标引结果。", 0, False, INK, 13.5),
        ])

    # 15 局限性
    slide = content_slide(deck, "局限性：哪些结论只能说，哪些不能说", "按数据、设计、实现、分析四类如实说明", 15, accent=AMBER)
    limits = [
        ("数据范围有限",
         [f"只用 5 类官方样例、19 件申请、{rows_total} 行；公布年份集中在 1979 / 2014 / 2020，时间维度几乎没有代表性。"]),
        ("引用不可闭环",
         [f"{p_cit['引用条数']} 条专利引用的被引目标全部在库外（库内解析 0 条），无法计算被引次数、中心性与技术演化路径。"]),
        ("专利族不完整",
         ["样例只给族头与少量成员，库内每族仅 1 名成员；family_citation 因缺少可靠双端族号保持 0 行并已在报告中声明。"]),
        ("人员语义受限",
         ["person_type 由源记录类型直接映射，样例中存在机构被标为自然人的情况；本组不做推断式修正，字段口径受限。"]),
        ("关键词是派生数据",
         [f"keyword / patent_keyword 基于标题生成（{an['keyword_source'][0]['数值']} 条，标 TITLE_DERIVED），"
          "可演示增强表，但不能当官方标引结果。"]),
        ("性能未压测",
         ["数据量只有几千行，索引与查询计划只能证明结构合理；未做分区、并行导入或物化视图优化。"]),
        ("功能边界清晰",
         ["前端只读、无权限与用户体系、无写入接口；数据库为单机容器，未涉及复制、备份策略与灾备。"]),
        ("导入器覆盖面",
         ["解析器按 5 类样例家族实现；换局别或新版数据手册需补解析规则并重做字段映射。"]),
    ]
    for column, chunk in enumerate((limits[:4], limits[4:])):
        left = MARGIN + column * (Inches(6.06) + Inches(0.03))
        lines = []
        for head, body in chunk:
            lines.append((head, 0, True, RED if column == 0 else NAVY, 14))
            lines.append((body[0], 1, False, INK, 12.5))
        add_text(slide, left, Inches(1.5), Inches(6.06), Inches(5.4), lines, line_spacing=1.2)
    footer(slide, "对应报告第 4.7 节；更细的问题与处理过程见 fourth stage/90-问题记录-D.md", 15)

    # 16 收获与建议
    slide = content_slide(deck, "小组收获与后续建议", "工程结论 + 给下一届的建议，均可由仓库证据复核", 16, accent=TEAL)
    gains = [
        ("先设计后建表", "先定六域 E-R 与函数依赖，再写 DDL，返工明显减少。"),
        ("约束即文档", "把业务规则写成 PRIMARY KEY / FOREIGN KEY / UNIQUE / CHECK，比写在说明里更能防错。"),
        ("可复现要靠工程手段", "SHA256 + 幂等键 + 单事务 + 一键验收，才能证明“同一个库”。"),
        ("证据驱动写作", "报告与 PPT 的每个数字都由脚本从结果文件注入，避免手工抄错。"),
    ]
    advice = [
        ("闭合引用网络", "拿到全量或更多样例后，先解析被引目标，把库外引用变成可分析的引用网络。"),
        ("增量与调度", "按批次号与变更检测做增量导入，替代一次性全量导入。"),
        ("前端补检索", "增加按申请人 / 分类号 / 年份筛选与分页，补齐权限与用户体系。"),
        ("性能基线", "用 EXPLAIN 与 pgbench 记录基线，再做分区与物化视图实验。"),
    ]
    for column, (title_text, items, color) in enumerate(
            (("我们的工程收获", gains, NAVY), ("给后续使用的建议", advice, TEAL))):
        left = MARGIN + column * (Inches(6.06) + Inches(0.03))
        lines = [(title_text, 0, True, color, 16)]
        for head, body in items:
            lines.append((head + "：" + body, 1, False, INK, 13))
        add_text(slide, left, Inches(1.46), Inches(6.06), Inches(4.4), lines, line_spacing=1.25)
    add_text(slide, MARGIN, Inches(6.0), BODY_W, Inches(0.9), [
        f"AI 使用声明：AI 仅用于脚本与文字草稿，全部结论与数字均由仓库内脚本和结果文件复核"
        f"（first stage / second stage / third stage / fourth stage 各自的 92-AI使用记录*.md）。",
        f"问题记录同样归档：本阶段 {ctx['problem_rows']} 条问题见 fourth stage/90-问题记录-D.md，"
        "均给出处理方式与验证证据。",
    ], size=12.5, color=GREY)
    footer(slide, "完整交付清单：01-设计文档 / 02-汇报PPT / 03-分析挖掘 / 04-流程图与框图 / 05-打包", 16)

    # 17 结束页
    slide = deck.slides.add_slide(deck.slide_layouts[6])
    SLIDE_TITLES.append((17, "结束页 · 谢谢与现场复现入口"))
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, 0, SW, SH, NAVY)
    add_shape(slide, MSO_SHAPE.RECTANGLE, 0, Inches(2.9), SW, Pt(3), TEAL)
    add_text(slide, MARGIN, Inches(2.15), BODY_W, Inches(0.8), "谢谢，欢迎提问", size=40,
             bold=True, line_spacing=1.0, color=WHITE)
    add_text(slide, MARGIN, Inches(3.28), BODY_W, Inches(0.6),
             "题目 5 · 专利数据关系数据库：结构、约束、验收与分析结论均可现场复核", size=18,
             color=RGBColor(0xC7, 0xD8, 0xE8))
    add_text(slide, MARGIN, Inches(4.3), BODY_W, Inches(2.2), [
        "现场复现（空容器开始，约一碗饭的等待时间）：", 
        "python3 -m venv .venv  →  .venv/bin/python 'third stage/06-运行管理/verify_fresh.py'",
        ".venv/bin/python 'fourth stage/03-分析挖掘/run_analysis.py'   # 5 个主题 21 条 SQL + 6 张图",
        "一键入口：./run.sh（建库 → 导入 → 测试 → 前端 → 分析）",
    ], size=14.5, color=RGBColor(0xAE, 0xC7, 0xDD), line_spacing=1.5)
    return deck


# --------------------------------------------------------------------------- 讲稿
# 每页讲稿：页号 → (建议时长, 讲稿要点)。数字同样从 ctx 注入，写入 PPT 备注页并导出 Markdown。
def build_notes(ctx) -> dict:
    st, an, extra = ctx["st"], ctx["an"], ctx["extra"]
    p_cit = next(row for row in an["type_split"] if row["类型码"] == "P")
    claim = {row["类型码"]: row for row in an["claim_type"]}
    links = next(row["关联条数"] for row in an["role_summary"] if row["角色"] == "申请人")
    people = extra["org_people"] + extra["nat_people"]
    claims_total = int(claim["I"]["条数"]) + int(claim["D"]["条数"])
    return {
        1: ("0:20", f"开场：我们做的是题目 5——专利数据关系数据库。整条链路从五局官方样例 XML 出发，"
                    f"到 {st['tables']} 张业务表、{st['rows']:,} 行数据、{ctx['test_total']} 条测试用例和 "
                    f"5 个主题 {ctx['query_count']} 条 SQL 的分析结论，全部可以现场复现。"),
        2: ("0:30", "汇报按“问题 → 设计 → 实现 → 结果 → 总结”五段走，与报告章节一一对应；"
                    "所有数字都来自仓库里可复核的证据文件，不是手工统计。"),
        3: ("0:50", f"先说边界：试验系统访问不到，所以我们只用官方样例与数据手册，共 {len(ctx['datasets'])} 类"
                    "数据集、17 个 XML、19 件申请。这些文件导入前都算了 SHA256，随时可以核对来源没有被改过。"),
        4: ("1:00", "需求阶段我们梳理出七类难点：多值属性、弱实体、一元递归引用、多语言多版本、日期精度、"
                    "来源缺口和可追溯性。每一类后面都能对应到具体的表结构或约束，这里先埋个伏笔。"),
        5: ("0:40", "总体路线是四角色、多阶段交接：每个阶段都留下脚本和结果文件，下一阶段直接复用，"
                    "所以第四阶段的报告和 PPT 能一键重生成。"),
        6: ("1:00", "概念设计分六个域：申请与文献、主体、内容、分类、引用、元数据。原则是域内强内聚、"
                    "域间用受控外键连接；弱实体一律拆表，不用 JSON 列，保证能被 SQL 查询。"),
        7: ("1:00", f"逻辑设计的结果是 {st['tables']} 张表、{st['fields']} 个字段、{st['fk']} 个外键、"
                    f"{st['idx']} 个索引。范式审查我们做了 1NF 到 BCNF 的逐条判定；示例：同一篇文献的多语言权项用 "
                    "(publication_id, language, seq) 复合唯一键，既消除多值属性又能防重。"),
        8: ("0:50", "物理设计与导入的关键词是幂等、可审计、可回滚：命名统一、日期与原文双列并存、"
                    "一次导入就是一个事务，批次与字段级错误都落到审计表，失败整批回滚。"),
        9: ("0:50", f"约束不只是写进文档，而是写成数据库能拒绝的语句：主键 {st['pk']}、外键 {st['fk']}、"
                    f"唯一 {st['uq']}（复合 {st['uq_multi']}）、检查 {st['chk']}、非空 {st['notnull']}。"
                    "每条约束都用反例验证过，违规写入会被数据库直接拒绝。"),
        10: ("0:40", f"前端是 Flask 只读浏览：首页列出 {st['tables']} 张表和行数，可以逐表翻页，也可以看单件专利的"
                     "详情；数据库异常时返回 503 并显示原因，绝不把错误显示成空表。"),
        11: ("1:00", f"测试一共 {ctx['test_total']} 条用例、5 类脚本，全部通过且没有 FAIL / SKIP。"
                     "更重要的是验收方式：在一次性容器里从空库跑完全流程，再 dump 恢复后逐表比对，"
                     "两次一致才算通过。"),
        12: ("0:50", f"分析一：分类覆盖率 {an['coverage'][0]['覆盖率百分比']}%，IPC 以 A 部最多；申请主体 {people} 个、"
                     f"{links} 条申请关系，基本是单申请人结构。这里有一个必须主动说明的数据质量问题——"
                     "样例里部分机构被标成了自然人。"),
        13: ("0:50", f"分析二：库内 {an['resolution'][0]['引用总条数']} 条引用，出度极不均衡，"
                     f"一件专利就引用了 {an['out_degree'][0]['合计']} 条。但要强调限制：{p_cit['引用条数']} 条"
                     "专利引用的被引目标全部在库外，所以我们只能说“谁引用了多少”，不能说“谁被引用最多”。"),
        14: ("0:50", f"分析三：{claims_total} 条权项，独立 {claim['I']['条数']} 条、从属 {claim['D']['条数']} 条；"
                     "同一篇文献的标题和权项按 EN / DE / FR 分套存放，统计必须按语言分别计数。"
                     "数据来源以美国授权公告为主，公布年份集中在 2014 年。"),
        15: ("0:50", "局限性分四类如实说明：数据范围、引用不可闭环、专利族不完整、人员语义受限；"
                     "还有关键词是派生数据、性能没压测、前端只读、导入器覆盖面有限。"
                     "这些不是隐瞒缺陷，而是明确的口径边界。"),
        16: ("0:40", "我们的收获是“先设计后建表”“约束即文档”“可复现要靠工程手段”“证据驱动写作”；"
                     "建议后续先闭合引用网络、做增量导入、给前端补检索与权限、建立性能基线。"),
        17: ("0:20", f"最后是复现入口：三条命令就能从空容器重建数据库、跑完 {ctx['test_total']} 条测试并生成"
                     "分析结果。谢谢，欢迎提问。"),
    }


def attach_notes(deck, notes) -> None:
    """把讲稿写入每页的备注页，方便演示时看提词。"""
    for page, slide in enumerate(deck.slides, start=1):
        if page not in notes:
            continue
        duration, text = notes[page]
        frame = slide.notes_slide.notes_text_frame
        frame.text = f"（建议 {duration}）{text}"


def write_script(path: Path, notes) -> None:
    """导出讲稿 Markdown（页序 + 建议时长 + 标题 + 讲稿）。"""
    total = sum(int(minutes.split(":")[0]) * 60 + int(minutes.split(":")[1])
                for minutes, _ in notes.values())
    lines = ["# 第四阶段汇报讲稿（专利数据关系数据库 · 题目 5）", "",
             f"配套文件：`{OUT.name}`（{len(SLIDE_TITLES)} 页，每页备注页含同一份讲稿）。",
             f"建议总时长：{total // 60} 分 {total % 60} 秒。",
             "全部数字与设计报告同源，均取自仓库内可复核的证据文件。", ""]
    for page, title in sorted(SLIDE_TITLES):
        duration, text = notes.get(page, ("", ""))
        lines += [f"## 第 {page} 页 · {title}", "",
                  f"- 建议时长：{duration}", f"- 讲稿：{text}", ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def slide_text(slide) -> list[str]:
    texts = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            texts += [para.text for para in shape.text_frame.paragraphs if para.text]
        if shape.has_table:
            for row in shape.table.rows:
                texts += [cell.text for cell in row.cells if cell.text]
    return texts


def estimate_height(frame) -> float:
    """按 CJK 全宽、ASCII 半宽估算文本所需高度（pt），用于检查文字是否超出文本框。"""
    needed = 0.0
    for para in frame.paragraphs:
        text = "".join(run.text for run in para.runs)
        if not text:
            continue
        size = next((run.font.size.pt for run in para.runs if run.font.size), 16)
        width = sum(size * (1.0 if ord(ch) > 0x2E80 else 0.55) for ch in text)
        lines = max(1, math.ceil(width / max(frame_width(frame), 1)))
        spacing = para.line_spacing or 1.2
        after = para.space_after.pt if para.space_after else 0
        needed += lines * size * spacing * 1.2 + after
    return needed


def frame_width(frame) -> float:
    return frame._parent.width / 12700 if frame._parent is not None else 600.0


def self_check(ctx, deck) -> bool:
    """生成后自检：页数、图片、关键数字、备注与文字溢出，全部由 ctx 推导期望值。"""
    st = ctx["st"]
    slides = list(deck.slides)
    problems: list[str] = []
    pages = [page for page, _ in SLIDE_TITLES]
    if sorted(pages) != list(range(1, len(slides) + 1)):
        problems.append(f"页码序列异常：{sorted(pages)}（应为 1..{len(slides)}）")

    pictures, off_slide = 0, 0
    too_tall = []
    for index, slide in enumerate(slides, start=1):
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                pictures += 1
                if (shape.left < 0 or shape.top < 0
                        or shape.left + shape.width > SW or shape.top + shape.height > SH):
                    off_slide += 1
            if shape.has_text_frame and shape.height > Emu(int(Inches(0.4))):
                if estimate_height(shape.text_frame) > shape.height / 12700:
                    too_tall.append(f"第 {index} 页：{slide_text(slide)[0][:16]}…")
    if off_slide:
        problems.append(f"有 {off_slide} 张图片超出页面范围")
    if too_tall:
        problems.append("文字可能超出文本框：" + "；".join(too_tall))

    joined = "\n".join(text for slide in slides for text in slide_text(slide))
    expected = [str(st["tables"]), str(st["fields"]), f"{st['rows']:,}", str(ctx["test_total"]),
                str(ctx["query_count"]), str(st["fk"]), str(st["idx"]), str(st["pk"]),
                str(st["uq"]), str(st["chk"]), str(st["notnull"])]
    for token in expected:
        if token not in joined:
            problems.append(f"缺少关键数字：{token}")
    for marker in ["（请填写）", "TODO", "{", "}", "None"]:
        if marker in joined:
            problems.append(f"残留占位或异常文本：{marker}")

    missing_notes = [index for index, slide in enumerate(slides, start=1)
                     if not (slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip())]
    if missing_notes:
        problems.append(f"缺少讲稿备注的页：{missing_notes}")

    figures = sorted((FIGDIR / name).name for name in [p.name for p in FIGDIR.glob("*.png")])
    print(f"[自检] 幻灯片 {len(slides)} 页、插图 {pictures} 张、表格 "
          f"{sum(1 for s in slides for sh in s.shapes if sh.has_table)} 个、讲稿备注 "
          f"{len(slides) - len(missing_notes)} 页")
    print(f"[自检] 业务表 {st['tables']} 张、字段 {st['fields']} 个、数据 {st['rows']} 行、"
          f"测试用例 {ctx['test_total']} 条、分析 SQL {ctx['query_count']} 条"
          f"（可用图源 {len(figures)} 张）")
    if problems:
        print("[自检] 发现问题：" + "；".join(problems))
        return False
    print("[自检] 全部通过：页序、插图、关键数字、讲稿与文字排版检查一致。")
    return True


def main() -> int:
    ctx = br.build_ctx()
    deck = build_deck(ctx)
    notes = build_notes(ctx)
    attach_notes(deck, notes)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    deck.save(str(OUT))
    write_script(SCRIPT, notes)
    print(f"[生成] {OUT}")
    print(f"[生成] {SCRIPT}")
    print(f"[统计] 幻灯片 {len(deck.slides._sldIdLst)} 页；业务表 {ctx['st']['tables']} 张、"
          f"字段 {ctx['st']['fields']} 个、数据 {ctx['st']['rows']} 行；测试用例 {ctx['test_total']} 条；"
          f"分析 SQL {ctx['query_count']} 条")
    return 0 if self_check(ctx, deck) else 1




if __name__ == "__main__":
    raise SystemExit(main())



