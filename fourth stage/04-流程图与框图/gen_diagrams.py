#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D 角色图表绘制：用例图、总体流程图、系统框图、导入流程图、验收流程图。

运行：python3 "fourth stage/04-流程图与框图/gen_diagrams.py"
输出：同目录下 图A~图E 的 PNG（中文使用微软雅黑/黑体渲染）。
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Ellipse  # noqa: E402

HERE = Path(__file__).resolve().parent
FONT_CANDIDATES = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/simhei.ttf",
    "/mnt/c/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
NAVY, BLUE, TEAL, AMBER, RED, GREY = "#1F3864", "#2F5597", "#4E9F8C", "#E8A33D", "#C0504D", "#6E6E6E"
TINT = {"A": "#EAF1FB", "B": "#E9F5F2", "C": "#FDF3E3", "D": "#F3EEF8"}
EDGE = {"A": BLUE, "B": TEAL, "C": AMBER, "D": "#7B5EA7"}


def setup_font() -> str:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                font_manager.fontManager.addfont(path)
                name = font_manager.FontProperties(fname=path).get_name()
                plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
                plt.rcParams["axes.unicode_minus"] = False
                return name
            except Exception:  # noqa: BLE001
                continue
    plt.rcParams["axes.unicode_minus"] = False
    return "DejaVu Sans"


def canvas(w_in, h_in, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    ax.set_xlim(0, xlim)
    ax.set_ylim(0, ylim)
    ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.02)
    return fig, ax


def rbox(ax, x, y, w, h, text, fc="#FFFFFF", ec=NAVY, fs=10, tc=NAVY, weight="normal", lw=1.3, rad=1.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.3,rounding_size={rad}",
                                linewidth=lw, facecolor=fc, edgecolor=ec, mutation_aspect=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            fontweight=weight, linespacing=1.5)


def diamond(ax, cx, cy, w, h, text, fc="#FFF7E6", ec=AMBER, fs=9.5):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
                         closed=True, facecolor=fc, edgecolor=ec, linewidth=1.3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color="#7A4E00", linespacing=1.4)


def arrow(ax, p1, p2, color=BLUE, lw=1.5, rad=0.0, style="-|>", ls="-", ms=13):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=ms, color=color,
                                 linewidth=lw, linestyle=ls, shrinkA=1, shrinkB=1,
                                 connectionstyle=f"arc3,rad={rad}"))


def title(ax, text, x, y, fs=15):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold", color=NAVY)


def save(fig, name, out=None):
    path = (out or HERE) / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def actor(ax, x, y, label, color=NAVY):
    """画一个火柴人参与者。"""
    ax.add_patch(plt.Circle((x, y + 4.2), 1.5, fill=False, color=color, linewidth=1.4))
    ax.plot([x, x], [y + 2.7, y - 0.6], color=color, linewidth=1.4)
    ax.plot([x - 2.4, x + 2.4], [y + 1.4, y + 1.4], color=color, linewidth=1.4)
    ax.plot([x, x - 1.8], [y - 0.6, y - 3.6], color=color, linewidth=1.4)
    ax.plot([x, x + 1.8], [y - 0.6, y - 3.6], color=color, linewidth=1.4)
    ax.text(x, y - 6.4, label, ha="center", va="top", fontsize=9.5, color=color, linespacing=1.4)


def usecase(ax, cx, cy, text, w=30, h=8.4, fs=9.5):
    ax.add_patch(Ellipse((cx, cy), w, h, facecolor="#EAF1FB", edgecolor=BLUE, linewidth=1.3))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=NAVY, linespacing=1.4)


