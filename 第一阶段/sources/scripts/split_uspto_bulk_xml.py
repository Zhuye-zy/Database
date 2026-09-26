#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 USPTO 批量全文 XML(多个 <us-patent-*> 文档拼接)拆分为单文档文件。

用法:
    python3 split_uspto_bulk_xml.py <输入文件> <输出目录> [最多拆分数]

说明:
    USPTO bulkdata 全文 XML 将一个周期内的多件专利文档直接拼接在一个 .xml 文件里,
    整文件并非合法 XML。本脚本按 '<?xml' 声明切分, 仅保留包含根结束标签的完整文档。
"""
import re
import sys
import os
import xml.etree.ElementTree as ET


def split_docs(text):
    starts = [m.start() for m in re.finditer(r'<\?xml\s', text)]
    docs = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(text)
        chunk = text[s:e].strip()
        if chunk:
            docs.append(chunk)
    return docs


def get_doc_number(doc_text):
    m = re.search(r'<publication-reference>.*?<doc-number>([^<]+)</doc-number>', doc_text, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r'<application-reference[^>]*>.*?<doc-number>([^<]+)</doc-number>', doc_text, re.S)
    return m.group(1).strip() if m else 'UNKNOWN'


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    in_path, out_dir = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    os.makedirs(out_dir, exist_ok=True)
    with open(in_path, encoding='utf-8', errors='replace') as f:
        text = f.read()
    docs = split_docs(text)
    root_tag = 'us-patent-grant' if re.search(r'<\?xml[^>]*|<!DOCTYPE\s+us-patent-grant', text[:2000]) else ''
    print(f'共发现 {len(docs)} 个文档片段')
    ok = 0
    for i, doc in enumerate(docs):
        try:
            ET.fromstring(doc)
        except ET.ParseError as ex:
            print(f'  文档 {i + 1} 解析失败: {ex}')
            continue
        if ok >= limit:
            break
        num = get_doc_number(doc)
        tag = ET.fromstring(doc).tag
        out = os.path.join(out_dir, f'{tag}-{num}.xml')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(doc if doc.endswith('\n') else doc + '\n')
        print(f'  已写出 {out}')
        ok += 1
    print(f'完成, 共写出 {ok} 个单文档样例')


if __name__ == '__main__':
    main()
