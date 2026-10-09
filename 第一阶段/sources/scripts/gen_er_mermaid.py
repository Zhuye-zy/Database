#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 gen_data_dictionary.T 生成 Mermaid erDiagram（总览图 + 完整属性图 + 关键子图）。

用法: python3 gen_er_mermaid.py <out_dir>
输出: ER-总览.mmd, ER-完整属性.mmd, ER-关键关系子图.mmd
"""
import re
import sys

import gen_data_dictionary as g


def mtype(t):
    t = t.split('/')[0].strip()
    m = re.match(r'(VARCHAR|CHAR)\((\d+)\)', t)
    if m:
        return f'{m.group(1).lower()}{m.group(2)}'
    return {'BIGINT': 'bigint', 'INT': 'int', 'SMALLINT': 'smallint',
            'REAL': 'real', 'DATE': 'date', 'TEXT': 'text'}.get(t, 'varchar')


def mkey(k):
    parts = [p for p in (k or '').split('/') if p in ('PK', 'FK', 'UK')]
    return ', '.join(dict.fromkeys(parts))


def attr_comment(c):
    cn = c[1] or ''
    fk = c[5] or ''
    src = c[6] or ''
    bits = [cn]
    if fk:
        bits.append('→' + fk.split('.')[0])
    if src.startswith('ST.9'):
        bits.append(src.split('/')[0])
    return ' '.join(bits).replace('"', "'")


RELS = [
    ('DATASET', 'PATENT', '||--o{', 'source_of'),
    ('DATASET', 'PUBLICATION', '||--o{', 'source_of'),
    ('DATASET', 'PERSON', '||--o{', 'source_of'),
    ('DATASET', 'PATENT_FAMILY', '||--o{', 'source_of'),
    ('DATASET', 'LEGAL_STATUS_EVENT', '||--o{', 'source_of'),
    ('COUNTRY_OFFICE', 'PATENT', '||--o{', 'appln_auth'),
    ('COUNTRY_OFFICE', 'PUBLICATION', '||--o{', 'publn_auth'),
    ('COUNTRY_OFFICE', 'PERSON', '|o--o{', 'country'),
    ('COUNTRY_OFFICE', 'PATENT_CITATION', '|o--o{', 'cited_country'),
    ('COUNTRY_OFFICE', 'LEGAL_STATUS_EVENT', '||--o{', 'event_auth'),
    ('COUNTRY_OFFICE', 'DESIGNATED_STATE', '||--o{', 'state_code'),
    ('LANGUAGE', 'TITLE', '||--o{', 'lang'),
    ('LANGUAGE', 'ABSTRACT', '||--o{', 'lang'),
    ('LANGUAGE', 'PUBLICATION', '||--o{', 'publn_lg'),
    ('LANGUAGE', 'PATENT', '||--o{', 'appln_lang'),
    ('KIND_CODE', 'PUBLICATION', '||--o{', 'kind'),
    ('APPLICATION_TYPE', 'PATENT', '||--o{', 'appl_type'),
    ('CLASSIFICATION_SCHEME', 'CLASSIFICATION', '||--o{', 'scheme'),
    ('CLASSIFICATION_SCHEME', 'PATENT_CLASSIFICATION', '||--o{', 'scheme'),
    ('LEGAL_EVENT_CODE', 'LEGAL_STATUS_EVENT', '||--o{', 'event'),
    ('CLASSIFICATION', 'PATENT_CLASSIFICATION', '||--o{', 'symbol'),
    ('PATENT', 'PUBLICATION', '||--o{', 'has_publication'),
    ('PUBLICATION', 'TITLE', '||--o{', 'has_title'),
    ('PUBLICATION', 'ABSTRACT', '||--o{', 'has_abstract'),
    ('PUBLICATION', 'CLAIM', '||--o{', 'has_claim'),
    ('PUBLICATION', 'DRAWING', '||--o{', 'has_drawing'),
    ('PUBLICATION', 'DESCRIPTION_SECTION', '||--o{', 'has_section'),
    ('DESCRIPTION_SECTION', 'DESCRIPTION_SECTION', '||--o{', 'parent_of'),
    ('CLAIM', 'CLAIM_DEPENDENCY', '||--o{', 'dependent_side'),
    ('CLAIM', 'CLAIM_DEPENDENCY', '||--o{', 'parent_side'),
    ('PATENT', 'PATENT_APPLICANT', '||--o{', 'has'),
    ('PERSON', 'PATENT_APPLICANT', '||--o{', 'as_applicant'),
    ('PATENT', 'PATENT_INVENTOR', '||--o{', 'has'),
    ('PERSON', 'PATENT_INVENTOR', '||--o{', 'as_inventor'),
    ('PATENT', 'PATENT_ASSIGNEE', '||--o{', 'has'),
    ('PERSON', 'PATENT_ASSIGNEE', '||--o{', 'as_assignee'),
    ('PATENT', 'PATENT_AGENT', '||--o{', 'has'),
    ('PERSON', 'PATENT_AGENT', '||--o{', 'as_agent'),
    ('PATENT', 'PATENT_EXAMINER', '||--o{', 'has'),
    ('PERSON', 'PATENT_EXAMINER', '||--o{', 'as_examiner'),
    ('PATENT', 'PATENT_CLASSIFICATION', '||--o{', 'has'),
    ('PATENT', 'PATENT_CITATION', '||--o{', 'citing'),
    ('PUBLICATION', 'PATENT_CITATION', '||--o{', 'citation_source'),
    ('PATENT', 'PATENT_CITATION', '|o--o{', 'cited'),
    ('PATENT_CITATION', 'PATENT_CITATION_CATEGORY', '||--o{', 'has'),
    ('CITATION_CATEGORY', 'PATENT_CITATION_CATEGORY', '||--o{', 'categorized'),
    ('PATENT_CITATION', 'NON_PATENT_CITATION', '||--o|', 'npl_ext'),
    ('PATENT', 'PATENT_FAMILY_MEMBER', '|o--o{', 'member'),
    ('PATENT_FAMILY', 'PATENT_FAMILY_MEMBER', '||--o{', 'has'),
    ('PATENT_FAMILY_MEMBER', 'FAMILY_MEMBER_APPLICATION_REF', '||--o{', 'has_application_ref'),
    ('PATENT_FAMILY_MEMBER', 'FAMILY_MEMBER_PUBLICATION_REF', '||--o{', 'has_publication_ref'),
    ('COUNTRY_OFFICE', 'FAMILY_MEMBER_APPLICATION_REF', '|o--o{', 'application_country'),
    ('COUNTRY_OFFICE', 'FAMILY_MEMBER_PUBLICATION_REF', '|o--o{', 'publication_country'),
    ('PATENT_FAMILY', 'FAMILY_ABSTRACT', '||--o{', 'has_abstract'),
    ('LANGUAGE', 'FAMILY_ABSTRACT', '|o--o{', 'abstract_language'),
    ('PATENT_FAMILY', 'FAMILY_CITATION', '||--o{', 'citing_fam'),
    ('PATENT_FAMILY', 'FAMILY_CITATION', '||--o{', 'cited_fam'),
    ('PATENT', 'PRIORITY_CLAIM', '||--o{', 'later_app'),
    ('PATENT', 'PRIORITY_CLAIM', '|o--o{', 'prior_app'),
    ('PATENT', 'RELATED_APPLICATION', '||--o{', 'main_app'),
    ('PATENT', 'RELATED_APPLICATION', '|o--o{', 'related_app'),
    ('PATENT', 'INTERNATIONAL_APPLICATION', '||--o|', 'nat_entry'),
    ('PATENT', 'INTERNATIONAL_APPLICATION', '|o--o{', 'pct_app'),
    ('PATENT', 'LEGAL_STATUS_EVENT', '||--o{', 'has_event'),
    ('PATENT', 'DESIGNATED_STATE', '||--o{', 'designated'),
    ('PATENT', 'PATENT_KEYWORD', '||--o{', 'has'),
    ('KEYWORD', 'PATENT_KEYWORD', '||--o{', 'tagged'),
    ('PATENT_FAMILY', 'PUBLICATION', '||--o|', 'representative'),
]

SUBSET = ['PATENT', 'PUBLICATION', 'CLAIM', 'CLAIM_DEPENDENCY', 'PATENT_CITATION',
          'NON_PATENT_CITATION', 'PATENT_FAMILY', 'PATENT_FAMILY_MEMBER', 'FAMILY_CITATION',
          'FAMILY_MEMBER_APPLICATION_REF', 'FAMILY_MEMBER_PUBLICATION_REF', 'FAMILY_ABSTRACT',
          'PRIORITY_CLAIM', 'PERSON', 'PATENT_APPLICANT', 'PATENT_INVENTOR', 'CLASSIFICATION',
          'PATENT_CLASSIFICATION', 'RELATED_APPLICATION']


def overview():
    lines = ['erDiagram']
    for t in g.T:
        lines.append(f'    {t["name"].upper()} {{')
        for c in t['cols']:
            k = mkey(c[4])
            if k:
                lines.append(f'        {mtype(c[2])} {c[0]} {k}')
        lines.append('    }')
    for a, b, card, label in RELS:
        lines.append(f'    {a} {card} {b} : "{label}"')
    return '\n'.join(lines) + '\n'


def full():
    lines = ['erDiagram']
    for t in g.T:
        lines.append(f'    {t["name"].upper()} {{')
        for c in t['cols']:
            k = mkey(c[4])
            parts = [mtype(c[2]), c[0]]
            if k:
                parts.append(k)
            parts.append('"' + attr_comment(c) + '"')
            lines.append('        ' + ' '.join(parts))
        lines.append('    }')
    for a, b, card, label in RELS:
        lines.append(f'    {a} {card} {b} : "{label}"')
    return '\n'.join(lines) + '\n'


def subset():
    lines = ['erDiagram']
    for t in g.T:
        if t['name'].upper() not in SUBSET:
            continue
        lines.append(f'    {t["name"].upper()} {{')
        for c in t['cols']:
            k = mkey(c[4])
            if k:
                lines.append(f'        {mtype(c[2])} {c[0]} {k}')
        lines.append('    }')
    for a, b, card, label in RELS:
        if a in SUBSET and b in SUBSET:
            lines.append(f'    {a} {card} {b} : "{label}"')
    return '\n'.join(lines) + '\n'


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    for name, content in [('ER-总览.mmd', overview()),
                          ('ER-完整属性.mmd', full()),
                          ('ER-关键关系子图.mmd', subset())]:
        with open(f'{out}/{name}', 'w', encoding='utf-8') as f:
            f.write(content)
        print('wrote', name, len(content.splitlines()), 'lines')


if __name__ == '__main__':
    main()
