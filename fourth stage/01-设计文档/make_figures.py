#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把第一阶段的概念设计矢量图（SVG）栅格化为报告用 PNG。

为什么需要：Word 不能嵌入 SVG，而模板要求插入 E-R 图等图形。
   1) 优先使用 cairosvg 直接渲染 SVG（保留矢量清晰度）；
   2) SVW 中的 font-family 若指向本机不存在的字体，会导致中文变方框，
      因此渲染前把字体族统一改写为系统可用的中文字体；
   3) 若 cairosvg 不可用则回退到仓库中已提交的 PNG（保证报告仍可生成）。

运行：python3 "fourth stage/01-设计文档/make_figures.py"
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "图"
STAGE1 = REPO / "第一阶段"
STAGE3_SHOTS = REPO / "third stage" / "07-验收结果" / "截图"
CHARTS = REPO / "fourth stage" / "03-分析挖掘" / "图表"
DIAGRAMS = REPO / "fourth stage" / "04-流程图与框图"

FONT_STACK = "Microsoft YaHei,SimHei,SimSun,Noto Sans CJK SC,sans-serif"

# (源 SVG, 输出名, 回退 PNG)
SVG_JOBS = [
    (STAGE1 / "04-ER图-域1-著录与文献.svg", "图2a-ER域1-著录与文献.png", None),
    (STAGE1 / "04-ER图-域2-人员与角色.svg", "图2b-ER域2-人员与角色.png", None),
    (STAGE1 / "04-ER图-域3-分类.svg", "图2c-ER域3-分类.png", None),
    (STAGE1 / "04-ER图-域4-引用.svg", "图2d-ER域4-引用.png", None),
    (STAGE1 / "04-ER图-域5-专利族与程序关系.svg", "图2e-ER域5-专利族与程序关系.png", None),
    (STAGE1 / "04-ER图-域6-法律状态与关键词.svg", "图2f-ER域6-法律状态与关键词.png", None),
]

# (源 PNG, 输出名) —— 直接复制，保证报告引用的图名统一
COPY_JOBS = [
    (DIAGRAMS / "图A-用例图.png", "图1-用例图.png"),
    (DIAGRAMS / "图F-关键表关系示意图.png", "图3-关键表关系示意图.png"),
    (DIAGRAMS / "图B-总体流程图.png", "图4-总体流程图.png"),
    (DIAGRAMS / "图C-系统框图.png", "图5-系统框图.png"),
    (DIAGRAMS / "图D-导入流程图.png", "图6-数据导入流程图.png"),
    (DIAGRAMS / "图E-验收流程图.png", "图7-验收流程图.png"),
    (STAGE3_SHOTS / "01-首页-43表.png", "图8-前端首页43表.png"),
    (STAGE3_SHOTS / "02-patent表-19行.png", "图9-前端patent表.png"),
    (STAGE3_SHOTS / "03-专利详情-patent1.png", "图10-前端专利详情.png"),
    (CHARTS / "图1-技术领域分布.png", "图11-技术领域分布.png"),
    (CHARTS / "图2-申请人排名.png", "图12-申请人排名.png"),
    (CHARTS / "图3-引用网络结构.png", "图13-引用网络结构.png"),
    (CHARTS / "图4-被引文献国别与年代.png", "图14-被引国别与年代.png"),
    (CHARTS / "图5-权利要求与多语言.png", "图15-权利要求与多语言.png"),
    (CHARTS / "图6-数据来源与年份.png", "图16-数据来源与年份.png"),
]


def rewrite_fonts(svg_text: str) -> str:
    """把 SVG 中的字体族改写成系统中文字体栈，避免中文渲染成方框。"""
    out = re.sub(r"font-family\s*:\s*[^;\"'}]+", f"font-family:{FONT_STACK}", svg_text)
    out = re.sub(r'font-family\s*=\s*"[^"]*"', f'font-family="{FONT_STACK}"', out)
    return out


def render_svg(src: Path, dst: Path, scale: float = 2.0) -> bool:
    try:
        import cairosvg
    except ImportError:
        return False
    svg = rewrite_fonts(src.read_text(encoding="utf-8"))
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(dst), scale=scale,
                     background_color="white")
    return True


def normalize(path: Path, max_width: int = 3600) -> None:
    """控制嵌入文档的图片像素规模：过宽的图（如 43 表关系模式总览）等比缩小。"""
    try:
        from PIL import Image
    except ImportError:
        return
    with Image.open(path) as im:
        if im.width <= max_width:
            return
        ratio = max_width / im.width
        resized = im.convert("RGB").resize((max_width, max(1, round(im.height * ratio))),
                                           Image.LANCZOS)
        resized.save(path, optimize=True)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    made, fallback = [], []

    for src, name, fallback_png in SVG_JOBS:
        dst = OUT / name
        if src.exists() and render_svg(src, dst):
            made.append(name)
        elif fallback_png and fallback_png.exists():
            shutil.copyfile(fallback_png, dst)
            fallback.append(name)
        else:
            print(f"[警告] 缺少图形来源：{src}")

    for src, name in COPY_JOBS:
        if not src.exists():
            print(f"[警告] 缺少图形来源：{src}")
            continue
        shutil.copyfile(src, OUT / name)
        made.append(name)

    for name in made:
        normalize(OUT / name)

    print(f"共输出 {len(made)} 个图形到 {OUT.relative_to(REPO)}")
    if fallback:
        print("以下图形使用了仓库内既有 PNG 回退（未安装 cairosvg）：" + ", ".join(fallback))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
