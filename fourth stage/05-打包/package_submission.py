#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包课程提交包：把仓库归档为 ZIP，并输出文件清单与 SHA256 指纹。

排除项：.git / .venv / __pycache__ 等缓存目录，以及 *.pyc、*.log、*.tmp 等临时文件。
打包后重新打开压缩包自检（testzip 必须为 None，条目数与清单一致）。

运行：
    .venv/bin/python 'fourth stage/05-打包/package_submission.py'
"""
from __future__ import annotations

import hashlib
import subprocess
import zipfile
from datetime import date
from pathlib import Path

DIR = Path(__file__).resolve().parent
REPO = DIR.parents[1]
TODAY = date.today().strftime("%Y%m%d")
OUT = DIR / f"数据库实践-题目5-第四阶段提交包-{TODAY}.zip"
MANIFEST = DIR / f"提交包文件清单-{TODAY}.txt"

EXCLUDE_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".idea"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".tmp", ".log", ".swp"}
EXCLUDE_NAMES = {".DS_Store", "Thumbs.db"}


def iter_files() -> list[Path]:
    """按稳定顺序列出待打包文件（跳过排除项）。"""
    files = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.suffix in EXCLUDE_SUFFIX or path.name in EXCLUDE_NAMES:
            continue
        # 打包产物本身不再入包（否则每次打包都会把上一版压缩包一起装进去）
        if path.parent == DIR and (path.suffix == ".zip" or path.name.startswith("提交包文件清单")):
            continue
        files.append(path)
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    """尽力取当前提交号，取不到时返回占位说明（不当作失败）。"""
    try:
        done = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=10, check=False)
        return done.stdout.strip() or "（工作区未提交）"
    except (OSError, subprocess.SubprocessError):
        return "（未安装 git 或不是仓库）"


def main() -> int:
    files = iter_files()
    if not files:
        print("[打包] 没有找到可打包文件，请检查目录")
        return 1

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            archive.write(path, path.relative_to(REPO).as_posix())

    # 自检：重新打开压缩包，核对条目数与内容可读
    with zipfile.ZipFile(OUT) as archive:
        names = archive.namelist()
        broken = archive.testzip()

    rows = [(path.relative_to(REPO).as_posix(), path.stat().st_size, sha256(path)) for path in files]
    header = [f"提交包清单　{OUT.name}",
              f"生成时间：{date.today().isoformat()}",
              f"仓库提交：{git_commit()}",
              f"文件数：{len(rows)}　压缩包大小：{OUT.stat().st_size / 1024 / 1024:.2f} MB",
              "",
              f"{'路径':<62}{'字节':>10}  SHA256",
              "-" * 110]
    MANIFEST.write_text("\n".join(header + [f"{name:<62}{size:>10}  {digest}"
                                            for name, size, digest in rows]) + "\n",
                        encoding="utf-8")

    problems = []
    if broken:
        problems.append(f"压缩包内条目损坏：{broken}")
    if len(names) != len(files):
        problems.append(f"压缩包条目数 {len(names)} 与清单文件数 {len(files)} 不一致")
    print(f"[打包] {OUT}（{OUT.stat().st_size / 1024 / 1024:.2f} MB，{len(files)} 个文件）")
    print(f"[打包] 清单：{MANIFEST.name}（含每文件 SHA256）")
    top = sorted({name.split('/')[0] for name in names})
    print(f"[打包] 顶层目录：{' / '.join(top)}")
    if problems:
        print("[打包] 发现问题：" + "；".join(problems))
        return 1
    print("[打包] 自检通过：压缩包可读、条目数与清单一致。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
