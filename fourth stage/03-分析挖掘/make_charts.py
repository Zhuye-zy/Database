#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D 角色统计图生成：读取 run_analysis.py 的结果对象，输出报告/PPT 用 PNG。

单独运行（不连数据库，使用已有 结果/analysis_results.json）：
    python3 "fourth stage/03-分析挖掘/make_charts.py"
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import font_manager  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_JSON = HERE / "结果" / "analysis_results.json"

# 统一配色（与 PPT 主题一致）
C_MAIN, C_ALT, C_ACC, C_WARN, C_GREY = "#2F5597", "#4E9F8C", "#E8A33D", "#C0504D", "#8C8C8C"
PALETTE = [C_MAIN, C_ALT, C_ACC, C_WARN, C_GREY, "#6B7FD7", "#97B4D8"]

FONT_CANDIDATES = [
    "/mnt/c/Windows/Fonts/msyh.ttc",
    "/mnt/c/Windows/Fonts/simhei.ttf",
    "/mnt/c/Windows/Fonts/simsun.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]


def setup_font() -> str:
    """注册可用的中文字体，避免图中出现方框。"""
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                font_manager.fontManager.addfont(path)
                name = font_manager.FontProperties(fname=path).get_name()
                plt.rcParams["font.sans-serif"] = [name, "DejaVu Sans"]
                plt.rcParams["axes.unicode_minus"] = False
                return name
            except Exception:  # noqa: BLE001 - 换下一个候选字体
                continue
    plt.rcParams["axes.unicode_minus"] = False
    return "DejaVu Sans"


def _index(summary: dict) -> dict:
    """把 analysis_results.json 拍平成 {查询名: 查询对象}。"""
    flat = {}
    for analysis in summary.get("analyses", []):
        for q in analysis.get("queries", []):
            if q.get("status") == "PASS":
                flat[q["name"]] = q
    return flat


def rows_of(flat: dict, name: str) -> list[list[str]]:
    q = flat.get(name)
    if q is None:
        raise KeyError(f"结果文件缺少查询 {name}，请先运行 run_analysis.py")
    return q["rows"]


def nums(rows, index):
    return [int(float(r[index])) for r in rows]


def style(ax, title=None, xlabel=None, ylabel=None, grid_axis="y"):
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color="#1F3864", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=10)
    ax.grid(axis=grid_axis, linestyle=":", color="#BFBFBF", alpha=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def save(fig, out_dir: Path, name: str, produced: list):
    path = out_dir / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    produced.append(path)


def chart1_sections(flat, out_dir, produced):
    """图1 技术领域分布：IPC / CPC 部级专利数。"""
    rows = rows_of(flat, "ipc_section")
    schemes = sorted({r[0] for r in rows})
    sections = sorted({r[1] for r in rows})
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    width = 0.38
    for i, scheme in enumerate(schemes):
        vals = []
        for sec in sections:
            hit = [int(r[2]) for r in rows if r[0] == scheme and r[1] == sec]
            vals.append(hit[0] if hit else 0)
        pos = [j + (i - (len(schemes) - 1) / 2) * width for j in range(len(sections))]
        bars = ax.bar(pos, vals, width, label=scheme, color=PALETTE[i], edgecolor="white")
        ax.bar_label(bars, labels=[v if v else "" for v in vals], fontsize=9, padding=2)
    ax.set_xticks(range(len(sections)))
    ax.set_xticklabels([f"{s} 部" for s in sections])
    style(ax, "技术领域分布（IPC / CPC 部级，按专利去重）", ylabel="专利数")
    ax.legend(title="分类体系", frameon=False)
    save(fig, out_dir, "图1-技术领域分布.png", produced)


def chart2_applicants(flat, out_dir, produced):
    """图2 申请人排名：TOP10 专利数（机构/自然人着色）。"""
    rows = rows_of(flat, "applicant_rank")[:10]
    rows = sorted(rows, key=lambda r: (int(r[2]), r[0]))
    labels = [r[0][:26] for r in rows]
    vals = [int(r[2]) for r in rows]
    colors = [C_MAIN if r[1] == "机构" else C_ALT for r in rows]
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    bars = ax.barh(labels, vals, color=colors, edgecolor="white")
    ax.bar_label(bars, labels=[str(v) for v in vals], fontsize=9, padding=3)
    ax.set_xlim(0, max(vals) + 0.6 if vals else 1)
    style(ax, "申请人排名（TOP10，按专利数去重）", xlabel="专利数", grid_axis="x")
    handles = [plt.Rectangle((0, 0), 1, 1, color=C_MAIN),
               plt.Rectangle((0, 0), 1, 1, color=C_ALT)]
    ax.legend(handles, ["机构", "自然人"], frameon=False, loc="lower right")
    save(fig, out_dir, "图2-申请人排名.png", produced)


def chart3_citations(flat, out_dir, produced):
    """图3 引用网络：类型分布 + 引用方出度 TOP8（堆叠 P/N）。"""
    types = rows_of(flat, "type_split")
    outdeg = rows_of(flat, "out_degree")[:8]
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.6))

    labels = [r[1] for r in types]
    totals = [int(r[2]) for r in types]
    docs = [int(r[3]) for r in types]
    bars = axes[0].bar(labels, totals, color=[C_MAIN, C_ALT][: len(labels)], width=0.55,
                       edgecolor="white")
    axes[0].bar_label(bars, labels=[f"{t} 条\n{ d } 件专利" for t, d in zip(totals, docs)],
                      fontsize=9, padding=3)
    axes[0].set_ylim(0, max(totals) * 1.28 if totals else 1)
    style(axes[0], "引用类型分布（P 专利 / N 非专利）", ylabel="引用条数")

    outdeg = sorted(outdeg, key=lambda r: int(r[4]))
    y = range(len(outdeg))
    p_vals = [int(r[2]) for r in outdeg]
    n_vals = [int(r[3]) for r in outdeg]
    axes[1].barh(y, p_vals, color=C_MAIN, label="专利引用 P", edgecolor="white")
    axes[1].barh(y, n_vals, left=p_vals, color=C_ACC, label="非专利引用 N", edgecolor="white")
    axes[1].set_yticks(list(y))
    axes[1].set_yticklabels([f"专利{r[0]}" for r in outdeg], fontsize=9)
    for i, r in enumerate(outdeg):
        axes[1].text(int(r[4]) + 8, i, str(r[4]), va="center", fontsize=9)
    axes[1].set_xlim(0, max([int(r[4]) for r in outdeg], default=1) * 1.18)
    style(axes[1], "引用方出度 TOP8（该专利引用了多少文献）", xlabel="引用条数", grid_axis="x")
    axes[1].legend(frameon=False, loc="lower right")
    fig.suptitle("引用网络结构（本样例被引目标全部在库外，故只给出引用方结构）",
                 fontsize=12, fontweight="bold", color="#1F3864", y=1.02)
    fig.tight_layout()
    save(fig, out_dir, "图3-引用网络结构.png", produced)


