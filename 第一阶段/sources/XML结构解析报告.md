# XML 结构解析报告（A角色 Step 2）

> 方法：用 `scripts/split_uspto_bulk_xml.py` 把 USPTO 批量 XML（同周期多篇文档直接拼接）拆成单文档，再用 `scripts/analyze_patent_xml.py` 遍历全部元素，统计**元素路径、单文档出现次数（min/max）、样例值、属性**。
> 样例来源见 `来源清单.md` W8–W10（第三方公开仓库中的 USPTO 样例镜像，DOCTYPE 分别为 `us-patent-application-v46-2022-02-17.dtd`、`us-patent-grant-v47-2022-02-17.dtd`）。
> 明细：`XML结构解析-美国专利申请公布.csv/.md`、`XML结构解析-美国专利授权公告.csv/.md`、`XML结构解析-美国外观设计授权.csv/.md`（本目录）。
> 说明：本报告只描述**实际解析到的内容**；未在样例中出现的 DTD 元素一律标注“样例未见，按 DTD/规范建模”，不虚构样例值。

## 0. 总览

| 样例类型 | 根元素 | 解析文档数 | 元素路径数 | 文件大小/文档数（拆分前） |
|---|---|---|---|---|
| 美国申请公布 | `us-patent-application` | 2 | 130 | 20.8 MB / 207 篇 |
| 美国授权公告（发明 B1） | `us-patent-grant` | 2 | 163 | 4.76 MB / 208 篇 |
| 美国外观设计授权（S1） | `us-patent-grant` | 2 | 110 | 同上 |

根元素属性：`lang`、`dtd-version`、`file`、`status`、`id`、`country`、`date-produced`、`date-publ`。
**重要工程问题**：整份批量文件不是合法 XML（多个 XML 声明/根元素顺序拼接），直接 `ElementTree.parse()` 会报 `junk after document element`，导入脚本必须按 `<?xml` 声明切分或流式解析（已写脚本，B/C可复用）。

## 1. 美国申请公布（us-patent-application）结构要点

```
us-patent-application
├── us-bibliographic-data-application
│   ├── publication-reference/document-id/{country,doc-number,kind,date}      ← 公布号/种类/公布日
│   ├── application-reference[@appl-type]/document-id/{country,doc-number,date} ← 申请号/申请日
│   ├── us-application-series-code
│   ├── priority-claims/priority-claim[@sequence,@kind]/{country,doc-number,date}
│   ├── classifications-ipcr/classification-ipcr/{section,class,subclass,main-group,subgroup,classification-level,symbol-position,classification-value,ipc-version-indicator/date,generating-office/country,action-date/date,classification-status,classification-data-source}   （单文档 2..3 条）
│   ├── classifications-cpc/main-cpc/classification-cpc 与 further-cpc/classification-cpc（含 cpc-version-indicator、scheme-origination-code、symbol-position、classification-value）
│   ├── pct-or-regional-filing-data/document-id/{country,doc-number,date}、us-371c12-date/date
│   ├── invention-title[@id]
│   └── us-parties
│       ├── inventors/inventor[@sequence,@designation]/addressbook/{first-name,last-name,address/{city,country}}
│       └── us-applicants/us-applicant[@appl-type,@applicant-authority-category]/addressbook/{first-name,last-name,orgname,address/{city,country}}、residence/country
├── abstract/p[@id,@num]
├── drawings/figure/img[@id,@alt,@file]                          （图 8..14 幅）
├── description/{heading,p,...}（p 嵌套 b/i/figref/ul/li，`figref/b` 指向附图号；单文档 p 最多 104）
└── claims/claim[@id]/claim-text（可嵌套 claim-text；`claim-ref[@idref]` 指向另一条权利要求，如 `claim 1`）
```

**多值证据（2篇样例的 min–max）**：`claims/claim` 7–20；`claim-text` 7–20（可再嵌套）；`claim-ref` 5–19（→从属权利要求）；`classification-ipcr` 2–3；`further-cpc/classification-cpc` 1–2；`priority-claim` 1；`inventor`/`us-applicant` 样例中各 1（真实数据为 1..N）。

## 2. 美国授权公告（us-patent-grant）结构要点

