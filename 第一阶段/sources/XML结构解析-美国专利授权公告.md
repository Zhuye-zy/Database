# 专利 XML 结构解析结果

- 输入: us-patent-grant-11540449-B1.xml, us-patent-grant-11542074-B1.xml
- 解析文档数: 2 (根元素: {'us-patent-grant': 2})
- 元素路径数: 163

| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |
|---|---|---|---|---|---|---|
| `/us-patent-grant` | 1 | 2/2 | 1 | 1 |  | country="US" date-produced="20221214" date-publ="20230103" dtd-version="v4.7 2022-02-17" |
| `/us-patent-grant/abstract` | 1 | 2/2 | 1 | 1 |  | id="abstract" |
| `/us-patent-grant/abstract/p` | 1 | 2/2 | 1 | 1 | A gardening shears includes a shank having an elongated groove, a first handle connected to the bott | id="p-0001" num="0000" |
| `/us-patent-grant/claims` | 1 | 2/2 | 1 | 1 |  | id="claims" |
| `/us-patent-grant/claims/claim` | 1..N (max=18) | 2/2 | 3 | 18 |  | id="CLM-00001" id="CLM-00002" id="CLM-00003" id="CLM-00004" |
| `/us-patent-grant/claims/claim/claim-text` | 1..N (max=18) | 2/2 | 3 | 18 | 1. A gardening shears comprising: \| 2. The gardening shears as claimed in |  |
| `/us-patent-grant/claims/claim/claim-text/claim-ref` | 1..N (max=15) | 2/2 | 2 | 15 | claim 1 \| claim 1 | idref="CLM-00001" idref="CLM-00002" idref="CLM-00003" idref="CLM-00004" |
| `/us-patent-grant/claims/claim/claim-text/claim-text` | 1..N (max=8) | 2/2 | 7 | 8 | a shank provided near a top end thereof with an elongated groove; \| a first handle connected to a b |  |
| `/us-patent-grant/claims/claim/claim-text/claim-text/claim-text` | 1..N (max=10) | 1/2 | 10 | 10 | a straw body having an upper portion and a lower portion; \| a cap attached to the upper portion by  |  |
| `/us-patent-grant/description` | 1 | 2/2 | 1 | 1 |  | id="description" |
| `/us-patent-grant/description/description-of-drawings` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/description/description-of-drawings/heading` | 1 | 2/2 | 1 | 1 | BRIEF DESCRIPTION OF THE DRAWINGS \| BRIEF DESCRIPTION OF THE DRAWINGS | id="h-0004" id="h-0005" level="1" |
| `/us-patent-grant/description/description-of-drawings/p` | 1..N (max=34) | 2/2 | 6 | 34 | Various exemplary embodiments of this disclosure will be described in detail, wherein like reference | id="p-0009" id="p-0010" id="p-0011" id="p-0012" |
| `/us-patent-grant/description/description-of-drawings/p/figref` | 1..N (max=37) | 2/2 | 6 | 37 | FIG. \| FIG. | idref="DRAWINGS" |
| `/us-patent-grant/description/description-of-drawings/p/figref/b` | 1..N (max=37) | 2/2 | 6 | 37 | 1 \| 2 |  |
| `/us-patent-grant/description/heading` | 1..N (max=5) | 2/2 | 4 | 5 | BACKGROUND OF THE INVENTION \| 1. Field of the Invention | id="h-0001" id="h-0002" id="h-0003" id="h-0004" |
| `/us-patent-grant/description/p` | 1..N (max=43) | 2/2 | 21 | 43 | The present invention relates to gardening shears and more particularly, to a gardening shears havin | id="p-0002" id="p-0003" id="p-0004" id="p-0005" |
| `/us-patent-grant/description/p/b` | 1..N (max=547) | 2/2 | 144 | 547 | 10 \| 20 |  |
| `/us-patent-grant/description/p/figref` | 1..N (max=59) | 2/2 | 11 | 59 | FIGS. \| FIGS. | idref="DRAWINGS" |
| `/us-patent-grant/description/p/figref/b` | 1..N (max=77) | 2/2 | 15 | 77 | 1 \| 5 |  |
| `/us-patent-grant/description/p/i` | 1..N (max=7) | 1/2 | 7 | 7 | a. \| a |  |
| `/us-patent-grant/drawings` | 1 | 2/2 | 1 | 1 |  | id="DRAWINGS" |
| `/us-patent-grant/drawings/figure` | 1..N (max=19) | 2/2 | 7 | 19 |  | id="Fig-EMI-D00000" id="Fig-EMI-D00001" id="Fig-EMI-D00002" id="Fig-EMI-D00003" |
| `/us-patent-grant/drawings/figure/img` | 1..N (max=19) | 2/2 | 7 | 19 |  | alt="embedded image" file="US11540449-20230103-D00000.TIF" file="US11540449-20230103-D00001.TIF" file="US11540449-20230103-D00002.TIF" |
| `/us-patent-grant/us-bibliographic-data-grant` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/application-reference` | 1 | 2/2 | 1 | 1 |  | appl-type="utility" |
| `/us-patent-grant/us-bibliographic-data-grant/application-reference/document-id` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/application-reference/document-id/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/application-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 20210701 \| 20210702 |  |
| `/us-patent-grant/us-bibliographic-data-grant/application-reference/document-id/doc-number` | 1 | 2/2 | 1 | 1 | 17365370 \| 17367159 |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/address` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/address/city` | 1 | 2/2 | 1 | 1 | Taichung \| Van Nuys |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/address/country` | 1 | 2/2 | 1 | 1 | TW \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/address/state` | 1 | 1/2 | 1 | 1 | CA |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/orgname` | 1 | 2/2 | 1 | 1 | WISE CENTER PRECISION APPLIANCE CO., LTD. \| MUNCHKIN, INC. |  |
| `/us-patent-grant/us-bibliographic-data-grant/assignees/assignee/addressbook/role` | 1 | 2/2 | 1 | 1 | 03 \| 02 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc` | 1 | 1/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc` | 1..N (max=3) | 1/2 | 3 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/action-date` | 1..N (max=3) | 1/2 | 3 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/action-date/date` | 1..N (max=3) | 1/2 | 3 | 3 | 20230103 \| 20230103 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/class` | 1..N (max=3) | 1/2 | 3 | 3 | 47 \| 47 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/classification-data-source` | 1..N (max=3) | 1/2 | 3 | 3 | H \| H |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/classification-status` | 1..N (max=3) | 1/2 | 3 | 3 | B \| B |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/classification-value` | 1..N (max=3) | 1/2 | 3 | 3 | I \| I |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/cpc-version-indicator` | 1..N (max=3) | 1/2 | 3 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/cpc-version-indicator/date` | 1..N (max=3) | 1/2 | 3 | 3 | 20130101 \| 20130101 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/generating-office` | 1..N (max=3) | 1/2 | 3 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/generating-office/country` | 1..N (max=3) | 1/2 | 3 | 3 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/main-group` | 1..N (max=3) | 1/2 | 3 | 3 | 19 \| 21 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/scheme-origination-code` | 1..N (max=3) | 1/2 | 3 | 3 | C \| C |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/section` | 1..N (max=3) | 1/2 | 3 | 3 | A \| A |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/subclass` | 1..N (max=3) | 1/2 | 3 | 3 | G \| G |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/subgroup` | 1..N (max=3) | 1/2 | 3 | 3 | 2205 \| 186 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/further-cpc/classification-cpc/symbol-position` | 1..N (max=3) | 1/2 | 3 | 3 | L \| L |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/action-date` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/action-date/date` | 1 | 2/2 | 1 | 1 | 20230103 \| 20230103 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/class` | 1 | 2/2 | 1 | 1 | 01 \| 65 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/classification-data-source` | 1 | 2/2 | 1 | 1 | H \| H |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/classification-status` | 1 | 2/2 | 1 | 1 | B \| B |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/classification-value` | 1 | 2/2 | 1 | 1 | I \| I |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/cpc-version-indicator/date` | 1 | 2/2 | 1 | 1 | 20130101 \| 20130101 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/generating-office` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/generating-office/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/main-group` | 1 | 2/2 | 1 | 1 | 3 \| 47 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/scheme-origination-code` | 1 | 2/2 | 1 | 1 | C \| C |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/section` | 1 | 2/2 | 1 | 1 | A \| B |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/subclass` | 1 | 2/2 | 1 | 1 | G \| D |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/subgroup` | 1 | 2/2 | 1 | 1 | 0475 \| 0885 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-cpc/main-cpc/classification-cpc/symbol-position` | 1 | 2/2 | 1 | 1 | F \| F |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/action-date` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/action-date/date` | 1..N (max=3) | 2/2 | 2 | 3 | 20230103 \| 20230103 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/class` | 1..N (max=3) | 2/2 | 2 | 3 | 01 \| 01 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/classification-data-source` | 1..N (max=3) | 2/2 | 2 | 3 | H \| H |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/classification-level` | 1..N (max=3) | 2/2 | 2 | 3 | A \| A |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/classification-status` | 1..N (max=3) | 2/2 | 2 | 3 | B \| B |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/classification-value` | 1..N (max=3) | 2/2 | 2 | 3 | I \| I |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/generating-office` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/generating-office/country` | 1..N (max=3) | 2/2 | 2 | 3 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/ipc-version-indicator` | 1..N (max=3) | 2/2 | 2 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/ipc-version-indicator/date` | 1..N (max=3) | 2/2 | 2 | 3 | 20060101 \| 20060101 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/main-group` | 1..N (max=3) | 2/2 | 2 | 3 | 3 \| 3 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/section` | 1..N (max=3) | 2/2 | 2 | 3 | A \| A |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/subclass` | 1..N (max=3) | 2/2 | 2 | 3 | G \| G |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/subgroup` | 1..N (max=3) | 2/2 | 2 | 3 | 02 \| 047 |  |
| `/us-patent-grant/us-bibliographic-data-grant/classifications-ipcr/classification-ipcr/symbol-position` | 1..N (max=3) | 2/2 | 2 | 3 | F \| L |  |
| `/us-patent-grant/us-bibliographic-data-grant/examiners` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/examiners/primary-examiner` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/examiners/primary-examiner/department` | 1 | 2/2 | 1 | 1 | 3724 \| 3735 |  |
| `/us-patent-grant/us-bibliographic-data-grant/examiners/primary-examiner/first-name` | 1 | 2/2 | 1 | 1 | Ghassem \| King M |  |
| `/us-patent-grant/us-bibliographic-data-grant/examiners/primary-examiner/last-name` | 1 | 2/2 | 1 | 1 | Alie \| Chu |  |
| `/us-patent-grant/us-bibliographic-data-grant/figures` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/figures/number-of-drawing-sheets` | 1 | 2/2 | 1 | 1 | 6 \| 18 |  |
| `/us-patent-grant/us-bibliographic-data-grant/figures/number-of-figures` | 1 | 2/2 | 1 | 1 | 6 \| 33 |  |
| `/us-patent-grant/us-bibliographic-data-grant/invention-title` | 1 | 2/2 | 1 | 1 | Gardening shears having effort-saving structure \| Flip straw cup assembly | id="d2e43" |
| `/us-patent-grant/us-bibliographic-data-grant/number-of-claims` | 1 | 2/2 | 1 | 1 | 3 \| 18 |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference/document-id` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference/document-id/country` | 1 | 2/2 | 1 | 1 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 20230103 \| 20230103 |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference/document-id/doc-number` | 1 | 2/2 | 1 | 1 | 11540449 \| 11542074 |  |
| `/us-patent-grant/us-bibliographic-data-grant/publication-reference/document-id/kind` | 1 | 2/2 | 1 | 1 | B1 \| B1 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-application-series-code` | 1 | 2/2 | 1 | 1 | 17 \| 17 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-exemplary-claim` | 1 | 2/2 | 1 | 1 | 1 \| 1 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search/classification-cpc-text` | 1..N (max=9) | 2/2 | 8 | 9 | A01G 3/02 \| A01G 3/08 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search/classification-national` | 1..N (max=9) | 2/2 | 3 | 9 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search/classification-national/additional-info` | 1 | 1/2 | 1 | 1 | unstructured |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search/classification-national/country` | 1..N (max=9) | 2/2 | 3 | 9 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-field-of-classification-search/classification-national/main-classification` | 1..N (max=9) | 2/2 | 3 | 9 | 30224 \| 30186 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent` | 1 | 2/2 | 1 | 1 |  | rep-type="attorney" sequence="01" |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook/address` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook/address/country` | 1 | 2/2 | 1 | 1 | unknown \| unknown |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook/first-name` | 1 | 1/2 | 1 | 1 | Robert Z. |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook/last-name` | 1 | 1/2 | 1 | 1 | Evora, Esq. |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/agents/agent/addressbook/orgname` | 1 | 1/2 | 1 | 1 | Muncy, Geissler, Olds & Lowe, P.C. |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor` | 1..N (max=4) | 2/2 | 1 | 4 |  | designation="us-only" sequence="001" sequence="002" sequence="003" |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook` | 1..N (max=4) | 2/2 | 1 | 4 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/address` | 1..N (max=4) | 2/2 | 1 | 4 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/address/city` | 1..N (max=4) | 2/2 | 1 | 4 | Taichung \| Los Angeles |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/address/country` | 1..N (max=4) | 2/2 | 1 | 4 | TW \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/address/state` | 1..N (max=4) | 1/2 | 4 | 4 | CA \| CA |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/first-name` | 1..N (max=4) | 2/2 | 1 | 4 | Thomas \| Agnes Yena |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/inventors/inventor/addressbook/last-name` | 1..N (max=4) | 2/2 | 1 | 4 | Lin \| Lee |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant` | 1 | 2/2 | 1 | 1 |  | app-type="applicant" applicant-authority-category="assignee" designation="us-only" sequence="001" |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook/address` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook/address/city` | 1 | 2/2 | 1 | 1 | Taichung \| Van Nuys |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook/address/country` | 1 | 2/2 | 1 | 1 | TW \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook/address/state` | 1 | 1/2 | 1 | 1 | CA |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/addressbook/orgname` | 1 | 2/2 | 1 | 1 | WISE CENTER PRECISION APPLIANCE CO., LTD. \| Munchkin, Inc. |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/residence` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-parties/us-applicants/us-applicant/residence/country` | 1 | 2/2 | 1 | 1 | TW \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited` | 1 | 2/2 | 1 | 1 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation` | 1..N (max=47) | 2/2 | 5 | 47 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/category` | 1..N (max=47) | 2/2 | 5 | 47 | cited by examiner \| cited by examiner |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/classification-cpc-text` | 1..N (max=5) | 2/2 | 4 | 5 | A01G 3/08 \| A01G 3/0251 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/classification-national` | 1..N (max=3) | 2/2 | 3 | 3 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/classification-national/country` | 1..N (max=3) | 2/2 | 3 | 3 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/classification-national/main-classification` | 1..N (max=3) | 2/2 | 3 | 3 | 30186 \| 30258 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/nplcit` | 1..N (max=5) | 1/2 | 5 | 5 |  | num="00043" num="00044" num="00045" num="00046" |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/nplcit/othercit` | 1..N (max=5) | 1/2 | 5 | 5 | https://www.kickstarter.com/projects/simplykleanfamily/patent-pending-resealable-and-reusable-silico |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit` | 1..N (max=42) | 2/2 | 5 | 42 |  | num="00001" num="00002" num="00003" num="00004" |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id` | 1..N (max=42) | 2/2 | 5 | 42 |  |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id/country` | 1..N (max=42) | 2/2 | 5 | 42 | US \| US |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id/date` | 1..N (max=42) | 2/2 | 5 | 42 | 20131200 \| 20190200 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id/doc-number` | 1..N (max=42) | 2/2 | 5 | 42 | 8607677 \| 10212891 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id/kind` | 1..N (max=42) | 2/2 | 5 | 42 | B2 \| B1 |  |
| `/us-patent-grant/us-bibliographic-data-grant/us-references-cited/us-citation/patcit/document-id/name` | 1..N (max=25) | 2/2 | 5 | 25 | Nelson \| Wu |  |
| `/us-patent-grant/us-claim-statement` | 1 | 2/2 | 1 | 1 | What is claimed is: \| What is claimed: |  |