def chart4_cited(flat, out_dir, produced):
    """图4 被引文献国别分布 + 年代分布。"""
    countries = rows_of(flat, "cited_country")
    decades = rows_of(flat, "cited_decade")
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 4.4))

    top = countries[:5]
    rest = sum(int(r[1]) for r in countries[5:])
    labels = [r[0] for r in top] + ([f"其他 {len(countries) - 5} 国"] if rest else [])
    vals = [int(r[1]) for r in top] + ([rest] if rest else [])
    wedges, _, autotexts = axes[0].pie(
        vals, autopct="%1.1f%%", startangle=105, pctdistance=0.75,
        colors=PALETTE[: len(vals)], wedgeprops={"width": 0.42, "edgecolor": "white"})
    for t in autotexts:
        t.set_fontsize(8.5)
    axes[0].legend(wedges, [f"{l}（{v}）" for l, v in zip(labels, vals)],
                   loc="center left", bbox_to_anchor=(0.92, 0.5), frameon=False, fontsize=9)
    axes[0].set_title("被引专利文献的来源国别", fontsize=12, fontweight="bold", color="#1F3864")

    xs = [f"{r[0]}s" for r in decades]
    ys = [int(r[1]) for r in decades]
    bars = axes[1].bar(xs, ys, color=C_MAIN, width=0.62, edgecolor="white")
    axes[1].bar_label(bars, fontsize=8.5, padding=2)
    axes[1].tick_params(axis="x", labelrotation=45)
    style(axes[1], "被引专利文献的年代分布", xlabel="年代段", ylabel="被引次数")
    fig.tight_layout()
    save(fig, out_dir, "图4-被引文献国别与年代.png", produced)




