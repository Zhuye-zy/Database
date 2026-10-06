# 冒烟测试结果（2026-10-06T18:17:47）

- schema：`patentdb`
- PostgreSQL：`PostgreSQL 16.15 (Debian 16.15-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`
- 业务表数量：**43**

## 1. 逐表 LIMIT 10 + 行数

| # | 表名 | 行数 | LIMIT 10 |
|---|---|---|---|
| 1 | abstract | 13 | PASS |
| 2 | application_type | 4 | PASS |
| 3 | citation_category | 2 | PASS |
| 4 | claim | 184 | PASS |
| 5 | claim_dependency | 84 | PASS |
| 6 | classification | 56 | PASS |
| 7 | classification_scheme | 2 | PASS |
| 8 | country_office | 50 | PASS |
| 9 | dataset | 5 | PASS |
| 10 | description_section | 538 | PASS |
| 11 | designated_state | 47 | PASS |
| 12 | drawing | 92 | PASS |
| 13 | family_abstract | 1 | PASS |
| 14 | family_citation | 0 | PASS |
| 15 | family_member_application_ref | 21 | PASS |
| 16 | family_member_publication_ref | 37 | PASS |
| 17 | international_application | 1 | PASS |
| 18 | ipc_techn_field | 1 | PASS |
| 19 | keyword | 59 | PASS |
| 20 | kind_code | 9 | PASS |
| 21 | language | 3 | PASS |
| 22 | legal_event_code | 5 | PASS |
| 23 | legal_status_event | 10 | PASS |
| 24 | natural_person | 61 | PASS |
| 25 | non_patent_citation | 297 | PASS |
| 26 | organization | 10 | PASS |
| 27 | patent | 19 | PASS |
| 28 | patent_agent | 12 | PASS |
| 29 | patent_applicant | 18 | PASS |
| 30 | patent_assignee | 9 | PASS |
| 31 | patent_citation | 805 | PASS |
| 32 | patent_citation_category | 789 | PASS |
| 33 | patent_classification | 71 | PASS |
| 34 | patent_examiner | 10 | PASS |
| 35 | patent_family | 3 | PASS |
| 36 | patent_family_member | 11 | PASS |
| 37 | patent_inventor | 32 | PASS |
| 38 | patent_keyword | 71 | PASS |
| 39 | person | 71 | PASS |
| 40 | priority_claim | 3 | PASS |
| 41 | publication | 19 | PASS |
| 42 | related_application | 11 | PASS |
| 43 | title | 30 | PASS |

- 空表数量：**1**
- 空表清单：family_citation

## 2. 简单 JOIN 验证

- 申请人三表 JOIN（patent→patent_applicant→person）：18 行
- 发明人三表 JOIN（patent→patent_inventor→person）：32 行
- 分类号 JOIN（patent→patent_classification）：71 行
- 引用表行数（patent_citation）：805 行
- 引用热度 TOP（citing_patent_id 分组）：9 行
- 权利要求 JOIN（publication→claim）：184 行
- 法律状态 JOIN（patent→legal_status_event）：10 行