```
us-patent-grant
├── us-bibliographic-data-grant
│   ├── publication-reference/document-id/{country,doc-number,kind,date}
│   ├── application-reference[@appl-type]/document-id/{country,doc-number,date}
│   ├── us-application-series-code
│   ├── us-term-of-grant/length-of-grant                            ← 保护期（授权特有）
│   ├── classification-locarno/{edition,main-classification}        ← 外观设计特有（design 样例）
│   ├── classification-national/{country,main-classification,further-classification}
│   ├── us-field-of-classification-search/classification-national/{country,main-classification,additional-info}  ← 审查员检索领域，单文档 1..9
│   ├── us-references-cited/us-citation
│   │   ├── patcit[@num]/document-id/{country,doc-number,kind,date,name}, category
│   │   ├── nplcit[@num]/othercit                                  ← 非专利文献（可为 URL）
│   │   ├── classification-national、classification-cpc-text
│   │   （us-citation 单文档最多 47 条；patcit 最多 42；nplcit 最多 5）
│   ├── assignees/assignee/addressbook/{orgname,role,address/{city,state,country}}
│   ├── examiners/primary-examiner/{first-name,last-name,department} ← 审查员＋审查部门
│   ├── invention-title、number-of-claims
│   └── us-parties
│       ├── agents/agent[@rep-type,@sequence]/addressbook/{first-name,last-name,orgname,address/country}  ← 代理人/机构
│       └── us-applicants/us-applicant/residence/country
├── abstract/p[@id,@num]
├── drawings/figure[@id]/img[@id,@alt,@file]（最多 19 幅）
├── description/{heading,p,b,i,figref,ul/li}（p 最多 43）
└── claims/claim[@id]/claim-text（最多 18 条）、claim-ref[@idref]
```

外观设计（S1）差异：无 `claims` 全文，仅有 `number-of-claims`、`us-exemplary-claim`；使用 `classification-locarno`；`claim` 章节标题为 “CLAIM”。

## 3. 关键数据特征（直接影响数据库设计）

| # | 特征 | 证据（样例） | 设计影响 |
|---|---|---|---|
| 1 | 一个批量文件含多篇文档，整体非法 XML | 申请公布 20.8MB/207 篇；授权 4.76MB/208 篇 | 导入脚本先切分/流式解析 |
| 2 | 日期有两种精度 | 全日期 `20230105`；引用文献月精度 `20131200`、`20190200` | 日精度才填 DATE；`YYYYMM00` 的 DATE 置 NULL 并保留 `*_date_raw`，不伪造 1 日 |
| 3 | 权利要求从属关系用 `claim-ref@idref` 指向 `claim@id` | `<claim-ref idref="CLM-00001">claim 1</claim-ref>` | `claim_dependency` 自引用表（依赖方→被依赖方） |
| 4 | 引用分专利/非专利，且带类别与序号 | `us-citation/category`（如 `cited by examiner`）、`patcit@num`、`nplcit@num/othercit` | `patent_citation`＋`non_patent_citation`＋`citation_category` |
| 5 | 被引文献可能不在本地库 | patcit 的 country/doc-number/kind 可为任意局 | 引用表需“外文库外文献”字段（country/number/kind/date），`cited_patent_id` 可为空 |
| 6 | 分类号有层级与角色属性 | IPC section→class→subclass→main-group/subgroup；`symbol-position` F/L、`classification-value` I/E、`classification-level`、generating-office | `patent_classification` 存符号＋角色字段；`classification_scheme` 维表 |
| 7 | 同一申请有公布（A1）与授权（B1/B2）两份文献 | 申请与授权样例的 publication-reference 不同 | `patent`（申请案）1:N `publication` |
| 8 | 多语言 | 根元素 `lang="EN"`；EP 数据含 DE/FR/EN | `title`/`abstract` 带语言列，与 `language` 维表关联 |
| 9 | 长文本且结构嵌套 | `description/p`（最多 104 段）、`claims/claim-text`、`abstract/p` | TEXT/LONGTEXT；说明书按章节/段落拆 `description_section` |
| 10 | XML 实体转义与内嵌元素 | 文本含 `&amp;` 等实体，`b/i/figref` 混排 | 入库前统一去标签取文本；特殊字符由驱动参数化处理 |
| 11 | 人员机构混用 first/last/orgname，地址为自由文本 | `addressbook/orgname`、`address/{city,state,country}` | `person` 统一建模，角色由关联表表达 |
| 12 | 国际申请数据 | `pct-or-regional-filing-data`、`us-371c12-date` | `international_application`（INID 86/87/85） |

## 4. 与 EP/DOCDB 的对应关系（来源：PATSTAT 第三方镜像，见来源清单 W6/W7）