def diagram_use_case():
    """图A 用例图：三类参与者与六项核心用例。"""
    fig, ax = canvas(13, 7.4, 130, 74)
    title(ax, "图A 系统用例图：专利数据关系数据库的典型使用场景", 65, 71)

    ax.add_patch(FancyBboxPatch((26, 8), 78, 57, boxstyle="round,pad=0.6,rounding_size=2",
                                facecolor="#FCFCFD", edgecolor=GREY, linewidth=1.4, linestyle="--"))
    ax.text(65, 60.5, "专利数据关系数据库系统（patentdb）", ha="center", va="center",
            fontsize=11, fontweight="bold", color=GREY)

    left = [(52, 46, "浏览全部 43 张业务表\n（前端列表 + 行数）"),
            (52, 33, "查看专利/文献详情\n（标题·摘要·权利要求）"),
            (52, 20, "按申请人 / 发明人 检索")]
    right = [(84, 46, "按分类号 / 技术领域 查询"),
             (84, 33, "查看引用关系\n（P 专利 / N 非专利）"),
             (84, 20, "执行统计分析\n并导出图表与结果")]
    for cx, cy, text in left + right:
        usecase(ax, cx, cy, text)

    actor(ax, 12, 44, "数据库使用者\n（浏览器 / 前端）")
    actor(ax, 12, 20, "数据分析人员")
    actor(ax, 118, 32, "数据库管理员\n（DBA / 测试）")

    for cy in (46, 33, 20):
        arrow(ax, (15, 40), (37, cy), color=GREY, lw=1.2, style="-", ms=10)
    for cy in (46, 33, 20):
        arrow(ax, (115, 28), (99, cy), color=GREY, lw=1.2, style="-", ms=10)

    rbox(ax, 30, -6, 70, 9,
         "非功能约束：全表可浏览（43 表列表）· 详情只显示活动文献 · 数据库异常返回 HTTP 503 并明确提示",
         fc="#F5F5F5", ec=GREY, fs=9, tc="#404040")
    return save(fig, "图A-用例图.png")


STAGES = [
    ("①", "官方样例获取与数据手册研读", "A", "17 个基础 XML · 5 类数据集 · 数据手册与 INID 码"),
    ("②", "XML 结构解析与概念设计", "A", "实体清单 · 六域 ER 图 · 基数与参与约束"),
    ("③", "关系模式转换与建表 SQL", "B", "43 业务表 · 345 字段 · 91 外键 · 143 索引"),
    ("④", "解析导入与审计留痕", "B", "3576 行数据 · 幂等 UPSERT · stage2_meta 审计"),
    ("⑤", "验收测试与前端展示", "C", "151 条用例全通过 · 43 表前端列表与详情"),
    ("⑥", "分析挖掘与文档整合", "D", "21 条分析 SQL · 6 张统计图 · 设计文档与 PPT"),
]


def diagram_overall_flow():
    """图B 总体流程图：四个角色、六个阶段的交付链。"""
    fig, ax = canvas(14, 7.8, 150, 78)
    title(ax, "图B 总体流程图：A→B→C→D 四角色六阶段交付链", 75, 74)

    w, h = 36, 16
    xs = [4, 46, 88]
    row1_y, row2_y = 46, 16
    positions = [(xs[0], row1_y), (xs[1], row1_y), (xs[2], row1_y),
                 (xs[2], row2_y), (xs[1], row2_y), (xs[0], row2_y)]

    for (num, name, role, deliverable), (x, y) in zip(STAGES, positions):
        rbox(ax, x, y, w, h, f"{num} {name}", fc=TINT[role], ec=EDGE[role], fs=10.5,
             tc=NAVY, weight="bold")
        rbox(ax, x + w / 2 - 9, y + h + 1.6, 18, 5, f"角色 {role}", fc=EDGE[role], ec=EDGE[role],
             fs=9.5, tc="white", weight="bold", rad=2)
        ax.text(x + w / 2, y - 4.4, deliverable, ha="center", va="center", fontsize=8.6,
                color=GREY, style="italic")

    arrow(ax, (xs[0] + w, row1_y + h / 2), (xs[1], row1_y + h / 2), color=BLUE, lw=1.8)
    arrow(ax, (xs[1] + w, row1_y + h / 2), (xs[2], row1_y + h / 2), color=BLUE, lw=1.8)
    # 阶段③→④ 的纵向交接：走最右侧走廊，避开交付物说明文字
    corridor = xs[2] + w + 6
    arrow(ax, (corridor, row1_y + h / 2), (corridor, row2_y + h / 2), color=TEAL, lw=1.8)
    arrow(ax, (corridor, row2_y + h / 2), (xs[2] + w, row2_y + h / 2), color=TEAL, lw=1.8)
    ax.text(corridor + 4, (row1_y + row2_y + h) / 2, "交接：脚本 + 数据库 + 文档", ha="center",
            va="center", fontsize=8.6, color=TEAL, rotation=90)
    arrow(ax, (xs[2], row2_y + h / 2), (xs[1] + w, row2_y + h / 2), color=TEAL, lw=1.8)
    arrow(ax, (xs[1], row2_y + h / 2), (xs[0] + w, row2_y + h / 2), color=TEAL, lw=1.8)

    rbox(ax, 4, 2.5, 142, 7,
         "全程一致性保障：Docker + PostgreSQL 16 · 源文件 SHA256 指纹 · 官方样例为唯一数据来源 · "
         "缺口（family_citation 0 行、库外引用）如实记录，不虚构数据",
         fc="#F5F5F5", ec=GREY, fs=9, tc="#404040")
    return save(fig, "图B-总体流程图.png")


