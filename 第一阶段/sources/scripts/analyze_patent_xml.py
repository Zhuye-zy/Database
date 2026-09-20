#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""专利 XML 结构解析器: 输出元素路径、出现次数(0..1/1/1..N)、样例值、属性。

用法:
    python3 analyze_patent_xml.py <xml文件或目录> <输出前缀> [max_docs]

输出:
    <输出前缀>.md    Markdown 统计表
    <输出前缀>.csv   CSV 统计表(供 B 角色导入/建模参考)

原理:
    对每篇文档遍历全部元素, 记录其从根节点出发的路径; 叶子节点采集文本样例,
    所有节点采集属性。跨文档汇总: 文档内出现次数 min/max, 出现该路径的文档数。
"""
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict


def split_docs(text):
    starts = [m.start() for m in re.finditer(r'<\?xml\s', text)]
    if not starts:
        return [text]
    return [text[s:(starts[i + 1] if i + 1 < len(starts) else len(text))].strip()
            for i, s in enumerate(starts)]


def collect_files(path):
    if os.path.isdir(path):
        out = []
        for root, _dirs, files in os.walk(path):
            out.extend(os.path.join(root, f) for f in files if f.lower().endswith('.xml'))
        return sorted(out)
    return [path]


def local(tag):
    return tag.split('}')[-1] if '}' in tag else tag


def clean(s, n=120):
    s = re.sub(r'\s+', ' ', (s or '').strip())
    return s[:n] + ('...' if len(s) > n else '')


def logical_documents(root):
    """Return patent-level documents instead of treating a batch wrapper as one doc.

    DOCDB exchange files use ``exchange-documents`` as a batch wrapper.  Occurrence
    constraints must be calculated per ``exchange-document``; otherwise a path
    present in only one patent is incorrectly reported as mandatory and counts are
    doubled across the batch.
    """
    if local(root.tag) == 'exchange-documents':
        docs = [ch for ch in root if local(ch.tag) == 'exchange-document']
        return docs or [root]
    return [root]


def analyze(files, max_docs=3):
    stats = {}   # path -> dict
    doc_tags = {}
    n_doc = 0
    for fp in files:
        with open(fp, encoding='utf-8', errors='replace') as f:
            text = f.read()
        for doc in split_docs(text):
            if not doc:
                continue
            try:
                root = ET.fromstring(doc)
            except ET.ParseError:
                continue
            for logical_root in logical_documents(root):
                if n_doc >= max_docs:
                    break
                n_doc += 1
                root_tag = local(logical_root.tag)
                doc_tags.setdefault(root_tag, 0)
                doc_tags[root_tag] += 1
                counts = defaultdict(int)
                samples = {}
                attrs_seen = defaultdict(set)

                def walk(el, path):
                    cur = f'{path}/{local(el.tag)}'
                    counts[cur] += 1
                    if el.attrib:
                        for k, v in el.attrib.items():
                            attrs_seen[cur].add(f'{k}="{clean(v, 40)}"')
                    if el.text and el.text.strip():
                        samples.setdefault(cur, []).append(clean(el.text))
                    for ch in el:
                        walk(ch, cur)

                walk(logical_root, '')
                # First give every known path a zero for this document.  The old
                # implementation updated only present paths, so docs_present=1/4
                # could still be labelled occurrence=1 instead of 0..1.
                for p, st in stats.items():
                    if p not in counts:
                        st['min'] = 0
                for p, c in counts.items():
                    is_new = p not in stats
                    st = stats.setdefault(p, {'docs': 0, 'min': 0 if n_doc > 1 else c,
                                              'max': 0, 'samples': [], 'attrs': set()})
                    st['docs'] += 1
                    if not is_new:
                        st['min'] = min(st['min'], c)
                    st['max'] = max(st['max'], c)
                    st['samples'] = (st['samples'] + samples.get(p, []))[:3]
                    st['attrs'] |= attrs_seen.get(p, set())

    def occ(st):
        if st['min'] >= 1 and st['max'] == 1:
            return '1'
        if st['min'] == 0 and st['max'] == 1:
            return '0..1'
        if st['min'] >= 1:
            return f'1..N (max={st["max"]})'
        return f'0..N (max={st["max"]})'

    rows = []
    for p in sorted(stats):
        st = stats[p]
        rows.append({
            'path': p,
            'occurrence': occ(st) if st['min'] != 10 ** 9 else '0..N',
            'docs_present': f"{st['docs']}/{n_doc}",
            'min_per_doc': st['min'] if st['min'] != 10 ** 9 else 0,
            'max_per_doc': st['max'],
            'sample_value': ' | '.join(st['samples'][:2]),
            'attributes': ' '.join(sorted(st['attrs'])[:4]),
        })
    return rows, doc_tags, n_doc


def write_outputs(rows, doc_tags, n_doc, prefix, inputs):
    with open(prefix + '.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'occurrence', 'docs_present', 'min_per_doc',
                                          'max_per_doc', 'sample_value', 'attributes'])
        w.writeheader()
        w.writerows(rows)
    with open(prefix + '.md', 'w', encoding='utf-8') as f:
        f.write(f'# 专利 XML 结构解析结果\n\n')
        f.write(f'- 输入: {", ".join(os.path.basename(i) for i in inputs)}\n')
        f.write(f'- 解析文档数: {n_doc} (根元素: {doc_tags})\n')
        f.write(f'- 元素路径数: {len(rows)}\n\n')
        f.write('| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |\n')
        f.write('|---|---|---|---|---|---|---|\n')
        for r in rows:
            f.write('| `{}` | {} | {} | {} | {} | {} | {} |\n'.format(
                r['path'], r['occurrence'], r['docs_present'], r['min_per_doc'],
                r['max_per_doc'], r['sample_value'].replace('|', '\\|')[:100],
                r['attributes'].replace('|', '\\|')))
    print(f'wrote {prefix}.md / {prefix}.csv, rows={len(rows)}, docs={n_doc}')


def main():
    src, prefix = sys.argv[1], sys.argv[2]
    max_docs = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    files = collect_files(src)
    rows, doc_tags, n_doc = analyze(files, max_docs)
    write_outputs(rows, doc_tags, n_doc, prefix, files)


if __name__ == '__main__':
    main()