- `publication-reference` → DOCDB `tls211_pat_publn`（`publn_auth/publn_nr/publn_kind/publn_date/appln_id`）。
- `application-reference` + `us-application-series-code` → `tls201_appln`（`appln_auth/appln_nr/appln_kind/appln_filing_date`）。
- `invention-title` → `tls202_appln_title`（`appln_title_lg/appln_title`）。
- `abstract/p` → `tls203_appln_abstr`（`appln_abstract_lg/appln_abstract`）。
- `priority-claim` → `tls204_appln_prior`。
- `us-parties`/`assignees`/`agents`/`examiners` → `tls206_person` + `tls207_pers_appln`。
- `classification-ipcr` → `tls209_appln_ipc`；`classification-national` → `tls210_appln_n_cls`（美国为 USPC）；`classification-cpc` → `tls224_appln_cpc`。
- `us-references-cited/us-citation` → `tls212_citation`（专利引用）＋`tls214_npl_publn`（非专利）＋`tls215_citn_categ`（类别）。
- 专利族 → `tls218_docdb_fam` / `tls219_inpadoc_fam`（→ 本设计 `patent_family`/`patent_family_member`）。
- 族级引用 → `tls228_docdb_fam_citn`（→ `family_citation`）。
- 法律状态 → `tls231_inpadoc_legal_event`（→ `legal_status_event`）。
- 国家码/法律事件码/技术领域 → `tls801_country`/`tls803_legal_event_code`/`tls901_techn_field_ipc`（→ `country_office`/`legal_event_code`/`ipc_techn_field`）。

> 上述映射已使用本地归档的四份官网手册与官网样例复核；第三方 PATSTAT 镜像仅作字段命名交叉验证。

## 5. 复现方式

```bash
# 拆分批量 XML（示例）
python3 scripts/split_uspto_bulk_xml.py sample_patent_grants.xml samples/ 2
# 结构统计（输入可为单文件或目录）
python3 scripts/analyze_patent_xml.py samples/ analysis_grant 2
```

---

# 官网样例解析结果（2026-09-15 更新，**主依据**）

> 组员已下载四类数据的官网手册与样例（`sources/官网资料/`、`sources/samples/官网/`），本节取代前述第三方样例作为**主依据**；第三方样例仅用于新旧 DTD 版本差异对照（见 §9）。

## 6. 官网样例总览

| 数据集 | 根元素 | 文档数 | 元素路径数 | DTD/模式 | 官网手册 |
|---|---|---|---|---|---|
| 美国申请公布 | `us-patent-application` | 4（A1×2、P1×2） | 141 | `us-patent-application-v43-2012-12-04.dtd` | US-PA-TXTO-10-A |
| 美国授权公告 | `us-patent-grant` | 8（B2、S1、PP、RE） | 262 | `us-patent-grant-v44-2013-05-16.dtd` | US-PA-TXTO-10-B |
| 欧洲专利全文 | `ep-patent-document` | 4（A、B1） | 190 | `ep-patent-document-v1-4` | EP-PA-TXTO-10-AB |
| EP DOCDB 摘要 | `exchange-document`（包装根为 `exchange-documents`） | 2 | 92 | `exchange-documents-v2.5.7.xsd` | EP-PA-ABSO-10-AB |

明细文件：`XML结构解析-官网美国专利申请公布.*`、`XML结构解析-官网美国专利授权公告.*`、`XML结构解析-官网欧洲专利全文.*`、`XML结构解析-官网EP-DOCDB摘要.*`。

## 7. 美国样例要点（与设计核对）

- **申请公布**：`publication-reference`（A1）、`application-reference/@appl-type`（utility/plant）、`us-application-series-code`、`priority-claims`（kind=national/regional）、`classifications-ipcr`、`classifications-cpc`（main/further）、`classification-national`（USPC）、`us-parties/{inventors,us-applicants}`（样例 3 位发明人）、`assignees`、`us-related-documents/us-provisional-application`、`us-botanic`、`abstract`、`drawings/figure/img`、`description`、`claims/claim`。
- **授权公告**：在申请公布元素基础上，确认 `us-term-of-grant/length-of-grant|us-term-extension`、`classification-locarno/{edition,main-classification}`、`figures/{number-of-drawing-sheets,number-of-figures}`、`number-of-claims`、`examiners/{primary-examiner,assistant-examiner}`（含 `department`）、`us-field-of-classification-search/{classification-national,classification-cpc-text}`、`us-references-cited/us-citation`（patcit 结构化、nplcit/othercit 文本、category="cited by examiner"/"cited by applicant"）、`us-related-documents`（`us-provisional-application`、`continuation-in-part/relation/{child-doc,parent-doc,parent-status}`、`related-publication`）。
- **多值实测**（官网授权 8 篇）：`us-citation` 最多 **690** 条、`patcit` 最多 **404**、`claims/claim` 最多 33、`classification-ipcr` 最多 8、`further-cpc` 最多 16、`inventors` 最多 3；引用日期含月精度 `19740100`（同前报告结论）。大引用量说明引用表必须 1:N 拆表并建索引。
- 与设计差异：新增 `patent.botanic_*`、`publication.{number_of_figures,number_of_drawing_sheets,term_extension_days}`、`related_application.parent_status`、`classification.edition`（已在 `02` §8 落地）。

## 8. 欧洲样例要点（EP 全文 + DOCDB）

### 8.1 EP 全文（ST.36 B 系列元素，官网手册 PDF p.5–9）

