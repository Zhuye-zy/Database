# 专利 XML 结构解析结果

- 输入: us-patent-application-20230000001.xml, us-patent-application-20230000002.xml
- 解析文档数: 2 (根元素: {'us-patent-application': 2})
- 元素路径数: 130

| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |
|---|---|---|---|---|---|---|
| `/us-patent-application` | 1 | 2/2 | 1 | 1 |  | country="US" date-produced="20221220" date-produced="20221221" date-publ="20230105" |
| `/us-patent-application/abstract` | 1 | 2/2 | 1 | 1 |  | id="abstract" |
| `/us-patent-application/abstract/p` | 1 | 2/2 | 1 | 1 | An assembled garden tool, including a tine, a base, and a tenon plate. The tine includes a blade par | id="p-0001" num="0000" |
| `/us-patent-application/claims` | 1 | 2/2 | 1 | 1 |  | id="claims" |
| `/us-patent-application/claims/claim` | 1..N (max=20) | 2/2 | 7 | 20 |  | id="CLM-00001" id="CLM-00002" id="CLM-00003" id="CLM-00004" |
| `/us-patent-application/claims/claim/claim-text` | 1..N (max=20) | 2/2 | 7 | 20 |  |  |
| `/us-patent-application/claims/claim/claim-text/b` | 1..N (max=20) | 2/2 | 8 | 20 | 1 \| 2 |  |
| `/us-patent-application/claims/claim/claim-text/claim-ref` | 1..N (max=19) | 2/2 | 5 | 19 | claim 1 \| claim 2 | idref="CLM-00001" idref="CLM-00002" idref="CLM-00003" idref="CLM-00005" |
| `/us-patent-application/claims/claim/claim-text/claim-text` | 1..N (max=32) | 2/2 | 14 | 32 | wherein the tine comprises a blade part and a connecting part, and the connecting part is defined wi |  |
| `/us-patent-application/description` | 1 | 2/2 | 1 | 1 |  | id="description" |
| `/us-patent-application/description/description-of-drawings` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/description/description-of-drawings/heading` | 1 | 2/2 | 1 | 1 | BRIEF DESCRIPTION OF THE DRAWINGS \| BRIEF DESCRIPTION OF THE DRAWINGS | id="h-0004" id="h-0005" level="1" |
| `/us-patent-application/description/description-of-drawings/p` | 1..N (max=13) | 2/2 | 8 | 13 | To illustrate the technical solutions according to the embodiment of the present invention or in the | id="p-0019" id="p-0020" id="p-0021" id="p-0022" |
| `/us-patent-application/description/description-of-drawings/p/figref` | 1..N (max=16) | 2/2 | 7 | 16 | FIG. \| FIG. | idref="DRAWINGS" |
| `/us-patent-application/description/description-of-drawings/p/figref/b` | 1..N (max=16) | 2/2 | 7 | 16 | 1 \| 2 |  |
| `/us-patent-application/description/heading` | 1..N (max=6) | 2/2 | 5 | 6 | TECHNICAL FIELD \| BACKGROUND | id="h-0001" id="h-0002" id="h-0003" id="h-0004" |
| `/us-patent-application/description/p` | 1..N (max=104) | 2/2 | 42 | 104 | The present disclosure relates to a garden tool, in particular to an assembled garden tool. \| Garde | id="p-0002" id="p-0003" id="p-0004" id="p-0005" |
| `/us-patent-application/description/p/b` | 1..N (max=1027) | 2/2 | 134 | 1027 | 1 \| 2 |  |
| `/us-patent-application/description/p/figref` | 1..N (max=28) | 2/2 | 2 | 28 | FIG. \| FIG. | idref="DRAWINGS" |
| `/us-patent-application/description/p/figref/b` | 1..N (max=38) | 2/2 | 2 | 38 | 1 \| 7 |  |
| `/us-patent-application/description/p/i` | 1..N (max=262) | 1/2 | 262 | 262 | o \| p |  |
| `/us-patent-application/description/p/ul` | 1 | 1/2 | 1 | 1 |  | id="ul0001" list-style="none" |
| `/us-patent-application/description/p/ul/li` | 1 | 1/2 | 1 | 1 |  | id="ul0001-0001" num="0000" |
| `/us-patent-application/description/p/ul/li/ul` | 1 | 1/2 | 1 | 1 |  | id="ul0002" list-style="none" |
| `/us-patent-application/description/p/ul/li/ul/li` | 1 | 1/2 | 1 | 1 |  | id="ul0002-0001" num="0037" |
| `/us-patent-application/description/p/ul/li/ul/li/b` | 1..N (max=22) | 1/2 | 22 | 22 | 1 \| 2 |  |
| `/us-patent-application/drawings` | 1 | 2/2 | 1 | 1 |  | id="DRAWINGS" |
| `/us-patent-application/drawings/figure` | 1..N (max=14) | 2/2 | 8 | 14 |  | id="Fig-EMI-D00000" id="Fig-EMI-D00001" id="Fig-EMI-D00002" id="Fig-EMI-D00003" |
| `/us-patent-application/drawings/figure/img` | 1..N (max=14) | 2/2 | 8 | 14 |  | alt="embedded image" file="US20230000001A1-20230105-D00000.TIF" file="US20230000001A1-20230105-D00001.TIF" file="US20230000001A1-20230105-D00002.TIF" |
| `/us-patent-application/us-bibliographic-data-application` | 1 | 2/2 | 1 | 1 |  | country="US" lang="EN" |
| `/us-patent-application/us-bibliographic-data-application/application-reference` | 1 | 2/2 | 1 | 1 |  | appl-type="utility" |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 20210630 \| 20200904 |  |
| `/us-patent-application/us-bibliographic-data-application/application-reference/document-id/doc-number` | 1 | 2/2 | 1 | 1 | 17364781 \| 17780947 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc` | 1..N (max=2) | 2/2 | 1 | 2 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/action-date` | 1..N (max=2) | 2/2 | 1 | 2 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/action-date/date` | 1..N (max=2) | 2/2 | 1 | 2 | 20230105 \| 20230105 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/class` | 1..N (max=2) | 2/2 | 1 | 2 | 01 \| 01 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/classification-data-source` | 1..N (max=2) | 2/2 | 1 | 2 | H \| H |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/classification-status` | 1..N (max=2) | 2/2 | 1 | 2 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/classification-value` | 1..N (max=2) | 2/2 | 1 | 2 | I \| I |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/cpc-version-indicator` | 1..N (max=2) | 2/2 | 1 | 2 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/cpc-version-indicator/date` | 1..N (max=2) | 2/2 | 1 | 2 | 20130101 \| 20130101 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/generating-office` | 1..N (max=2) | 2/2 | 1 | 2 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/generating-office/country` | 1..N (max=2) | 2/2 | 1 | 2 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/main-group` | 1..N (max=2) | 2/2 | 1 | 2 | 1 \| 1 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/scheme-origination-code` | 1..N (max=2) | 2/2 | 1 | 2 | C \| C |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/section` | 1..N (max=2) | 2/2 | 1 | 2 | A \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/subclass` | 1..N (max=2) | 2/2 | 1 | 2 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/subgroup` | 1..N (max=2) | 2/2 | 1 | 2 | 08 \| 10 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/further-cpc/classification-cpc/symbol-position` | 1..N (max=2) | 2/2 | 1 | 2 | L \| L |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/action-date` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/action-date/date` | 1 | 2/2 | 1 | 1 | 20230105 \| 20230105 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/class` | 1 | 2/2 | 1 | 1 | 01 \| 01 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-data-source` | 1 | 2/2 | 1 | 1 | H \| H |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-status` | 1 | 2/2 | 1 | 1 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/classification-value` | 1 | 2/2 | 1 | 1 | I \| I |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator/date` | 1 | 2/2 | 1 | 1 | 20130101 \| 20130101 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/generating-office` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/generating-office/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/main-group` | 1 | 2/2 | 1 | 1 | 1 \| 59 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/scheme-origination-code` | 1 | 2/2 | 1 | 1 | C \| C |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/section` | 1 | 2/2 | 1 | 1 | A \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/subclass` | 1 | 2/2 | 1 | 1 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/subgroup` | 1 | 2/2 | 1 | 1 | 227 \| 043 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-cpc/main-cpc/classification-cpc/symbol-position` | 1 | 2/2 | 1 | 1 | F \| F |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/action-date` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/action-date/date` | 1..N (max=3) | 2/2 | 2 | 3 | 20230105 \| 20230105 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/class` | 1..N (max=3) | 2/2 | 2 | 3 | 01 \| 01 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-data-source` | 1..N (max=3) | 2/2 | 2 | 3 | H \| H |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-level` | 1..N (max=3) | 2/2 | 2 | 3 | A \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-status` | 1..N (max=3) | 2/2 | 2 | 3 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/classification-value` | 1..N (max=3) | 2/2 | 2 | 3 | I \| I |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/generating-office` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/generating-office/country` | 1..N (max=3) | 2/2 | 2 | 3 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/ipc-version-indicator` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/ipc-version-indicator/date` | 1..N (max=3) | 2/2 | 2 | 3 | 20060101 \| 20060101 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/main-group` | 1..N (max=3) | 2/2 | 2 | 3 | 1 \| 1 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/section` | 1..N (max=3) | 2/2 | 2 | 3 | A \| A |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/subclass` | 1..N (max=3) | 2/2 | 2 | 3 | B \| B |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/subgroup` | 1..N (max=3) | 2/2 | 2 | 3 | 22 \| 08 |  |
| `/us-patent-application/us-bibliographic-data-application/classifications-ipcr/classification-ipcr/symbol-position` | 1..N (max=3) | 2/2 | 2 | 3 | F \| L |  |
| `/us-patent-application/us-bibliographic-data-application/invention-title` | 1 | 2/2 | 1 | 1 | ASSEMBLED GARDEN TOOL \| TRACTOR | id="d2e43" id="d2e61" |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data` | 1 | 1/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id` | 1 | 1/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/country` | 1 | 1/2 | 1 | 1 | WO |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/date` | 1 | 1/2 | 1 | 1 | 20200904 |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/document-id/doc-number` | 1 | 1/2 | 1 | 1 | PCT/JP2020/033620 |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/us-371c12-date` | 1 | 1/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/pct-or-regional-filing-data/us-371c12-date/date` | 1 | 1/2 | 1 | 1 | 20220527 |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims` | 1 | 1/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim` | 1 | 1/2 | 1 | 1 |  | kind="national" sequence="01" |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/country` | 1 | 1/2 | 1 | 1 | JP |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/date` | 1 | 1/2 | 1 | 1 | 20191227 |  |
| `/us-patent-application/us-bibliographic-data-application/priority-claims/priority-claim/doc-number` | 1 | 1/2 | 1 | 1 | 2019-239059 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 20230105 \| 20230105 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/doc-number` | 1 | 2/2 | 1 | 1 | 20230000001 \| 20230000002 |  |
| `/us-patent-application/us-bibliographic-data-application/publication-reference/document-id/kind` | 1 | 2/2 | 1 | 1 | A1 \| A1 |  |
| `/us-patent-application/us-bibliographic-data-application/us-application-series-code` | 1 | 2/2 | 1 | 1 | 17 \| 17 |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor` | 1 | 2/2 | 1 | 1 |  | designation="us-only" sequence="00" |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address/city` | 1 | 2/2 | 1 | 1 | Taiyuan \| Sakai-shi |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/address/country` | 1 | 2/2 | 1 | 1 | CN \| JP |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/first-name` | 1 | 2/2 | 1 | 1 | Weinan \| Katsumi |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/inventors/inventor/addressbook/last-name` | 1 | 2/2 | 1 | 1 | WU \| YANAGIHARA |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant` | 1 | 2/2 | 1 | 1 |  | app-type="applicant" applicant-authority-category="assignee" designation="us-only" sequence="00" |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address/city` | 1 | 2/2 | 1 | 1 | Taiyuan \| Osaka-shi, Osaka |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/address/country` | 1 | 2/2 | 1 | 1 | CN \| JP |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/first-name` | 1 | 1/2 | 1 | 1 | Weinan |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/last-name` | 1 | 1/2 | 1 | 1 | WU |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/addressbook/orgname` | 1 | 1/2 | 1 | 1 | KUBOTA CORPORATION |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/residence` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-application/us-bibliographic-data-application/us-parties/us-applicants/us-applicant/residence/country` | 1 | 2/2 | 1 | 1 | CN \| JP |  |