LAYERS = [
    ("展示层", BLUE, ["Flask 路由：/ 首页 43 表列表", "/table/<name> 通用表浏览", "/patent/<id> 详情（活动文献）"]),
    ("分析层", TEAL, ["21 条分析 SQL（5 个主题）", "run_analysis.py → CSV/JSON 证据", "6 张统计图，供报告与 PPT 引用"]),
    ("存储层", NAVY, ["PostgreSQL 16 · schema patentdb", "43 业务表 / 345 字段 / 91 外键", "143 索引 · stage2_meta 审计"]),
    ("导入层", AMBER, ["import_samples.py 主控 + import_support.py", "SHA256 校验 · 逻辑根切分 · 幂等 UPSERT", "失败整批回滚 + 字段级错误留痕"]),
    ("数据源层", GREY, ["US 申请公布 / US 授权公告 / EP 全文 / EP DOCDB / 法律状态",
                        "17 个基础 XML（保留原始 CRLF 字节）"]),
]

MANAGEMENT = ["start.sh（启动 B 库）", "run.sh（验收 + 前端）", "run_all.py（固定样例验收）",
              "verify_fresh.py（全新复现）", "package_submission.py（打包提交）"]


def diagram_architecture():
    """图C 系统框图：五层架构 + 运行管理面。"""
    fig, ax = canvas(13.6, 8.2, 136, 82)
    title(ax, "图C 系统框图：五层架构与运行管理面", 68, 78)

    band_h = 12.4
    ys = [63, 49.6, 36.2, 22.8, 9.4]
    for (name, color, chips), y in zip(LAYERS, ys):
        ax.add_patch(FancyBboxPatch((4, y), 100, band_h, boxstyle="round,pad=0.4,rounding_size=1.6",
                                    facecolor="white", edgecolor=color, linewidth=1.5))
        ax.add_patch(FancyBboxPatch((4.6, y + 0.6), 16, band_h - 1.2,
                                    boxstyle="round,pad=0.3,rounding_size=1.2",
                                    facecolor=color, edgecolor=color))
        ax.text(12.6, y + band_h / 2, name, ha="center", va="center", fontsize=11,
                color="white", fontweight="bold")
        inner_w = (100 - 18) / len(chips)
        for i, chip in enumerate(chips):
            cx = 21.4 + i * inner_w
            ax.text(cx + inner_w / 2 - 0.6, y + band_h / 2, chip, ha="center", va="center",
                    fontsize=8.6, color=NAVY, linespacing=1.5)

    ax.add_patch(FancyBboxPatch((108, 9.4), 24, 66, boxstyle="round,pad=0.5,rounding_size=1.6",
                                facecolor="#FAFAFC", edgecolor="#7B5EA7", linewidth=1.4,
                                linestyle="--"))
    ax.text(120, 72.6, "运行管理面", ha="center", va="center", fontsize=10.5,
            fontweight="bold", color="#7B5EA7")
    for i, item in enumerate(MANAGEMENT):
        rbox(ax, 110.4, 62.6 - i * 12, 19.2, 9, item, fc="#F3EEF8", ec="#7B5EA7", fs=8.2,
             tc="#4B3670", rad=1.2)
        arrow(ax, (110.4, 67.1 - i * 12), (104, ys[min(i, len(LAYERS) - 1)] + band_h / 2),
              color="#7B5EA7", lw=1.0, style="-|>", ls="--", ms=10)
    return save(fig, "图C-系统框图.png")