- `ep-patent-document` 属性：`id/file/lang/country/doc-number/kind/date-publ/status/dtd-version`。
- `SDOBI`（=bibliographic-data）下：`B100`（公开：B110 号/B120 类型文字/B130 种类/B140 日期/B190 局）、`B200`（申请：B210/B220/B240 权利生效/B250-B260 语言）、`B300`（优先权：B310/B320/B330）、`B400`（公开级别：B405 公报、B430/B450、B452EP 拟授权日）、`B500`（B510EP IPC、B540 标题 B541 语言/B542 文本、B560 引用 B561 专利文本/B562 非专利文本/B565EP）、`B700`（B710 申请人 B711/申请人名/iid/irf/adr、B720 发明人 B721、B730 权利人 B731、B740 代理人 B741）、`B800`（B840 指定国、B844EP/B845EP 延伸国、B860/B861 国际申请、B870/B871 国际公布、B880 检索报告）、`B900`（B910 PCT 失效）。
- 正文：`description/{heading,p,...}`（p 内可含 `figref/tables(CALS)/dl/ol/ul/nplcit/patcit`）、`claims`、`abstract`（**4 篇样例均无 abstract**，摘要以 DOCDB 数据为准）。
- **关键修正**：`<claims id="claims01" lang="en">`、`<claim id="c-en-01-0001" num="0001">` —— 权利要求**按语言分套**，`claim` 表需含 `lang_code`。

### 8.2 EP DOCDB（exchange-documents v2.5.7）

- `exchange-documents`（属性：date-of-exchange/dtd-version/file/no-of-documents/originating-office）
  - `exchange-document`（属性：**country/doc-number/kind/doc-id/date-publ/family-id/is-representative/date-of-last-exchange/date-of-previous-exchange/date-added-docdb/originating-office/status**）
    - `bibliographic-data`：`publication-reference`（可多条）、`classification-ipc`（1–7 版，main/further-classification）、`classifications-ipcr`（第 8 版 `text` 串）、`patent-classifications`（scheme/symbol/position/value/source）、`application-reference`（多 `data-format`：docdb/epodoc/original）、`language-of-filing/publication`、`priority-claims`（含 `priority-active-indicator`）、`parties/{applicants/applicant/applicant-name/name, residence, inventors/inventor/inventor-name/name}`、`designation-of-states/designation-epc/contracting-states/country`、`invention-title`（多语言）、`dates-of-public-availability/{examined-printed-without-grant,unexamined-printed-without-grant}/document-id/date`、`references-cited/citation[@cited-phase,@sequence]/{patcit[@dnum,...]/document-id, nplcit[@npl-type,@num]/text}`
    - `abstract`（多条，属性 `lang/data-format/abstract-source`）
    - `patent-family`（族）：`family-member/publication-reference` 与 `family-member/application-reference`（含 `@is-representative`），另有族级 `abstract`
- 与设计差异：新增 `publication.{docdb_doc_id,date_added_docdb}`、`abstract.{data_format,abstract_source}`、`title.data_format`、`patent_citation.cited_raw_text`；族成员的多格式申请号、多份公布文献和族级摘要分别落入 `family_member_application_ref`、`family_member_publication_ref`、`family_abstract`。

**分析器修正说明（2026-09-18）**：旧版将 DOCDB 包装根当成 1 篇文档，且路径在部分文档缺失时没有把 0 计入最小出现次数。脚本现先切分 `exchange-document`，再对每个逻辑文档统计，因此为 2 篇/92 路径，`0..1`/`0..N` 口径可复现。

## 9. 新旧 DTD 版本差异（官网 v4.3/v4.4 vs 第三方 v4.6/v4.7）

| 项 | 官网样例（2012–2014） | 第三方样例（2022） | 导入建议 |
|---|---|---|---|
| DTD | 申请 v4.3 / 授权 v4.4 | 申请 v4.6 / 授权 v4.7 | 按“并集”解析；对可选元素做空值保护 |
| `us-references-cited` | v4.4 已为 `us-references-cited` | v4.7 同 | 一致 |
| 引用 `patcit` 结构 | country/doc-number/kind/date/name | 同 + 更多种类 | 统一按设计字段映射 |
| 分类 | `classifications-ipcr` + `classifications-cpc` | 同（CPC 更细） | `symbol_raw` 保留原文串 |
| 族/摘要 | 官网无 DOCDB 族字段（在 DOCDB 数据） | 同 | 以 DOCDB 交换文件为准 |
| 权利要求 | `claims/claim@id/@num` | 同 | v4.3+ 均可用 `xml_claim_id` 解析依赖 |

> 复现命令：
> ```bash
> python3 scripts/analyze_patent_xml.py /path/to/samples sources/XML结构解析-官网<名称> 6
> ```