def chart5_claims(flat, out_dir, produced):
    """图5 权利要求结构（独立/从属）+ 多语言分布。"""
    structure = rows_of(flat, "doc_structure")[:8]
    langs = rows_of(flat, "lang_split")
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))

    xs = [f"{r[1]}\n({r[2]})" for r in structure]
    indep = [int(r[3]) for r in structure]
    dep = [int(r[4]) for r in structure]
    pos = list(range(len(structure)))
    axes[0].bar(pos, indep, color=C_MAIN, label="独立权利要求", edgecolor="white")
    axes[0].bar(pos, dep, bottom=indep, color=C_ALT, label="从属权利要求", edgecolor="white")
    for i, (a, b) in enumerate(zip(indep, dep)):
        axes[0].text(i, a + b + 0.8, str(a + b), ha="center", fontsize=9)
    axes[0].set_xticks(pos)
    axes[0].set_xticklabels(xs, fontsize=7.5)
    style(axes[0], "各文献权利要求结构 TOP8（含多语言合计）", ylabel="权利要求条数")
    axes[0].legend(frameon=False)

    lang_names = [r[0] for r in langs]
    claim_cnt = [int(r[1]) for r in langs]
    title_cnt = [int(r[2]) for r in langs]
    width = 0.36
    p1 = [i - width / 2 for i in range(len(langs))]
    p2 = [i + width / 2 for i in range(len(langs))]
    b1 = axes[1].bar(p1, claim_cnt, width, color=C_MAIN, label="权利要求", edgecolor="white")
    b2 = axes[1].bar(p2, title_cnt, width, color=C_ACC, label="标题", edgecolor="white")
    axes[1].bar_label(b1, fontsize=9, padding=2)
    axes[1].bar_label(b2, fontsize=9, padding=2)
    axes[1].set_xticks(range(len(langs)))
    axes[1].set_xticklabels(lang_names)
    style(axes[1], "多语言分布（EP 文献按语言分套）", ylabel="条数")
    axes[1].legend(frameon=False)
    fig.tight_layout()
    save(fig, out_dir, "图5-权利要求与多语言.png", produced)


def chart6_dataset(flat, out_dir, produced):
    """图6 数据来源分布（环形）+ 公布年份分布。"""
    datasets = rows_of(flat, "dataset_split")
    years = rows_of(flat, "publn_year")
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 4.5))

    labels = [r[0] for r in datasets]
    vals = [int(r[2]) for r in datasets]
    wedges, _, autotexts = axes[0].pie(
        vals, autopct=lambda p: f"{p:.0f}%", startangle=90, pctdistance=0.78,
        colors=PALETTE[: len(vals)], wedgeprops={"width": 0.42, "edgecolor": "white"})
    for t in autotexts:
        t.set_fontsize(8.5)
    axes[0].legend(wedges, [f"{l}（{v} 篇）" for l, v in zip(labels, vals)],
                   loc="center left", bbox_to_anchor=(0.92, 0.5), frameon=False, fontsize=9)
    axes[0].set_title("数据来源分布（官方样例 5 类）", fontsize=12, fontweight="bold", color="#1F3864")

    xs = [r[0] for r in years]
    ys = [int(r[1]) for r in years]
    bars = axes[1].bar(xs, ys, color=C_MAIN, width=0.5, edgecolor="white")
    axes[1].bar_label(bars, fontsize=9.5, padding=2)
    axes[1].set_ylim(0, max(ys) * 1.22 if ys else 1)
    style(axes[1], "文献公布年份分布（可确定到日的记录）", xlabel="公布年份", ylabel="文献数")
    fig.tight_layout()
    save(fig, out_dir, "图6-数据来源与年份.png", produced)


def build_all(summary: dict, out_dir: Path) -> list:
    """按结果对象生成全部图表，返回生成的文件路径列表。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    setup_font()
    flat = _index(summary)
    produced: list = []
    for fn in (chart1_sections, chart2_applicants, chart3_citations,
               chart4_cited, chart5_claims, chart6_dataset):
        fn(flat, out_dir, produced)
    return produced


def _load_default():
    return json.loads(DEFAULT_JSON.read_text(encoding="utf-8"))


if __name__ == "__main__":
    charts = build_all(_load_default(), HERE / "图表")
    print("已生成：" + ", ".join(p.name for p in charts))