LEFT_STEPS = [
    ("① 读取数据目录，定位 17 个基础 XML", "in", "#EAF1FB", BLUE),
    ("SHA256 与快照一致？", "dec", None, None),
    ("② 切分 logical_roots 为逻辑文档\n（幂等键：数据集 + 文献号）", "in", "#EAF1FB", BLUE),
    ("③ 按数据集选择解析器家族\n（US 申请公布/授权、EP 全文/DOCDB/法律状态）", "in", "#EAF1FB", BLUE),
    ("④ 解析著录项·人员·分类·引用\n·权利要求·说明书章节", "in", "#EAF1FB", BLUE),
]
RIGHT_STEPS = [
    ("⑤ 父表 UPSERT\n（patent / publication / person / classification）", "#E9F5F2", TEAL),
    ("⑥ 关联表与弱实体子表 UPSERT\n（专利×人员/分类、引用、权项，复合唯一键）", "#E9F5F2", TEAL),
    ("⑦ 写 stage2_meta 审计\n（批次 / 源文件 / 字段级错误）", "#E9F5F2", TEAL),
    ("行数与约束核对通过？", None, None),
    ("⑧ 提交事务并输出统计\n（否则整批回滚，不留半成品数据）", "#FDF3E3", AMBER),
]


def diagram_import_flow():
    """图D 导入流程图：解析导入主流程与失败分支。"""
    fig, ax = canvas(11.6, 9.4, 100, 104)
    title(ax, "图D 数据导入流程图（import_samples.py + import_support.py）", 50, 100)

    w, h = 40, 12
    left_x, right_x = 4, 56
    ys = [82, 66, 50, 34, 18]
    for (text, kind, fc, ec), y in zip(LEFT_STEPS, ys):
        if kind == "dec":
            diamond(ax, left_x + w / 2, y + h / 2, 34, 14, text)
        else:
            rbox(ax, left_x, y, w, h, text, fc=fc, ec=ec, fs=9, tc=NAVY)
    # 左侧竖向箭头（逐段绘制）
    for i in range(4):
        arrow(ax, (left_x + w / 2, ys[i]), (left_x + w / 2, ys[i + 1] + h), color=BLUE)

    arrow(ax, (left_x + w, 24), (right_x, 24), color=TEAL, lw=1.8)
    ax.text((left_x + w + right_x) / 2, 26, "逐逻辑文档写入", ha="center", va="bottom",
            fontsize=8.6, color=TEAL)

    ys_r = [82, 66, 50, 34, 18]
    for (text, fc, ec), y in zip(RIGHT_STEPS, ys_r):
        if fc is None:
            diamond(ax, right_x + w / 2, y + h / 2, 34, 14, text)
        else:
            rbox(ax, right_x, y, w, h, text, fc=fc, ec=ec, fs=9, tc=NAVY)
    for i in range(4):
        arrow(ax, (right_x + w / 2, ys_r[i]), (right_x + w / 2, ys_r[i + 1] + h), color=TEAL)

    rbox(ax, 12, 2.5, 76, 9,
         "失败分支：指纹不一致 / XML 解析异常 / 约束冲突 → 记录错误明细并整批回滚，\n"
         "下一次导入依据幂等键重跑，不产生重复行、不留下半成品数据",
         fc="#FDECEA", ec=RED, fs=9, tc="#8B2E2B")
    # 两条失败分支汇入中间走廊（x=50）后指向失败说明框，避免虚线穿过步骤框
    arrow(ax, (left_x + w / 2 + 17, 73), (49, 73), color=RED, lw=1.2, ls="--", ms=11)
    arrow(ax, (right_x + w / 2 - 17, 40), (51, 40), color=RED, lw=1.2, ls="--", ms=11)
    arrow(ax, (50, 73), (50, 11.8), color=RED, lw=1.2, ls="--", ms=11)
    ax.text(46.5, 69, "否", ha="right", va="center", fontsize=9, color=RED)
    ax.text(53.5, 44, "否", ha="left", va="center", fontsize=9, color=RED)
    return save(fig, "图D-导入流程图.png")


