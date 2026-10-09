#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""报告模板排版工具：在《报告模板.docx》的样式与编号基础上生成正文内容。

模板事实（由报告模板.docx 解析得到）：
  * 页面 A4 纵向，左右页边距 1.25 英寸（3.17cm），上下 1 英寸（2.54cm）；
  * 正文样式 Normal + 宋体小四（12pt），无自定义 Heading 样式；
  * 五个一级标题使用样式 Normal + numPr(numId=5, ilvl=0)，编号格式为 japaneseCounting「一、」；
  * 封面页包含「《数据库实践》课程报告/小组序号/小组题目/年月日」及一个校徽图片；
  * 正文含 5 行 4 列 Table Grid 分工表（学号/姓名/角色/任务分工）。
因此本模块不新建样式，只复用模板样式并显式设置中英文字体，保证与模板一致。
"""
from __future__ import annotations

import copy
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.table import Table
from docx.text.paragraph import Paragraph

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "报告模板.docx"

SONG, HEI, MONO = "宋体", "黑体", "Consolas"


def open_template() -> Document:
    if not TEMPLATE.exists():
        raise SystemExit(f"找不到报告模板：{TEMPLATE}")
    return Document(str(TEMPLATE))


def set_run_font(run, size=12, bold=False, ea=SONG, ascii_font=SONG, color=None, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = ascii_font
    rPr = run._r.get_or_add_rPr()
    fonts = rPr.get_or_add_rFonts()
    fonts.set(qn("w:eastAsia"), ea)
    fonts.set(qn("w:ascii"), ascii_font)
    fonts.set(qn("w:hAnsi"), ascii_font)
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    return run


def _style_paragraph(p: Paragraph, *, size, bold, ea, ascii_font, align, indent_chars,
                     space_before, space_after, line_spacing, color=None):
    if align is not None:
        p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if line_spacing:
        pf.line_spacing = line_spacing
    if indent_chars:
        ind = p._p.get_or_add_pPr().get_or_add_ind()
        ind.set(qn("w:firstLineChars"), str(int(indent_chars * 100)))
    for run in p.runs:
        set_run_font(run, size=size, bold=bold, ea=ea, ascii_font=ascii_font, color=color)
    return p


def new_para(doc: Document, text="", *, size=12, bold=False, ea=SONG, ascii_font=SONG,
             align=None, indent_chars=2, space_before=0, space_after=0, line_spacing=1.5,
             color=None):
    """新建正文段落（默认宋体小四、首行缩进 2 字符、1.5 倍行距）。"""
    p = doc.add_paragraph()
    if text:
        p.add_run(text)
    return _style_paragraph(p, size=size, bold=bold, ea=ea, ascii_font=ascii_font, align=align,
                            indent_chars=indent_chars, space_before=space_before,
                            space_after=space_after, line_spacing=line_spacing, color=color)


def new_heading(doc: Document, text, level, proto_pPr=None, *, number=None):
    """二级/三级标题：黑体加粗，手动编号（模板只定义了五个一级标题的自动编号）。"""
    size = {1: 16, 2: 14, 3: 12}.get(level, 12)
    label = f"{number} {text}" if number else text
    p = doc.add_paragraph()
    if proto_pPr is not None:
        p._p.insert(0, copy.deepcopy(proto_pPr))
    p.add_run(label)
    return _style_paragraph(p, size=size, bold=(level == 1), ea=HEI, ascii_font=HEI,
                            align=None, indent_chars=0, space_before=8 if level > 1 else 10,
                            space_after=4, line_spacing=1.4)


def numbered_heading(doc: Document, text, proto_pPr):
    """五个一级标题：完全沿用模板的 Normal + numId=5 编号与黑体三号加粗格式。"""
    p = doc.add_paragraph()
    p._p.insert(0, copy.deepcopy(proto_pPr))
    p.add_run(text)
    return _style_paragraph(p, size=16, bold=True, ea=HEI, ascii_font=HEI, align=None,
                            indent_chars=0, space_before=12, space_after=6, line_spacing=1.4)


def new_bullet(doc: Document, text, *, size=12, indent_level=1):
    p = doc.add_paragraph()
    p.add_run(("　" * indent_level) + "· " + text)
    return _style_paragraph(p, size=size, bold=False, ea=SONG, ascii_font=SONG, align=None,
                            indent_chars=0, space_before=0, space_after=0, line_spacing=1.45)


def new_code(doc: Document, lines):
    """伪代码/命令块：等宽字体、单倍行距、浅灰底纹。"""
    p = doc.add_paragraph()
    p.add_run("\n".join(lines))
    _style_paragraph(p, size=10, bold=False, ea=SONG, ascii_font=MONO, align=None,
                     indent_chars=0, space_before=4, space_after=4, line_spacing=1.15)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "F4F6F8")
    p._p.get_or_add_pPr().append(shd)
    return p


def new_caption(doc: Document, text, *, above=False):
    p = doc.add_paragraph()
    p.add_run(text)
    return _style_paragraph(p, size=10.5, bold=above, ea=HEI if above else SONG,
                            ascii_font=SONG, align=WD_ALIGN_PARAGRAPH.CENTER, indent_chars=0,
                            space_before=4 if above else 2, space_after=2 if above else 8,
                            line_spacing=1.2)


def _shade(cell, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shd)


def new_table(doc: Document, header, rows, widths_cm=None, *, size=10.5,
              header_fill="DCE6F1", center_cols=None):
    """表格：Table Grid 样式，表头黑体加粗并加底纹，正文五号宋体。"""
    center_cols = set(center_cols if center_cols is not None else range(len(header)))
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, text in enumerate(header):
        cell = t.cell(0, j)
        cell.text = ""
        p = cell.paragraphs[0]
        p.add_run(str(text))
        _style_paragraph(p, size=size, bold=True, ea=HEI, ascii_font=HEI,
                         align=WD_ALIGN_PARAGRAPH.CENTER, indent_chars=0, space_before=1,
                         space_after=1, line_spacing=1.15)
        _shade(cell, header_fill)
    for i, row in enumerate(rows, start=1):
        for j, value in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.add_run("" if value is None else str(value))
            _style_paragraph(p, size=size, bold=False, ea=SONG, ascii_font=SONG,
                             align=WD_ALIGN_PARAGRAPH.CENTER if j in center_cols
                             else WD_ALIGN_PARAGRAPH.LEFT,
                             indent_chars=0, space_before=1, space_after=1, line_spacing=1.15)
    if widths_cm:
        for j, width in enumerate(widths_cm):
            if width is None:
                continue
            for r in t.rows:
                r.cells[j].width = Cm(width)
    return t


def new_picture(doc: Document, path, caption="", width_cm=14.0):
    """插入居中图片并附图题（图题在图下方，宋体五号居中）。"""
    doc.add_picture(str(path), width=Cm(width_cm))
    pic_p = doc.paragraphs[-1]
    pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic_p.paragraph_format.space_before = Pt(6)
    pic_p.paragraph_format.space_after = Pt(2)
    elements = [pic_p._p]
    if caption:
        elements.append(new_caption(doc, caption)._p)
    return elements


def append_element(doc: Document, element) -> Paragraph | Table:
    """把刚创建的元素（段落或表格）包装成 python-docx 对象，便于继续搬运。"""
    if element.tag.endswith("}tbl"):
        return Table(element, doc)
    return Paragraph(element, doc)


def move_after(target_element, *elements):
    """把若干元素按顺序移动到 target_element 之后，返回最后一个元素。"""
    cursor = target_element
    for el in elements:
        parent = el.getparent()
        if parent is not None:
            parent.remove(el)
        cursor.addnext(el)
        cursor = el
    return cursor


def drop(element):
    parent = element.getparent()
    if parent is not None:
        parent.remove(element)


def fill_table(table: Table, data, *, size=10.5, header_fill="DCE6F1"):
    """用二维数据填充既有表格（沿用模板自带的 Table Grid 表格）。"""
    for i, row in enumerate(data):
        for j, value in enumerate(row):
            if i >= len(table.rows) or j >= len(table.columns):
                continue
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.add_run("" if value is None else str(value))
            _style_paragraph(p, size=size, bold=(i == 0), ea=HEI if i == 0 else SONG,
                             ascii_font=HEI if i == 0 else SONG,
                             align=WD_ALIGN_PARAGRAPH.CENTER if i == 0 or j < 3
                             else WD_ALIGN_PARAGRAPH.LEFT,
                             indent_chars=0, space_before=1, space_after=1, line_spacing=1.15)
            if i == 0:
                _shade(cell, header_fill)
    return table

