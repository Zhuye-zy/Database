# 专利 XML 结构解析结果

- 输入: 712-096-DOC00001.xml, 797-400-DOC00001.xml, 797-401-DOC00001.xml, 890-251-DOC00001.xml
- 解析文档数: 4 (根元素: {'ep-patent-document': 4})
- 元素路径数: 190

| 元素路径 | 出现次数 | 文档出现率 | 单文档最少 | 单文档最多 | 样例值 | 属性 |
|---|---|---|---|---|---|---|
| `/ep-patent-document` | 1 | 4/4 | 1 | 1 |  | country="EP" date-publ="20141105" doc-number="0712096" doc-number="0890251" |
| `/ep-patent-document/SDOBI` | 1 | 4/4 | 1 | 1 |  | lang="en" |
| `/ep-patent-document/SDOBI/B000` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B000/eptags` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B000/eptags/B001EP` | 1 | 4/4 | 1 | 1 | ......DE....FRGB.................................................................................... |  |
| `/ep-patent-document/SDOBI/B000/eptags/B003EP` | 0..1 | 3/4 | 0 | 1 | * \| * |  |
| `/ep-patent-document/SDOBI/B000/eptags/B005EP` | 1 | 4/4 | 1 | 1 | J \| X |  |
| `/ep-patent-document/SDOBI/B000/eptags/B007EP` | 1 | 4/4 | 1 | 1 | DIM360 Ver 2.41 (21 Oct 2013) - 2100000/0 \| DIM360 Ver 2.41 (21 Oct 2013) - 1100000/0 |  |
| `/ep-patent-document/SDOBI/B100` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B100/B110` | 1 | 4/4 | 1 | 1 | 0712096 \| 2797400 |  |
| `/ep-patent-document/SDOBI/B100/B120` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B100/B120/B121` | 0..1 | 2/4 | 0 | 1 | EUROPEAN PATENT SPECIFICATION \| EUROPEAN PATENT SPECIFICATION |  |
| `/ep-patent-document/SDOBI/B100/B130` | 1 | 4/4 | 1 | 1 | B1 \| A1 |  |
| `/ep-patent-document/SDOBI/B100/B140` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B100/B140/date` | 1 | 4/4 | 1 | 1 | 20141105 \| 20141105 |  |
| `/ep-patent-document/SDOBI/B100/B190` | 1 | 4/4 | 1 | 1 | EP \| EP |  |
| `/ep-patent-document/SDOBI/B200` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B200/B210` | 1 | 4/4 | 1 | 1 | 95308109.8 \| 12862380.8 |  |
| `/ep-patent-document/SDOBI/B200/B220` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B200/B220/date` | 1 | 4/4 | 1 | 1 | 19951113 \| 20121213 |  |
| `/ep-patent-document/SDOBI/B200/B240` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B200/B240/B241` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B200/B240/B241/date` | 1 | 4/4 | 1 | 1 | 19970604 \| 20140415 |  |
| `/ep-patent-document/SDOBI/B200/B240/B242` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B200/B240/B242/date` | 0..1 | 2/4 | 0 | 1 | 20030407 \| 20050415 |  |
| `/ep-patent-document/SDOBI/B200/B250` | 1 | 4/4 | 1 | 1 | en \| en |  |
| `/ep-patent-document/SDOBI/B200/B251EP` | 1 | 4/4 | 1 | 1 | en \| en |  |
| `/ep-patent-document/SDOBI/B200/B260` | 1 | 4/4 | 1 | 1 | en \| en |  |
| `/ep-patent-document/SDOBI/B300` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B300/B310` | 0..N (max=2) | 3/4 | 0 | 2 | 338856 \| 201161581832 P |  |
| `/ep-patent-document/SDOBI/B300/B320` | 0..N (max=2) | 3/4 | 0 | 2 |  |  |
| `/ep-patent-document/SDOBI/B300/B320/date` | 0..N (max=2) | 3/4 | 0 | 2 | 19941114 \| 20111230 |  |
| `/ep-patent-document/SDOBI/B300/B330` | 0..N (max=2) | 3/4 | 0 | 2 |  |  |
| `/ep-patent-document/SDOBI/B300/B330/ctry` | 0..N (max=2) | 3/4 | 0 | 2 | US \| US |  |
| `/ep-patent-document/SDOBI/B400` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B400/B405` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B400/B405/bnum` | 1 | 4/4 | 1 | 1 | 201445 \| 201445 |  |
| `/ep-patent-document/SDOBI/B400/B405/date` | 1 | 4/4 | 1 | 1 | 20141105 \| 20141105 |  |
| `/ep-patent-document/SDOBI/B400/B430` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B400/B430/bnum` | 1 | 4/4 | 1 | 1 | 199620 \| 201445 |  |
| `/ep-patent-document/SDOBI/B400/B430/date` | 1 | 4/4 | 1 | 1 | 19960515 \| 20141105 |  |
| `/ep-patent-document/SDOBI/B400/B450` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B400/B450/bnum` | 0..1 | 2/4 | 0 | 1 | 201445 \| 201445 |  |
| `/ep-patent-document/SDOBI/B400/B450/date` | 0..1 | 2/4 | 0 | 1 | 20141105 \| 20141105 |  |
| `/ep-patent-document/SDOBI/B400/B452EP` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B400/B452EP/date` | 0..1 | 2/4 | 0 | 1 | 20140616 \| 20140521 |  |
| `/ep-patent-document/SDOBI/B500` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B500/B510EP` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B500/B510EP/classification-ipcr` | 1..N (max=6) | 4/4 | 1 | 6 |  | sequence="1" sequence="2" sequence="3" sequence="4" |
| `/ep-patent-document/SDOBI/B500/B510EP/classification-ipcr/text` | 1..N (max=6) | 4/4 | 1 | 6 | G06T 11/60 20060101AFI19960302BHEP \| A01C 1/06 20060101AFI20130718BHEP |  |
| `/ep-patent-document/SDOBI/B500/B540` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B500/B540/B541` | 1..N (max=3) | 4/4 | 3 | 3 | de \| en |  |
| `/ep-patent-document/SDOBI/B500/B540/B542` | 1..N (max=3) | 4/4 | 3 | 3 | Bildaufbereitungsverfahren und Editor für Bilder auf strukturiertem Bildformat \| Editing method and |  |
| `/ep-patent-document/SDOBI/B500/B560` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B500/B560/B561` | 0..N (max=3) | 2/4 | 0 | 3 |  |  |
| `/ep-patent-document/SDOBI/B500/B560/B561/text` | 0..N (max=3) | 2/4 | 0 | 3 | EP-A- 0 528 631 \| WO-A-94/22101 |  |
| `/ep-patent-document/SDOBI/B500/B560/B562` | 0..N (max=2) | 2/4 | 0 | 2 |  |  |
| `/ep-patent-document/SDOBI/B500/B560/B562/text` | 0..N (max=2) | 2/4 | 0 | 2 | COMPUTERS AND GRAPHICS, vol. 12, no. 2, 1 January 1988, pages 201-211, XP000141988 HOWARD T: "A SHAR |  |
| `/ep-patent-document/SDOBI/B500/B560/B565EP` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B500/B560/B565EP/date` | 0..1 | 1/4 | 0 | 1 | 19990429 |  |
| `/ep-patent-document/SDOBI/B700` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B710` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B710/B711` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/adr` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/adr/city` | 0..1 | 2/4 | 0 | 1 | Federal Way, WA 98063-9777 \| 561 82 Huskvarna |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/adr/ctry` | 0..1 | 2/4 | 0 | 1 | US \| SE |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/adr/str` | 0..1 | 2/4 | 0 | 1 | P.O. Box 9777 CH1J27 \| Drottninggatan 2 |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/iid` | 0..1 | 2/4 | 0 | 1 | 101142012 \| 101145245 |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/irf` | 0..1 | 2/4 | 0 | 1 | JAS/P132178EP00 \| P2787EP00 |  |
| `/ep-patent-document/SDOBI/B700/B710/B711/snm` | 0..1 | 2/4 | 0 | 1 | Weyerhaeuser Nr Company \| Husqvarna AB |  |
| `/ep-patent-document/SDOBI/B700/B720` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B720/B721` | 1..N (max=3) | 4/4 | 1 | 3 |  |  |
| `/ep-patent-document/SDOBI/B700/B720/B721/adr` | 1..N (max=3) | 4/4 | 1 | 3 |  |  |
| `/ep-patent-document/SDOBI/B700/B720/B721/adr/city` | 1..N (max=3) | 4/4 | 1 | 3 | Webster NY 14580 \| Rochester, NY 14612 |  |
| `/ep-patent-document/SDOBI/B700/B720/B721/adr/ctry` | 1..N (max=3) | 4/4 | 1 | 3 | US \| US |  |
| `/ep-patent-document/SDOBI/B700/B720/B721/adr/str` | 1..N (max=3) | 4/4 | 1 | 3 | 1105 Marigold Drive \| 777 Latta Road |  |
| `/ep-patent-document/SDOBI/B700/B720/B721/snm` | 1..N (max=3) | 4/4 | 1 | 3 | Campanelli, Michael R. \| Fuss, William A. |  |
| `/ep-patent-document/SDOBI/B700/B730` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B730/B731` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/adr` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/adr/city` | 0..1 | 2/4 | 0 | 1 | Rochester, New York 14644 \| Melbourne, VIC 3000 |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/adr/ctry` | 0..1 | 2/4 | 0 | 1 | US \| AU |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/adr/str` | 0..1 | 2/4 | 0 | 1 | Xerox Square \| 242 Exhibition Street |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/iid` | 0..1 | 2/4 | 0 | 1 | 100256692 \| 100234324 |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/irf` | 0..1 | 2/4 | 0 | 1 | D/93175 \| PJF01778EP |  |
| `/ep-patent-document/SDOBI/B700/B730/B731/snm` | 0..1 | 2/4 | 0 | 1 | Xerox Corporation \| TELSTRA CORPORATION LIMITED |  |
| `/ep-patent-document/SDOBI/B700/B740` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B740/B741` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/adr` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/adr/city` | 0..1 | 3/4 | 0 | 1 | London EC2A 2ES \| London WC1X 8BT |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/adr/ctry` | 0..1 | 3/4 | 0 | 1 | GB \| GB |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/adr/str` | 0..1 | 3/4 | 0 | 1 | Gill Jennings & Every LLP The Broadgate Tower 20 Primrose Street \| Verulam Gardens 70 Gray's Inn Ro |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/iid` | 0..1 | 3/4 | 0 | 1 | 100024113 \| 101370347 |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/sfx` | 0..1 | 1/4 | 0 | 1 | et al |  |
| `/ep-patent-document/SDOBI/B700/B740/B741/snm` | 0..1 | 3/4 | 0 | 1 | Skone James, Robert Edmund \| Boult Wade Tennant |  |
| `/ep-patent-document/SDOBI/B800` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B840` | 1 | 4/4 | 1 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B840/ctry` | 1..N (max=38) | 4/4 | 3 | 38 | DE \| FR |  |
| `/ep-patent-document/SDOBI/B800/B844EP` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B844EP/B845EP` | 0..N (max=5) | 1/4 | 0 | 5 |  |  |
| `/ep-patent-document/SDOBI/B800/B844EP/B845EP/ctry` | 0..N (max=5) | 1/4 | 0 | 5 | AL \| LT |  |
| `/ep-patent-document/SDOBI/B800/B844EP/B845EP/date` | 0..N (max=5) | 1/4 | 0 | 5 | 19980930 \| 19980930 |  |
| `/ep-patent-document/SDOBI/B800/B860` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B860/B861` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B860/B861/date` | 0..1 | 3/4 | 0 | 1 | 20121213 \| 20111230 |  |
| `/ep-patent-document/SDOBI/B800/B860/B861/dnum` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B860/B861/dnum/anum` | 0..1 | 3/4 | 0 | 1 | US2012069532 \| SE2011051609 |  |
| `/ep-patent-document/SDOBI/B800/B860/B862` | 0..1 | 3/4 | 0 | 1 | en \| en |  |
| `/ep-patent-document/SDOBI/B800/B870` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B870/B871` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B870/B871/bnum` | 0..1 | 3/4 | 0 | 1 | 201327 \| 201327 |  |
| `/ep-patent-document/SDOBI/B800/B870/B871/date` | 0..1 | 3/4 | 0 | 1 | 20130704 \| 20130704 |  |
| `/ep-patent-document/SDOBI/B800/B870/B871/dnum` | 0..1 | 3/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B870/B871/dnum/pnum` | 0..1 | 3/4 | 0 | 1 | WO2013101486 \| WO2013100833 |  |
| `/ep-patent-document/SDOBI/B800/B880` | 0..1 | 2/4 | 0 | 1 |  |  |
| `/ep-patent-document/SDOBI/B800/B880/bnum` | 0..1 | 2/4 | 0 | 1 | 199649 \| 199902 |  |
| `/ep-patent-document/SDOBI/B800/B880/date` | 0..1 | 2/4 | 0 | 1 | 19961204 \| 19990113 |  |
| `/ep-patent-document/claims` | 0..N (max=3) | 2/4 | 0 | 3 |  | id="claims01" id="claims02" id="claims03" lang="de" |
| `/ep-patent-document/claims/claim` | 0..N (max=42) | 2/4 | 0 | 42 |  | id="c-de-01-0001" id="c-de-01-0002" id="c-de-01-0003" id="c-de-01-0004" |
| `/ep-patent-document/claims/claim/claim-text` | 0..N (max=42) | 2/4 | 0 | 42 | A structured image (SI) editor for editing a structured image, the structured image being a raster i |  |
| `/ep-patent-document/claims/claim/claim-text/b` | 0..N (max=18) | 1/4 | 0 | 18 | characterised in that \| characterised in that |  |
| `/ep-patent-document/claims/claim/claim-text/br` | 0..N (max=4) | 1/4 | 0 | 4 |  |  |
| `/ep-patent-document/claims/claim/claim-text/claim-text` | 0..N (max=39) | 2/4 | 0 | 39 | an SI structure editor operable to create a hierarchical representation of the structured image; and |  |
| `/ep-patent-document/claims/claim/claim-text/claim-text/b` | 0..N (max=5) | 1/4 | 0 | 5 | caractérisé en ce que \| caractérisé en ce que |  |
| `/ep-patent-document/claims/claim/claim-text/claim-text/claim-text` | 0..N (max=2) | 1/4 | 0 | 2 | einen SI-Struktureditor, der betätigt werden kann, um eine hierarchische Darstellung des strukturier |  |
| `/ep-patent-document/description` | 0..1 | 2/4 | 0 | 1 |  | id="desc" lang="en" |
| `/ep-patent-document/description/heading` | 0..N (max=8) | 2/4 | 0 | 8 | A. \| A1. | id="h0001" id="h0002" id="h0003" id="h0004" |
| `/ep-patent-document/description/heading/b` | 0..N (max=4) | 1/4 | 0 | 4 | SUMMARY OF THE INVENTION \| BRIEF DESCRIPTION OF THE DRAWINGS |  |
| `/ep-patent-document/description/heading/u` | 0..N (max=7) | 1/4 | 0 | 7 | System Overview \| Structured Image Defined |  |
| `/ep-patent-document/description/p` | 0..N (max=72) | 2/4 | 0 | 72 | This invention relates to image editors, and more particularly to methods for editing images and ima | id="p0001" id="p0002" id="p0003" id="p0004" |
| `/ep-patent-document/description/p/b` | 0..N (max=2) | 1/4 | 0 | 2 | Response codes to do with card validation and authorisation \| Response codes indicating general fai |  |
| `/ep-patent-document/description/p/dl` | 0..N (max=3) | 1/4 | 0 | 3 |  | compact="compact" id="dl0001" id="dl0002" id="dl0003" |
| `/ep-patent-document/description/p/dl/dd` | 0..N (max=31) | 1/4 | 0 | 31 | call answered and in progress (A and B party connected) \| call finished |  |
| `/ep-patent-document/description/p/dl/dt` | 0..N (max=31) | 1/4 | 0 | 31 | 600 \| 601 |  |
| `/ep-patent-document/description/p/figref` | 0..N (max=39) | 2/4 | 0 | 39 | Fig. 1 \| Fig. 1 | idref="f0001" idref="f0002" idref="f0003" idref="f0004" |
| `/ep-patent-document/description/p/nplcit` | 0..1 | 1/4 | 0 | 1 |  | id="ncit0001" npl-type="s" |
| `/ep-patent-document/description/p/nplcit/text` | 0..1 | 1/4 | 0 | 1 | A Shareable Centralised Database for KRT3: A Hierarchical Graphics System based on PHIGS", T. Howard |  |
| `/ep-patent-document/description/p/ol` | 0..N (max=2) | 1/4 | 0 | 2 |  | compact="compact" id="ol0001" id="ol0002" ol-style="" |
| `/ep-patent-document/description/p/ol/li` | 0..N (max=11) | 1/4 | 0 | 11 | 1) raster image - TiFF, RES, or other digital display, \| 2) toy text - simple text annotation, |  |
| `/ep-patent-document/description/p/patcit` | 0..N (max=4) | 2/4 | 0 | 4 |  | dnum-type="L" dnum="DE3629468A" dnum="EP0528631A" dnum="EP528631A" |
| `/ep-patent-document/description/p/patcit/text` | 0..N (max=4) | 2/4 | 0 | 4 | EP-A-0528631 \| EP-A-647,921 |  |
| `/ep-patent-document/description/p/tables` | 0..N (max=3) | 1/4 | 0 | 3 |  | id="tabl0001" id="tabl0002" id="tabl0003" num="0001" |
| `/ep-patent-document/description/p/tables/table` | 0..N (max=3) | 1/4 | 0 | 3 |  | frame="all" frame="none" |
| `/ep-patent-document/description/p/tables/table/tgroup` | 0..N (max=3) | 1/4 | 0 | 3 |  | cols="2" cols="3" colsep="0" rowsep="0" |
| `/ep-patent-document/description/p/tables/table/tgroup/colspec` | 0..N (max=7) | 1/4 | 0 | 7 |  | colname="col1" colname="col2" colname="col3" colnum="1" |
| `/ep-patent-document/description/p/tables/table/tgroup/tbody` | 0..N (max=3) | 1/4 | 0 | 3 |  |  |
| `/ep-patent-document/description/p/tables/table/tgroup/tbody/row` | 0..N (max=34) | 1/4 | 0 | 34 |  |  |
| `/ep-patent-document/description/p/tables/table/tgroup/tbody/row/entry` | 0..N (max=80) | 1/4 | 0 | 80 | Applet to Server \| USER |  |
| `/ep-patent-document/description/p/tables/table/tgroup/tbody/row/entry/i` | 0..N (max=8) | 1/4 | 0 | 8 | username \| key |  |
| `/ep-patent-document/description/p/tables/table/tgroup/thead` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/description/p/tables/table/tgroup/thead/row` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/description/p/tables/table/tgroup/thead/row/entry` | 0..N (max=3) | 1/4 | 0 | 3 |  | align="center" valign="top" |
| `/ep-patent-document/description/p/tables/table/tgroup/thead/row/entry/b` | 0..N (max=3) | 1/4 | 0 | 3 | Direction \| Message |  |
| `/ep-patent-document/description/p/tables/table/title` | 0..N (max=3) | 1/4 | 0 | 3 |  |  |
| `/ep-patent-document/description/p/tables/table/title/b` | 0..N (max=3) | 1/4 | 0 | 3 | Table 1 \| Format of request |  |
| `/ep-patent-document/description/p/ul` | 0..N (max=6) | 2/4 | 0 | 6 |  | compact="compact" id="ul0001" id="ul0002" id="ul0003" |
| `/ep-patent-document/description/p/ul/li` | 0..N (max=25) | 2/4 | 0 | 25 | selecting a B party; and, \| sending, in response to selection of the B party, selected party data c |  |
| `/ep-patent-document/description/p/ul/li/figref` | 0..N (max=14) | 2/4 | 0 | 14 | Figure 1 \| Figure 2 | idref="f0001" idref="f0002" idref="f0003" idref="f0004" |
| `/ep-patent-document/drawings` | 0..1 | 2/4 | 0 | 1 |  | id="draw" lang="en" |
| `/ep-patent-document/drawings/figure` | 0..N (max=12) | 2/4 | 0 | 12 |  | id="f0001" id="f0002" id="f0003" id="f0004" |
| `/ep-patent-document/drawings/figure/img` | 0..N (max=12) | 2/4 | 0 | 12 |  | file="imgf0001.tif" file="imgf0002.tif" file="imgf0003.tif" file="imgf0004.tif" |
| `/ep-patent-document/ep-reference-list` | 0..1 | 2/4 | 0 | 1 |  | id="ref-list" |
| `/ep-patent-document/ep-reference-list/heading` | 0..N (max=3) | 2/4 | 0 | 3 |  | id="ref-h0001" id="ref-h0002" id="ref-h0003" |
| `/ep-patent-document/ep-reference-list/heading/b` | 0..N (max=3) | 2/4 | 0 | 3 | REFERENCES CITED IN THE DESCRIPTION \| Patent documents cited in the description |  |
| `/ep-patent-document/ep-reference-list/p` | 0..N (max=3) | 2/4 | 0 | 3 |  | id="ref-p0001" id="ref-p0002" id="ref-p0003" num="" |
| `/ep-patent-document/ep-reference-list/p/i` | 0..1 | 2/4 | 0 | 1 | This list of references cited by the applicant is for the reader's convenience only. It does not for |  |
| `/ep-patent-document/ep-reference-list/p/ul` | 0..N (max=2) | 2/4 | 0 | 2 |  | id="ref-ul0001" id="ref-ul0002" list-style="bullet" |
| `/ep-patent-document/ep-reference-list/p/ul/li` | 0..N (max=5) | 2/4 | 0 | 5 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/crossref` | 0..N (max=5) | 2/4 | 0 | 5 | [0013] \| [0050] | idref="ncit0001" idref="pcit0001" idref="pcit0002" idref="pcit0003" |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit` | 0..1 | 1/4 | 0 | 1 |  | id="ref-ncit0001" npl-type="s" |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/atl` | 0..1 | 1/4 | 0 | 1 | A Shareable Centralised Database for KRT3: A Hierarchical Graphics System based on PHIGS |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/author` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/author/name` | 0..1 | 1/4 | 0 | 1 | T. HOWARD |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/location` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/location/pp` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/location/pp/ppf` | 0..1 | 1/4 | 0 | 1 | 201 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/location/pp/ppl` | 0..1 | 1/4 | 0 | 1 | 211 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/ino` | 0..1 | 1/4 | 0 | 1 | 2 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/pubdate` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/pubdate/edate` | 0..1 | 1/4 | 0 | 1 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/pubdate/sdate` | 0..1 | 1/4 | 0 | 1 | 19880101 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/sertitle` | 0..1 | 1/4 | 0 | 1 | Computer and Graphics |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/nplcit/article/serial/vid` | 0..1 | 1/4 | 0 | 1 | 12 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/patcit` | 0..N (max=4) | 2/4 | 0 | 4 |  | dnum-type="L" dnum="DE3629468A" dnum="EP0528631A" dnum="EP528631A" |
| `/ep-patent-document/ep-reference-list/p/ul/li/patcit/document-id` | 0..N (max=4) | 2/4 | 0 | 4 |  |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/patcit/document-id/country` | 0..N (max=4) | 2/4 | 0 | 4 | EP \| EP |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/patcit/document-id/doc-number` | 0..N (max=4) | 2/4 | 0 | 4 | 0528631 \| 647921 |  |
| `/ep-patent-document/ep-reference-list/p/ul/li/patcit/document-id/kind` | 0..N (max=4) | 2/4 | 0 | 4 | A \| A |  |