PHASES = [
    ("① 环境准备", BLUE, "#EAF1FB",
     ["创建一次性容器\n（唯一名称 + 随机端口）", "执行三个建库 SQL\n（建表 / 审计迁移 / 导入审计）",
      "源文件 SHA256 校验\n（17 个基础 XML）"]),
    ("② 数据导入", TEAL, "#E9F5F2",
     ["基础 XML 导入\n（基础口径）", "补充样例导入\n（EP 全文 / DOCDB / 法律状态）",
      "批次样例与幂等重跑\n（行数不翻倍）"]),
    ("③ 测试验证", AMBER, "#FDF3E3",
     ["故障注入验收 6/6", "冒烟测试 48/48", "外键违规 14/14",
      "复杂与边界 12/12", "前端用例 71/71"]),
    ("④ 交付留证", "#7B5EA7", "#F3EEF8",
     ["46 表内容一致性", "pg_dump 备份\n（patentdb-phase3.dump）", "独立数据库恢复比对",
      "*_result.json + 退出码"]),
]


def diagram_acceptance_flow():
    """图E 验收流程图：verify_fresh.py 的一次性全新复现。"""
    fig, ax = canvas(13.6, 7.6, 136, 76)
    title(ax, "图E 验收流程图：verify_fresh.py 全新容器复现（151 条用例全部 PASS）", 68, 72)

    w = 29
    xs = [4, 37, 70, 103]
    for (name, color, tint, steps), x in zip(PHASES, xs):
        rbox(ax, x, 62, w, 8, name, fc=color, ec=color, fs=10.5, tc="white", weight="bold", rad=1.6)
        box_h = 8.6 if len(steps) > 3 else 10
        gap = box_h + 1.8
        y = 50
        for step in steps:
            rbox(ax, x, y, w, box_h, step, fc=tint, ec=color, fs=8.6, tc=NAVY, rad=1.2)
            y -= gap
        for i in range(len(steps) - 1):
            arrow(ax, (x + w / 2, 50 - i * gap), (x + w / 2, 50 - (i + 1) * gap + box_h),
                  color=color, lw=1.2, ms=11)

    for i in range(3):
        arrow(ax, (xs[i] + w, 66), (xs[i + 1], 66), color=GREY, lw=1.6, ms=13)

    rbox(ax, 4, 1, 128, 8.5,
         "证据落盘：third stage/07-验收结果/*_result.json、performance_current.txt、fresh_acceptance.json，"
         "数据库备份 08-数据库交付/patentdb-phase3.dump（含 SHA256）\n"
         "成功退出码 0，失败非 0；测试只使用临时容器或回滚事务，不修改已交付数据库，"
         "每次复现均从空容器开始",
         fc="#F5F5F5", ec=GREY, fs=8.8, tc="#404040")
    return save(fig, "图E-验收流程图.png")


