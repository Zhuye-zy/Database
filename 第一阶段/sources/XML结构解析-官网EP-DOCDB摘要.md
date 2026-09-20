# 专利 XML 结构解析结果

- 输入: DOCDB-201724-Amend-PubDate20170609AndBefore-EP-000.xml
- 解析文档数: 2 (根元素: {'exchange-document': 2})
- 元素路径数: 92

| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |
|---|---|---|---|---|---|---|
| `/exchange-document` | 1 | 2/2 | 1 | 1 |  | country="EP" date-added-docdb="20000418" date-of-last-exchange="20170615" date-of-previous-exchange="20170302" |
| `/exchange-document/abstract` | 1..N (max=2) | 2/2 | 1 | 2 |  | abstract-source="EPO" data-format="docdba" lang="de" lang="en" |
| `/exchange-document/abstract/p` | 1..N (max=2) | 2/2 | 1 | 2 | Bei der Erfindung handelt es sich um einen vornehmlich im Mikrowellenbereich arbeitenden, beispielsw |  |
| `/exchange-document/bibliographic-data` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/application-reference` | 1..N (max=3) | 2/2 | 3 | 3 |  | data-format="docdb" data-format="epodoc" data-format="original" doc-id="16430989" |
| `/exchange-document/bibliographic-data/application-reference/document-id` | 1..N (max=3) | 2/2 | 3 | 3 |  |  |
| `/exchange-document/bibliographic-data/application-reference/document-id/country` | 1 | 2/2 | 1 | 1 | EP \| EP |  |
| `/exchange-document/bibliographic-data/application-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 19790129 \| 19790305 |  |
| `/exchange-document/bibliographic-data/application-reference/document-id/doc-number` | 1..N (max=3) | 2/2 | 3 | 3 | 79100245 \| EP19790100245 |  |
| `/exchange-document/bibliographic-data/application-reference/document-id/kind` | 1 | 2/2 | 1 | 1 | A \| A |  |
| `/exchange-document/bibliographic-data/classification-ipc` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/classification-ipc/further-classification` | 0..1 | 1/2 | 0 | 1 | F 23D 13/18 B |  |
| `/exchange-document/bibliographic-data/classification-ipc/main-classification` | 1 | 2/2 | 1 | 1 | H 04B 7/185 A \| F 02M 27/02 A |  |
| `/exchange-document/bibliographic-data/classifications-ipcr` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/classifications-ipcr/classification-ipcr` | 1..N (max=3) | 2/2 | 2 | 3 |  | sequence="1" sequence="2" sequence="3" |
| `/exchange-document/bibliographic-data/classifications-ipcr/classification-ipcr/text` | 1..N (max=3) | 2/2 | 2 | 3 | H04B 7/15 20060101AFI20051220RMJP \| H04B 7/185 20060101A I20051008RMEP |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/examined-printed-without-grant` | 0..1 | 1/2 | 0 | 1 |  |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/examined-printed-without-grant/document-id` | 0..1 | 1/2 | 0 | 1 |  |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/examined-printed-without-grant/document-id/date` | 0..1 | 1/2 | 0 | 1 | 19790822 |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/unexamined-printed-without-grant` | 0..1 | 1/2 | 0 | 1 |  |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/unexamined-printed-without-grant/document-id` | 0..1 | 1/2 | 0 | 1 |  |  |
| `/exchange-document/bibliographic-data/dates-of-public-availability/unexamined-printed-without-grant/document-id/date` | 0..1 | 1/2 | 0 | 1 | 19790919 |  |
| `/exchange-document/bibliographic-data/designation-of-states` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/designation-of-states/designation-epc` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/designation-of-states/designation-epc/contracting-states` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/designation-of-states/designation-epc/contracting-states/country` | 1..N (max=6) | 2/2 | 3 | 6 | FR \| GB |  |
| `/exchange-document/bibliographic-data/invention-title` | 1..N (max=3) | 2/2 | 3 | 3 | Übertragungsanordnung in Ein- und Mehrkanalsystemen. \| Transmission device for mono- or multichanne | data-format="docdba" lang="de" lang="en" lang="fr" |
| `/exchange-document/bibliographic-data/language-of-publication` | 1 | 2/2 | 1 | 1 | de \| de |  |
| `/exchange-document/bibliographic-data/parties` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/parties/applicants` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/parties/applicants/applicant` | 1..N (max=2) | 2/2 | 2 | 2 |  | data-format="docdb" data-format="docdba" sequence="1" |
| `/exchange-document/bibliographic-data/parties/applicants/applicant/applicant-name` | 1..N (max=2) | 2/2 | 2 | 2 |  |  |
| `/exchange-document/bibliographic-data/parties/applicants/applicant/applicant-name/name` | 1..N (max=2) | 2/2 | 2 | 2 | LICENTIA GMBH \| LICENTIA PATENT-VERWALTUNGS-GMBH |  |
| `/exchange-document/bibliographic-data/parties/applicants/applicant/residence` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/parties/applicants/applicant/residence/country` | 1 | 2/2 | 1 | 1 | DE \| DE |  |
| `/exchange-document/bibliographic-data/parties/inventors` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/parties/inventors/inventor` | 1..N (max=8) | 2/2 | 4 | 8 |  | data-format="docdb" data-format="docdba" sequence="1" sequence="2" |
| `/exchange-document/bibliographic-data/parties/inventors/inventor/inventor-name` | 1..N (max=8) | 2/2 | 4 | 8 |  |  |
| `/exchange-document/bibliographic-data/parties/inventors/inventor/inventor-name/name` | 1..N (max=8) | 2/2 | 4 | 8 | SEIDENSTICKER KLAUS \| DIENER FRANCO |  |
| `/exchange-document/bibliographic-data/parties/inventors/inventor/residence` | 0..N (max=2) | 1/2 | 0 | 2 |  |  |
| `/exchange-document/bibliographic-data/parties/inventors/inventor/residence/country` | 0..N (max=2) | 1/2 | 0 | 2 | DE \| DE |  |
| `/exchange-document/bibliographic-data/patent-classifications` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification` | 1..N (max=3) | 2/2 | 1 | 3 |  | sequence="1" sequence="2" sequence="3" |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/action-date` | 1..N (max=3) | 2/2 | 1 | 3 |  |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/action-date/date` | 1..N (max=3) | 2/2 | 1 | 3 | 20170220 \| 20161130 |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-data-source` | 1..N (max=3) | 2/2 | 1 | 3 | H \| H |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-scheme` | 1..N (max=3) | 2/2 | 1 | 3 |  | office="EP" scheme="CPC" |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-scheme/date` | 1..N (max=3) | 2/2 | 1 | 3 | 20130101 \| 20130101 |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-status` | 1..N (max=3) | 2/2 | 1 | 3 | B \| B |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-symbol` | 1..N (max=3) | 2/2 | 1 | 3 | H04B 7/18515 \| F23D 11/448 |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/classification-value` | 1..N (max=3) | 2/2 | 1 | 3 | I \| I |  |
| `/exchange-document/bibliographic-data/patent-classifications/patent-classification/symbol-position` | 1..N (max=3) | 2/2 | 1 | 3 | F \| F |  |
| `/exchange-document/bibliographic-data/priority-claims` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim` | 1..N (max=3) | 2/2 | 3 | 3 |  | data-format="docdb" data-format="epodoc" data-format="original" sequence="1" |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/document-id` | 1..N (max=3) | 2/2 | 3 | 3 |  | doc-id="10336288" doc-id="10343348" |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/document-id/country` | 1 | 2/2 | 1 | 1 | DE \| DE |  |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/document-id/date` | 1 | 2/2 | 1 | 1 | 19780202 \| 19780315 |  |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/document-id/doc-number` | 1..N (max=3) | 2/2 | 3 | 3 | 2804439 \| DE19782804439 |  |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/document-id/kind` | 1 | 2/2 | 1 | 1 | A \| A |  |
| `/exchange-document/bibliographic-data/priority-claims/priority-claim/priority-active-indicator` | 1 | 2/2 | 1 | 1 | Y \| Y |  |
| `/exchange-document/bibliographic-data/publication-reference` | 1..N (max=2) | 2/2 | 2 | 2 |  | data-format="docdb" data-format="epodoc" |
| `/exchange-document/bibliographic-data/publication-reference/document-id` | 1..N (max=2) | 2/2 | 2 | 2 |  | lang="de" |
| `/exchange-document/bibliographic-data/publication-reference/document-id/country` | 1 | 2/2 | 1 | 1 | EP \| EP |  |
| `/exchange-document/bibliographic-data/publication-reference/document-id/date` | 1 | 2/2 | 1 | 1 | 19790822 \| 19790919 |  |
| `/exchange-document/bibliographic-data/publication-reference/document-id/doc-number` | 1..N (max=2) | 2/2 | 2 | 2 | 0003543 \| EP0003543 |  |
| `/exchange-document/bibliographic-data/publication-reference/document-id/kind` | 1 | 2/2 | 1 | 1 | A1 \| A2 |  |
| `/exchange-document/bibliographic-data/references-cited` | 0..1 | 1/2 | 0 | 1 |  |  |
| `/exchange-document/bibliographic-data/references-cited/citation` | 0..N (max=7) | 1/2 | 0 | 7 |  | cited-phase="SEA" sequence="1" sequence="2" sequence="3" |
| `/exchange-document/bibliographic-data/references-cited/citation/nplcit` | 0..N (max=3) | 1/2 | 0 | 3 |  | npl-type="a" num="1" num="2" num="3" |
| `/exchange-document/bibliographic-data/references-cited/citation/nplcit/text` | 0..N (max=3) | 1/2 | 0 | 3 | COLLOQUE INTERNATIONAL L'ESPACE ET LA COMMUNICATION, Band 2, Paris 2. Marz - 2. April 1971, Chiron,  |  |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit` | 0..N (max=4) | 1/2 | 0 | 4 |  | dnum-type="publication number" dnum="FR1402311A" dnum="FR2057218A5" dnum="US2770722A" |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id` | 0..N (max=4) | 1/2 | 0 | 4 |  | doc-id="316912938" doc-id="317211701" doc-id="327029824" doc-id="327310613" |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id/country` | 0..N (max=4) | 1/2 | 0 | 4 | US \| FR |  |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id/date` | 0..N (max=4) | 1/2 | 0 | 4 | 19620807 \| 19710521 |  |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id/doc-number` | 0..N (max=4) | 1/2 | 0 | 4 | 3048794 \| 2057218 |  |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id/kind` | 0..N (max=4) | 1/2 | 0 | 4 | A \| A5 |  |
| `/exchange-document/bibliographic-data/references-cited/citation/patcit/document-id/name` | 0..N (max=4) | 1/2 | 0 | 4 | MANUEL ARES \| THOMSON CSF |  |
| `/exchange-document/patent-family` | 1 | 2/2 | 1 | 1 |  |  |
| `/exchange-document/patent-family/abstract` | 0..1 | 1/2 | 0 | 1 |  | abstract-source="translation" country="US" data-format="docdba" doc-number="4230443" |
| `/exchange-document/patent-family/abstract/p` | 0..1 | 1/2 | 0 | 1 | A vaporizing burner which includes a multi-portioned burner housing. The housing encompasses an inle |  |
| `/exchange-document/patent-family/family-member` | 1..N (max=7) | 2/2 | 3 | 7 |  |  |
| `/exchange-document/patent-family/family-member/application-reference` | 1..N (max=14) | 2/2 | 6 | 14 |  | data-format="docdb" data-format="epodoc" is-representative="NO" is-representative="YES" |
| `/exchange-document/patent-family/family-member/application-reference/document-id` | 1..N (max=14) | 2/2 | 6 | 14 |  |  |
| `/exchange-document/patent-family/family-member/application-reference/document-id/country` | 1..N (max=7) | 2/2 | 3 | 7 | DE \| EP |  |
| `/exchange-document/patent-family/family-member/application-reference/document-id/doc-number` | 1..N (max=14) | 2/2 | 6 | 14 | 2804439 \| DE19782804439 |  |
| `/exchange-document/patent-family/family-member/application-reference/document-id/kind` | 1..N (max=7) | 2/2 | 3 | 7 | A \| A |  |
| `/exchange-document/patent-family/family-member/publication-reference` | 1..N (max=30) | 2/2 | 6 | 30 |  | data-format="docdb" data-format="epodoc" sequence="1" sequence="2" |
| `/exchange-document/patent-family/family-member/publication-reference/document-id` | 1..N (max=30) | 2/2 | 6 | 30 |  |  |
| `/exchange-document/patent-family/family-member/publication-reference/document-id/country` | 1..N (max=15) | 2/2 | 3 | 15 | DE \| EP |  |
| `/exchange-document/patent-family/family-member/publication-reference/document-id/doc-number` | 1..N (max=30) | 2/2 | 6 | 30 | 2804439 \| DE2804439 |  |
| `/exchange-document/patent-family/family-member/publication-reference/document-id/kind` | 1..N (max=15) | 2/2 | 3 | 15 | A1 \| A1 |  |
