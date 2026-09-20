# 专利 XML 结构解析结果

- 输入: US20140338089A1-20141120.XML, US20140338090A1-20141120.XML, US20140345008P1-20141120.XML, US20140345009P1-20141120.XML
- 解析文档数: 4 (根元素: {'us-patent-application': 4})
- 元素路径数: 141

| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |
|---|---|---|---|---|---|---|
| `/us-patent-application` | 1 | 4/4 | 1 | 1 |  | country="US" date-produced="20141106" date-publ="20141120" dtd-version="v4.3 2012-12-04" |
| `/us-patent-application/abstract` | 1 | 4/4 | 1 | 1 |  | id="abstract" |
| `/us-patent-application/abstract/p` | 1 | 4/4 | 1 | 1 | A wetsuit comprising first panels exhibiting a high-stretch and adapted to provide buoyancy to the w | id="p-0001" num="0000" |
| `/us-patent-application/abstract/p/i` | 0..1 | 2/4 | 0 | 1 | Actinidia deliciosa \| Actinidia chinensis |  |
| `/us-patent-application/claims` | 1 | 4/4 | 1 | 1 |  | id="claims" |
| `/us-patent-application/claims/claim` | 1..N (max=20) | 4/4 | 1 | 20 |  | id="CLM-00001" id="CLM-00002" id="CLM-00003" id="CLM-00004" |
| `/us-patent-application/claims/claim/claim-text` | 1..N (max=20) | 4/4 | 1 | 20 |  |  |
| `/us-patent-application/claims/claim/claim-text/b` | 1..N (max=20) | 4/4 | 1 | 20 | 1 \| 2 |  |
| `/us-patent-application/claims/claim/claim-text/claim-ref` | 0..N (max=18) | 2/4 | 0 | 18 | claim 1 \| claim 1 | idref="CLM-00001" idref="CLM-00005" idref="CLM-00009" idref="CLM-00011" |
| `/us-patent-application/claims/claim/claim-text/claim-text` | 0..N (max=9) | 2/4 | 0 | 9 | at least one first panel exhibiting high-stretch and adapted to provide buoyancy to the wearer; \| a |  |
| `/us-patent-application/claims/claim/claim-text/i` | 0..1 | 2/4 | 0 | 1 | Actinidia deliciosa \| Actinidia chinensis |  |
| `/us-patent-application/description` | 1 | 4/4 | 1 | 1 |  | id="description" |
| `/us-patent-application/description/description-of-drawings` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/description/description-of-drawings/heading` | 1 | 4/4 | 1 | 1 | BRIEF DESCRIPTION OF THE DRAWINGS \| BRIEF DESCRIPTION OF THE SEVERAL VIEWS OF THE DRAWINGS | id="h-0004" id="h-0005" id="h-0006" id="h-0007" |
| `/us-patent-application/description/description-of-drawings/p` | 1..N (max=9) | 4/4 | 1 | 9 | Other characteristics and advantages of the invention will readily appear from the following descrip | id="p-0009" id="p-0014" id="p-0015" id="p-0016" |
| `/us-patent-application/description/description-of-drawings/p/figref` | 1..N (max=7) | 4/4 | 3 | 7 | FIG. 1 \| FIG. 2 | idref="DRAWINGS" |
| `/us-patent-application/description/description-of-drawings/p/i` | 0..1 | 1/4 | 0 | 1 | Actinidia |  |
| `/us-patent-application/description/heading` | 1..N (max=7) | 4/4 | 4 | 7 | FIELD OF THE INVENTION \| BACKGROUND OF THE INVENTION | id="h-0001" id="h-0002" id="h-0003" id="h-0004" |
| `/us-patent-application/description/p` | 1..N (max=77) | 4/4 | 8 | 77 | The instant invention relates to wetsuits and technical wetsuits for use in water sports such as sur | id="p-0002" id="p-0003" id="p-0004" id="p-0005" |
| `/us-patent-application/description/p/b` | 0..N (max=279) | 2/4 | 0 | 279 | 10 \| 100 |  |
| `/us-patent-application/description/p/figref` | 0..N (max=19) | 2/4 | 0 | 19 | FIG. 1 \| FIG. 1 | idref="DRAWINGS" |
| `/us-patent-application/description/p/i` | 0..N (max=52) | 3/4 | 0 | 52 | a \| a |  |
| `/us-patent-application/description/p/ul` | 0..N (max=2) | 3/4 | 0 | 2 |  | id="ul0001" id="ul0002" list-style="none" |
| `/us-patent-application/description/p/ul/li` | 0..N (max=20) | 3/4 | 0 | 20 | Botanical classification: \| Propagation: ‘MERLE’ can be successfully grafted onto rootstocks of | id="ul0001-0001" id="ul0001-0002" id="ul0001-0003" id="ul0001-0004" |
| `/us-patent-application/description/p/ul/li/i` | 0..N (max=3) | 2/4 | 0 | 3 | Actinidia deliciosa \| Actnidia deliciosa. |  |
| `/us-patent-application/description/p/ul/li/ul` | 0..N (max=6) | 3/4 | 0 | 6 |  | id="ul0002" id="ul0003" id="ul0004" id="ul0005" |
| `/us-patent-application/description/p/ul/li/ul/li` | 0..N (max=13) | 3/4 | 0 | 13 | the at least one second panel are located along specific muscles of the wearer in order to increase  | id="ul0002-0001" id="ul0002-0002" id="ul0002-0003" id="ul0002-0004" |
| `/us-patent-application/description/p/ul/li/ul/li/ul` | 0..N (max=6) | 2/4 | 0 | 6 |  | id="ul0003" id="ul0004" id="ul0005" id="ul0006" |
| `/us-patent-application/description/p/ul/li/ul/li/ul/li` | 0..N (max=63) | 2/4 | 0 | 63 |  | id="ul0003-0001" id="ul0003-0002" id="ul0003-0003" id="ul0003-0004" |
| `/us-patent-application/description/p/ul/li/ul/li/ul/li/i` | 0..N (max=64) | 2/4 | 0 | 64 | Age of the plant described \| Sex expression |  |
| `/us-patent-application/drawings` | 1 | 4/4 | 1 | 1 |  | id="DRAWINGS" |
| `/us-patent-application/drawings/figure` | 1..N (max=13) | 4/4 | 4 | 13 |  | id="Fig-EMI-D00000" id="Fig-EMI-D00001" id="Fig-EMI-D00002" id="Fig-EMI-D00003" |
| `/us-patent-application/drawings/figure/img` | 1..N (max=13) | 4/4 | 4 | 13 |  | alt="embedded image" file="US20140338089A1-20141120-D00000.TIF" file="US20140338089A1-20141120-D00001.TIF" file="US20140338089A1-20141120-D00002.TIF" |
| `/us-patent-application/us-bibliographic-data-application` | 1 | 4/4 | 1 | 1 |  | country="US" lang="EN" |
| `/us-patent-application/us-bibliographic-data-application/application-reference` | 1 | 4/4 | 1 | 1 |  | appl-type="plant" appl-type="utility" |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/date` | 1 | 4/4 | 1 | 1 | 20121102 \| 20140520 |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/doc-number` | 1 | 4/4 | 1 | 1 | 14355146 \| 14282878 |  |
| `/us-patent-application/us-bibliographic-data-application/assignees` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/address` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/address/city` | 0..1 | 1/4 | 0 | 1 | Lehi |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/address/country` | 0..1 | 1/4 | 0 | 1 | US |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/address/state` | 0..1 | 1/4 | 0 | 1 | UT |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/orgname` | 0..1 | 1/4 | 0 | 1 | Etre Vous, LLC |  |
| `/us-patent-application/us-bibliographic-data-application/assignees/assignee/addressbook/role` | 0..1 | 1/4 | 0 | 1 | 02 |  |
| `/us-patent-application/us-bibliographic-data-application/classification-national` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classification-national/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classification-national/main-classification` | 1 | 4/4 | 1 | 1 | 2 215 \| 2 22 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/action-date` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/action-date/date` | 0..1 | 2/4 | 0 | 1 | 20141120 \| 20141120 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/class` | 0..1 | 2/4 | 0 | 1 | 63 \| 43 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-data-source` | 0..1 | 2/4 | 0 | 1 | H \| H |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-status` | 0..1 | 2/4 | 0 | 1 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-value` | 0..1 | 2/4 | 0 | 1 | I \| I |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator/date` | 0..1 | 2/4 | 0 | 1 | 20130101 \| 20130101 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/generating-office` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/generating-office/country` | 0..1 | 2/4 | 0 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/main-group` | 0..1 | 2/4 | 0 | 1 | 11 \| 17 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/scheme-origination-code` | 0..1 | 2/4 | 0 | 1 | C \| C |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/section` | 0..1 | 2/4 | 0 | 1 | B \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/subclass` | 0..1 | 2/4 | 0 | 1 | C \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/subgroup` | 0..1 | 2/4 | 0 | 1 | 04 \| 02 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/symbol-position` | 0..1 | 2/4 | 0 | 1 | F \| F |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/action-date` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/action-date/date` | 1 | 4/4 | 1 | 1 | 20141120 \| 20141120 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/class` | 1 | 4/4 | 1 | 1 | 63 \| 43 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-data-source` | 1 | 4/4 | 1 | 1 | H \| H |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-level` | 1 | 4/4 | 1 | 1 | A \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-status` | 1 | 4/4 | 1 | 1 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-value` | 1 | 4/4 | 1 | 1 | I \| I |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/generating-office` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/generating-office/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/ipc-version-indicator` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/ipc-version-indicator/date` | 1 | 4/4 | 1 | 1 | 20060101 \| 20060101 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/main-group` | 1 | 4/4 | 1 | 1 | 11 \| 17 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/section` | 1 | 4/4 | 1 | 1 | B \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/subclass` | 1 | 4/4 | 1 | 1 | C \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/subgroup` | 1 | 4/4 | 1 | 1 | 04 \| 02 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/symbol-position` | 1 | 4/4 | 1 | 1 | F \| F |  |
| `/us-patent-application/us-bibliographic-data-application/invention-title` | 1 | 4/4 | 1 | 1 | Technical Wetsuit \| DANCE FOOTWEAR | id="d0e43" id="d0e61" |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/country` | 0..1 | 1/4 | 0 | 1 | WO |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/date` | 0..1 | 1/4 | 0 | 1 | 20121102 |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/doc-number` | 0..1 | 1/4 | 0 | 1 | PCT/IB2012/056118 |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/kind` | 0..1 | 1/4 | 0 | 1 | 00 |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/us-371c124-date` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/us-371c124-date/date` | 0..1 | 1/4 | 0 | 1 | 20140429 |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim` | 0..1 | 1/4 | 0 | 1 |  | kind="regional" sequence="01" |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/country` | 0..1 | 1/4 | 0 | 1 | EP |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/date` | 0..1 | 1/4 | 0 | 1 | 20111102 |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/doc-number` | 0..1 | 1/4 | 0 | 1 | 11306410.9 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/date` | 1 | 4/4 | 1 | 1 | 20141120 \| 20141120 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/doc-number` | 1 | 4/4 | 1 | 1 | 20140338089 \| 20140338090 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/kind` | 1 | 4/4 | 1 | 1 | A1 \| A1 |  |
| `/us-patent-application/us-bibliographic-data-application/us-application-series-code` | 1 | 4/4 | 1 | 1 | 14 \| 14 |  |
| `/us-patent-application/us-bibliographic-data-application/us-botanic` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-botanic/latin-name` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-botanic/variety` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor` | 1..N (max=3) | 4/4 | 1 | 3 |  | designation="us-only" sequence="00" sequence="01" sequence="02" |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook` | 1..N (max=3) | 4/4 | 1 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address` | 1..N (max=3) | 4/4 | 1 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address/city` | 1..N (max=3) | 4/4 | 1 | 3 | Torquay \| Biarrtz |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address/country` | 1..N (max=3) | 4/4 | 1 | 3 | AU \| FR |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address/state` | 0..1 | 1/4 | 0 | 1 | UT |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/first-name` | 1..N (max=3) | 4/4 | 1 | 3 | Troy \| Josh |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/last-name` | 1..N (max=3) | 4/4 | 1 | 3 | Brooks \| Rush |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant` | 1 | 4/4 | 1 | 1 |  | app-type="applicant" applicant-authority-category="assignee" designation="us-only" sequence="00" |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address/city` | 1 | 4/4 | 1 | 1 | Hungtington Beach \| Lehi |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address/state` | 0..1 | 2/4 | 0 | 1 | CA \| UT |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/first-name` | 0..1 | 2/4 | 0 | 1 | Donald Alfred \| Donald Alfred |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/last-name` | 0..1 | 2/4 | 0 | 1 | Skelton \| Skelton |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/orgname` | 0..1 | 2/4 | 0 | 1 | Quiksilver, Inc. \| Etre Vous, LLC |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/residence` | 1 | 4/4 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/residence/country` | 1 | 4/4 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents/us-provisional-application` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents/us-provisional-application/document-id` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents/us-provisional-application/document-id/country` | 0..1 | 1/4 | 0 | 1 | US |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents/us-provisional-application/document-id/date` | 0..1 | 1/4 | 0 | 1 | 20130520 |  |
| `/us-patent-application/us-bibliographic-data-application/us-related-documents/us-provisional-application/document-id/doc-number` | 0..1 | 1/4 | 0 | 1 | 61825415 |  |
| `/us-patent-application/us-claim-statement` | 0..1 | 3/4 | 0 | 1 | What is claimed is: \| What is claimed is: |  |