SCHEMA_GROUPS = [
    ("② 人员与角色（M:N 拆表 + ISA）", TEAL, [
        "person（patent_id 无；PK person_id）",
        "  person_type CHAR(1) ∈ {N, L}",
        "natural_person / organization（ISA 子类）",
        "patent_applicant / patent_inventor",
        "patent_assignee / patent_agent",
        "patent_examiner（审查员）",
        "5 张角色表均为「专利 × 人员」复合唯一键",
    ]),
    ("③ 分类（组合键维表）", BLUE, [
        "classification（PK scheme_code+symbol）",
        "  section / class_no / subclass",
        "patent_classification（专利 × 分类号）",
        "复合唯一键阻止同一专利重复挂同号",
    ]),
    ("④ 引用（一元递归 + 库外目标）", AMBER, [
        "patent_citation（PK citation_id）",
        "  citing_patent_id → patent（NOT NULL）",
        "  cited_patent_id → patent（可空：库外）",
        "  citation_type ∈ {P, N} + 类别码",
        "non_patent_citation（非专利文献全文）",
        "citation_category（引用类别维表）",
    ]),
    ("⑤ 专利族（M:N 自关联）", "#7B5EA7", [
        "patent_family（PK family_id, 族类型）",
        "patent_family_member（成员，可空转本地专利）",
        "family_member_publication_ref（成员文献号）",
        "family_member_application_ref（成员申请号）",
        "family_abstract / family_citation（后者 0 行）",
    ]),
    ("⑥ 程序关系 · 法律状态 · 增强", GREY, [
        "priority_claim / related_application",
        "designated_state（指定国）",
        "legal_status_event + legal_event_code",
        "keyword / patent_keyword（TITLE_DERIVED）",
        "ipc_techn_field（IPC 主组技术领域）",
    ]),
]


def diagram_schema_core():
    """图F 关键表关系示意图：文献主干 + 五个分支域的落地表。"""
    fig, ax = canvas(13.6, 8.0, 136, 88)
    title(ax, "图F 关键表关系示意图（43 张业务表按域归并，标注键与基数）", 68, 84)

    rbox(ax, 30, 60, 76, 20,
         "① 数据来源与文献主干\ndataset（数据来源维表） 1—N patent（申请案） 1—N publication（公布/公告文献）\n"
         "publication 1—N 文献部件弱实体：title / abstract / claim / drawing / description_section\n"
         "claim 1—N claim_dependency（从属权项 → 被引权项，一元递归）",
         fc="#EAF1FB", ec=BLUE, fs=9.4, tc=NAVY)

    w, gap = 25.2, 1.4
    xs = [2 + i * (w + gap) for i in range(5)]
    for (name, color, lines), x in zip(SCHEMA_GROUPS, xs):
        ax.add_patch(FancyBboxPatch((x, 6), w, 40, boxstyle="round,pad=0.4,rounding_size=1.4",
                                    facecolor="white", edgecolor=color, linewidth=1.4,
                                    linestyle="--"))
        rbox(ax, x + 0.8, 38.4, w - 1.6, 6.4, name, fc=color, ec=color, fs=8.4, tc="white",
             weight="bold", rad=1.2)
        for i, line in enumerate(lines):
            ax.text(x + 1.6, 35.2 - i * 4.6, line, ha="left", va="center", fontsize=7.1,
                    color="#333333", linespacing=1.4)

    ax.plot([68, 68], [60, 51], color=NAVY, linewidth=1.8)
    ax.plot([68, xs[-1] + w / 2], [51, 51], color=NAVY, linewidth=1.8)
    arrow(ax, (68, 51), (68, 47.2), color=NAVY, lw=1.3, ms=12)
    for gx in xs:
        arrow(ax, (gx + w / 2, 51), (gx + w / 2, 47.2), color=NAVY, lw=1.3, ms=12)
    ax.text(70, 55, "主干外键分别指向五个分支域（patent_id / publication_id / person_id）",
            ha="left", va="center", fontsize=8.4, color=NAVY, style="italic")
    return save(fig, "图F-关键表关系示意图.png")


def main():
    setup_font()
    produced = [diagram_use_case(), diagram_overall_flow(), diagram_architecture(),
                diagram_import_flow(), diagram_acceptance_flow(), diagram_schema_core()]
    print("已生成：" + ", ".join(p.name for p in produced))
    return produced


if __name__ == "__main__":
    main()



