#!/usr/bin/env python3
"""Import the official patent XML samples archived by A into the PostgreSQL schema."""
from __future__ import annotations
import re, sys, subprocess, datetime, os, json, hashlib
from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET
from import_support import logical_roots

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
REPO = STAGE.parent
SAMPLES = STAGE / "05-官方来源" / "01-四类基础样例"
CONTAINER = os.environ.get("PATENT_CONTAINER", "patentdb")
DATASETS = {
    "us-application": (1, "US_APP_PUB", "美国专利申请公布全文文本数据", "US", "fulltext"),
    "us-grant": (2, "US_GRANT", "美国专利授权公告全文文本数据", "US", "fulltext"),
    "ep-fulltext": (3, "EP_FULLTEXT", "欧洲专利全文文本数据", "EP", "fulltext"),
    "ep-docdb": (4, "EP_DOCDB_ABS", "EP专利摘要DOCDB数据", "EP", "abstract"),
}

def local(e): return e.tag.rsplit("}", 1)[-1] if isinstance(e.tag, str) else ""
def children(e, name): return [x for x in list(e) if local(x) == name] if e is not None else []
def allnodes(e, name): return [x for x in e.iter() if local(x) == name] if e is not None else []
def first(e, name):
    a = allnodes(e, name)
    return a[0] if a else None
def val(e): return "".join(e.itertext()).strip() if e is not None else ""
def text(e, name): return val(first(e, name))
def attr(e, name, default=None): return (e.attrib.get(name) if e is not None else None) or default
def clean(s, limit=None):
    if s is None: return None
    s = str(s).replace("\x00", "").strip()
    return s[:limit] if limit else (s or None)
def date_parts(s):
    s = clean(s)
    if not s: return None, None
    raw = re.sub(r"[^0-9]", "", s)[:8]
    if len(raw) == 8 and raw != "99991231":
        try: return datetime.datetime.strptime(raw, "%Y%m%d").date().isoformat(), raw
        except ValueError: pass
    return None, raw or None
def integer(s, default=None):
    m = re.search(r"-?\d+", s or "")
    try: return int(m.group()) if m else default
    except ValueError: return default
def lang(s):
    s = (s or "EN").strip().upper()
    return s[:2] if len(s) >= 2 else "EN"
def q(s):
    if s is None: return "NULL"
    if isinstance(s, bool): return "TRUE" if s else "FALSE"
    if isinstance(s, (int, float)): return str(s)
    return "'" + str(s).replace("\x00", "").replace("'", "''") + "'"

def parse_document(root, bucket, source_file):
    application_kind = "NA"
    rootname = local(root)
    dataset_id, dataset_code, *_ = DATASETS[bucket]
    if rootname.startswith("us-patent-"):
        bib = first(root, "us-bibliographic-data-application") or first(root, "us-bibliographic-data-grant")
        pref = first(bib, "publication-reference")
        aref = first(bib, "application-reference")
        pdoc = first(pref, "document-id")
        adoc = first(aref, "document-id")
        application_kind = text(adoc, "kind") or "NA"
        pauth = text(pdoc, "country") or attr(root, "country", "US")
        pnr = text(pdoc, "doc-number")
        pkind = text(pdoc, "kind") or "NA"
        pdate = text(pdoc, "date") or attr(root, "date-publ")
        aa = text(adoc, "country") or pauth
        an = text(adoc, "doc-number") or pnr
        adate = text(adoc, "date")
        app_type = attr(aref, "appl-type")
        rootlang = lang(attr(root, "lang", "EN"))
        titles = [(lang(attr(x, "lang", rootlang)), val(x)) for x in allnodes(bib, "invention-title") if val(x)]
        abs_nodes = allnodes(root, "abstract")
        abstracts = [(lang(attr(x, "lang", rootlang)), val(x)) for x in abs_nodes if val(x)]
    elif rootname == "ep-patent-document":
        bib = first(root, "SDOBI")
        pauth = attr(root, "country", "EP")
        pnr = attr(root, "doc-number") or text(bib, "B110")
        pkind = attr(root, "kind") or text(bib, "B130") or "NA"
        pdate = attr(root, "date-publ") or text(first(bib, "B140"), "date")
        aa = pauth
        an = text(first(bib, "B200"), "B210")
        adate = text(first(bib, "B200"), "date")
        app_type = None
        rootlang = lang(attr(root, "lang", "EN"))
        titles = []
        b540 = first(bib, "B540")
        if b540 is not None:
            kids = list(b540)
            for i, item in enumerate(kids[:-1]):
                if local(item) == "B541" and local(kids[i+1]) == "B542" and val(kids[i+1]):
                    titles.append((lang(val(item)), val(kids[i+1])))
        abstracts = [(lang(attr(x, "lang", rootlang)), val(x)) for x in allnodes(root, "abstract") if val(x)]
    else:  # DOCDB exchange-document
        bib = first(root, "bibliographic-data")
        pauth = attr(root, "country", "EP")
        pnr = attr(root, "doc-number")
        pkind = attr(root, "kind") or "NA"
        pdate = attr(root, "date-publ")
        pubref = next((x for x in allnodes(bib, "publication-reference") if attr(x, "data-format") == "docdb"), first(bib, "publication-reference"))
        pdoc = first(pubref, "document-id")
        pauth = text(pdoc, "country") or pauth
        pnr = text(pdoc, "doc-number") or pnr
        pkind = text(pdoc, "kind") or pkind
        pdate = text(pdoc, "date") or pdate
        aref = next((x for x in allnodes(bib, "application-reference") if attr(x, "data-format") == "docdb"), first(bib, "application-reference"))
        adoc = first(aref, "document-id")
        application_kind = text(adoc, "kind") or "NA"
        aa = text(adoc, "country") or pauth
        an = text(adoc, "doc-number")
        adate = text(adoc, "date")
        app_type = None
        rootlang = lang(attr(pdoc, "lang", text(bib, "language-of-publication") or "EN"))
        titles = [(lang(attr(x, "lang", rootlang)), val(x)) for x in allnodes(bib, "invention-title") if val(x)]
        abstracts = [(lang(attr(x, "lang", rootlang)), val(x)) for x in children(root, "abstract") if val(x)]
    pd, pdraw = date_parts(pdate)
    ad, araw = date_parts(adate)
    if not pnr or not an:
        raise ValueError(f"missing publication/application number: {pnr!r}/{an!r}")
    if not ad:
        pass  # Unknown/partial dates stay NULL; original date remains in *_raw.
    if not titles:
        # Retain an explicit empty title only as an audit issue; title_text is NOT NULL.
        titles = []
    return {"root":root,"bib":bib,"source":source_file,"bucket":bucket,"dataset_id":dataset_id,
            "dataset_code":dataset_code,"pubkey":(pauth.upper(), pnr, pkind.upper()),
            "appkey":(aa.upper(), an, application_kind.upper()),"pub_date":pd,"pub_raw":pdraw,
            "app_date":ad,"app_raw":araw,"app_type":clean(app_type,20).upper() if app_type else None,
            "lang":rootlang,"titles":titles,"abstracts":abstracts}


def prepare_sources(samples, accept_document=None):
    SAMPLES=Path(samples)
    # Logical sample document extraction. DOCDB uses one wrapper file with multiple records.
    parsed, parse_errors, operations = [], [], []
    for path in sorted(p for p in SAMPLES.rglob("*") if p.is_file() and p.suffix.lower() == ".xml"):
        rel = path.relative_to(SAMPLES)
        bucket = rel.parts[0]
        if bucket not in DATASETS:
            continue
        try:
            roots = logical_roots(path.read_bytes())
            for index, node in enumerate(roots, 1):
                if accept_document is not None and not accept_document(node,bucket,path,index): continue
                if local(node)=="exchange-document" and node.get("status") in ("D","CV","DV"):
                    operations.append({"root":node,"source":str(rel),"bucket":bucket,"index":index})
                    continue
                try:
                    parsed.append(parse_document(node, bucket, str(rel)))
                except Exception as ex:
                    parse_errors.append({"dataset":bucket,"source_file":str(rel),"logical_document":str(index),
                      "xml_path":"/"+local(node),"error_type":type(ex).__name__,"message":str(ex)})
        except Exception as ex:
            parse_errors.append({"dataset":bucket,"source_file":str(rel),"logical_document":None,
              "xml_path":"/","error_type":type(ex).__name__,"message":str(ex)})



    # IDs are deterministic for this fixed sample set, so the loader is repeatable.
    apps = sorted({d["appkey"] for d in parsed}); pubs = sorted({d["pubkey"] for d in parsed})
    app_id = {k:i+1 for i,k in enumerate(apps)}; pub_id = {k:i+1 for i,k in enumerate(pubs)}
    patent_meta = {}
    for d in sorted(parsed, key=lambda x:(x["bucket"],x["source"],x["pubkey"])):
        patent_meta.setdefault(d["appkey"], d)

    tables = defaultdict(list); seen = defaultdict(set)
    unique_cols = {
     "dataset":["dataset_code"],"country_office":["ctry_code"],"language":["lang_code"],"kind_code":["office_code","kind_code"],
     "application_type":["appl_type_code"],"classification_scheme":["scheme_code"],"patent":["appln_auth","appln_nr","appln_kind"],
     "publication":["publn_auth","publn_nr","publn_kind"],"title":["publication_id","lang_code","title_type"],
     "abstract":["publication_id","lang_code"],"description_section":["publication_id","section_seq"],"drawing":["publication_id","figure_seq"],
     "claim":["publication_id","lang_code","claim_number"],"claim_dependency":["dependent_claim_id","parent_claim_id"],"person":["person_type","person_name"],"natural_person":["person_id"],"organization":["person_id"],
     "patent_applicant":["patent_id","sequence_nr"],"patent_inventor":["patent_id","sequence_nr"],"patent_assignee":["patent_id","sequence_nr"],
     "patent_agent":["patent_id","sequence_nr"],"patent_examiner":["patent_id","examiner_type","sequence_nr"],
     "classification":["scheme_code","symbol"],"patent_classification":["patent_id","scheme_code","symbol","source_type"],
     "patent_citation":["citing_publication_id","citation_type","citn_seq"],"non_patent_citation":["citation_id"],
     "priority_claim":["patent_id","sequence_nr"]}
    def add(table, cols, values):
        key = tuple(values[cols.index(c)] for c in unique_cols[table])
        if key in seen[table]: return
        seen[table].add(key); tables[table].append((cols, tuple(values)))

    # Reference/lookup rows required by imported records.
    countries = {"US","EP","WO","UN"}; languages = {"EN","DE","FR"}; kinds=set(); app_types=set(); schemes=set()
    for d in parsed:
        countries.update(x.text.strip().upper() for x in allnodes(d["root"],"country") if x.text and len(x.text.strip())==2)
        countries.update(x.text.strip().upper() for x in allnodes(d["root"],"ctry") if x.text and len(x.text.strip())==2)
        # Some official samples encode party country as an attribute rather than an element.
        for node in d["root"].iter():
            for key, value in node.attrib.items():
                if key.rsplit("}", 1)[-1] in ("country", "ctry") and len(value.strip()) == 2:
                    countries.add(value.strip().upper())
        countries.add(d["pubkey"][0]); countries.add(d["appkey"][0]); languages.add(d["lang"]); languages.update(l for l,_ in d["titles"]); languages.update(l for l,_ in d["abstracts"])
        kinds.add((d["pubkey"][0],d["pubkey"][2]))
        if d["app_type"]: app_types.add(d["app_type"])
        if d["bucket"]=="ep-docdb": schemes.update(("IPC","CPC"))
        else: schemes.update(("IPC","CPC"))
    for bucket,(did,code,name_cn,office,category) in DATASETS.items():
        add("dataset",["dataset_id","dataset_code","dataset_name_cn","dataset_name_en","office_code","data_category","file_format","manual_ref","description"],
            [did,code,name_cn,code,office,category,"XML",None,"从 A 阶段归档样例导入"])
    for c in sorted(countries): add("country_office",["ctry_code","st3_name","organisation_flag","is_epo_member","is_eu_member","discontinued"],[c,c,None,None,None,None])
    lang_names={"EN":"English","DE":"German","FR":"French","ES":"Spanish","IT":"Italian","ZH":"Chinese","JA":"Japanese"}
    for l in sorted(languages): add("language",["lang_code","name_en"],[l,lang_names.get(l,l)])
    for office,kind in sorted(kinds): add("kind_code",["office_code","kind_code","kind_description_en","kind_description_cn","is_grant"],[office,kind,"Sample publication kind "+kind,"样例文献种类 "+kind,"Y" if kind.startswith(("B","S")) else "N"])
    for t in sorted(app_types): add("application_type",["appl_type_code","appl_type_name_en","appl_type_name_cn"],[t,t.title(),t])
    for s in sorted(schemes): add("classification_scheme",["scheme_code","scheme_name_en","scheme_name_cn","is_hierarchical"],[s,s,s,"Y"])

    # Base application/publication rows.
    for key,d in patent_meta.items():
        add("patent",["patent_id","dataset_id","appln_auth","appln_nr","appln_kind","appln_nr_original","appl_type_code","appln_filing_date","appln_filing_date_raw","appln_lang","int_phase","reg_phase","nat_phase","us_application_series_code"],
            [app_id[key],d["dataset_id"],key[0],key[1],key[2],key[1],d["app_type"],d["app_date"],d["app_raw"],d["lang"],"N","N","N",clean(text(d["bib"],"us-application-series-code"),5)])
    for key,d in sorted({d["pubkey"]:d for d in parsed}.items()):
        add("publication",["publication_id","patent_id","dataset_id","publn_auth","publn_nr","publn_kind","publn_date","publn_date_raw","publn_lg","publn_first_grant","number_of_claims","number_of_figures"],
            [pub_id[key],app_id[d["appkey"]],d["dataset_id"],key[0],key[1],key[2],d["pub_date"],d["pub_raw"],d["lang"],"Y" if key[2].startswith(("B","S")) else "N",integer(text(d["bib"],"number-of-claims")),integer(text(first(d["root"],"figures"),"number-of-figures"))])

    # Titles, abstracts, claims, descriptions and drawings.
    title_id=abstract_id=section_id=drawing_id=claim_id=1
    claim_lookup={}; claim_pending=[]
    for d in parsed:
        pk=d["pubkey"]; pid=pub_id[pk]; root=d["root"]
        for l,txt in d["titles"]:
            if txt: add("title",["title_id","publication_id","lang_code","title_text","title_type","is_original","data_format"],[title_id,pid,l,clean(txt,2000),"INV","Y","XML"]); title_id+=1
        for l,txt in d["abstracts"]:
            if txt: add("abstract",["abstract_id","publication_id","lang_code","abstract_text","data_format","abstract_source"],[abstract_id,pid,l,txt,"XML",d["bucket"]]); abstract_id+=1
        desc=first(root,"description")
        if desc is not None:
            heading=None; seq=0
            for child in desc.iter():
                tag=local(child)
                if tag=="heading": heading=clean(val(child),500)
                elif tag=="p":
                    tx=clean(val(child))
                    if tx:
                        seq+=1; add("description_section",["section_id","publication_id","section_seq","section_level","heading","section_text"],[section_id,pid,seq,1,heading,tx]); section_id+=1
        for claimsroot in allnodes(root,"claims"):
            cl=lang(attr(claimsroot,"lang",d["lang"]))
            for seq,node in enumerate(children(claimsroot,"claim"),1):
                tx=clean(val(node))
                if not tx: continue
                num=integer(attr(node,"num")) or integer(tx) or seq
                xid=attr(node,"id")
                this_id=claim_id; claim_id+=1
                claim_lookup[(pk,cl,xid)]=this_id if xid else this_id
                typ="D" if allnodes(node,"claim-ref") else "I"
                add("claim",["claim_id","publication_id","lang_code","claim_number","claim_seq","claim_type","claim_text","xml_claim_id"],[this_id,pid,cl,num,seq,typ,tx,xid])
                for ref in allnodes(node,"claim-ref"):
                    rid=attr(ref,"idref")
                    if rid: claim_pending.append((this_id,pk,cl,rid,val(ref)))
        figs=allnodes(first(root,"drawings") or root,"figure")
        for seq,fig in enumerate(figs,1):
            image=first(fig,"img")
            if image is None: image=fig
            add("drawing",["drawing_id","publication_id","figure_seq","figure_id","image_file","alt_text"],[drawing_id,pid,seq,attr(fig,"id"),attr(image,"file",attr(image,"id")),clean(attr(image,"alt"),200)]); drawing_id+=1
    for dependent,pk,cl,rid,reftext in claim_pending:
        parent=claim_lookup.get((pk,cl,rid))
        if parent and parent!=dependent:
            add("claim_dependency",["dependent_claim_id","parent_claim_id","dependency_type","ref_text"],[dependent,parent,"claim-ref",clean(reftext,200)])

    # People and role links across US, EP and DOCDB structures.
    people_by_key={}; person_role_pending=[]
    for d in parsed:
        root,bib=d["root"],d["bib"]; roles=[]
        if local(root).startswith("us-patent-"):
            parties=first(bib,"us-parties")
            for rname,table in (("us-applicant","patent_applicant"),("inventor","patent_inventor")):
                for n in allnodes(parties,rname): roles.append((table,n,"N"))
            for rname,table in (("assignee","patent_assignee"),("agent","patent_agent")):
                for n in allnodes(bib,rname): roles.append((table,n,"N"))
            for rname,etype in (("primary-examiner","P"),("assistant-examiner","A")):
                for n in allnodes(bib,rname): roles.append(("patent_examiner",n,etype))
        elif local(root)=="ep-patent-document":
            b700=first(first(root,"SDOBI"),"B700")
            for nm,table in (("B711","patent_applicant"),("B721","patent_inventor"),("B731","patent_assignee"),("B741","patent_agent")):
                for n in allnodes(b700,nm): roles.append((table,n,"N"))
        else:
            for nm,table in (("applicant","patent_applicant"),("inventor","patent_inventor")):
                for n in allnodes(bib,nm): roles.append((table,n,"N"))
        seqs=defaultdict(int)
        for table,node,examtype in roles:
            ab=first(node,"addressbook") or node
            org=text(ab,"orgname")
            firstn=text(ab,"first-name"); lastn=text(ab,"last-name")
            if not firstn and not lastn: lastn=text(ab,"snm")
            nm=org or " ".join(x for x in (firstn,lastn) if x) or text(ab,"name")
            if not nm: continue
            ptype="L" if org else "N"; pkey=(ptype," ".join(nm.split()).casefold())
            address=first(ab,"address") or first(ab,"adr")
            p=people_by_key.setdefault(pkey,{"name":clean(nm,500),"type":ptype,"dataset_id":d["dataset_id"],"org":clean(org,500),"first":clean(firstn,200),"last":clean(lastn,200),"city":clean(text(address,"city"),200),"country":clean(text(address,"country") or text(address,"ctry"),2)})
            seqs[table]+=1
            seq=integer(attr(node,"sequence")) or seqs[table]
            person_role_pending.append((table,d["appkey"],pkey,seq,examtype,node))
    person_ids={k:i+1 for i,k in enumerate(sorted(people_by_key))}
    for key,p in sorted(people_by_key.items()):
        pid=person_ids[key]
        add("person",["person_id","person_name","person_name_orig","person_type","city","ctry_code","source_dataset_id"],[pid,p["name"],p["name"],p["type"],p["city"],p["country"].upper() if p["country"] else None,p["dataset_id"]])
        if p["type"]=="N": add("natural_person",["person_id","last_name","first_name"],[pid,p["last"],p["first"]])
        else: add("organization",["person_id","org_name"],[pid,p["org"]])
    role_seqs=defaultdict(int)
    for table,appkey,pkey,seq,examtype,node in person_role_pending:
        patent=app_id[appkey]; person=person_ids[pkey]
        if table=="patent_examiner":
            add(table,["patent_id","person_id","examiner_type","sequence_nr","department"],[patent,person,examtype,seq,clean(text(node,"department"),20)])
        elif table=="patent_applicant":
            add(table,["patent_id","person_id","sequence_nr","applicant_type","authority_category"],[patent,person,seq,clean(attr(node,"appl-type"),20),clean(attr(node,"applicant-authority-category"),50)])
        elif table=="patent_inventor": add(table,["patent_id","person_id","sequence_nr","designation"],[patent,person,seq,clean(attr(node,"designation"),50)])
        elif table=="patent_assignee": add(table,["patent_id","person_id","sequence_nr","role_code"],[patent,person,seq,clean(text(node,"role"),5)])
        elif table=="patent_agent": add(table,["patent_id","person_id","sequence_nr","rep_type"],[patent,person,seq,clean(attr(node,"rep-type"),20)])

    # Classifications from US structured fields and EP/DOCDB text symbols.
    class_items=[]
    patent_symbols=set()
    pattern=re.compile(r"\b([A-HY])\s*(\d{2})\s*([A-Z])\s*(\d+)\s*/\s*(\d+)\b",re.I)
    for d in parsed:
        root,bib=d["root"],d["bib"]; pk=d["pubkey"]
        for node in allnodes(root,"classification-ipcr")+allnodes(root,"classification-cpc"):
            nm=local(node); scheme="CPC" if nm=="classification-cpc" else "IPC"
            raw=val(node)
            sec=text(node,"section"); cls=text(node,"class"); sub=text(node,"subclass"); mg=text(node,"main-group"); sg=text(node,"subgroup")
            if sec and cls and sub and mg and sg: symbol=f"{sec}{cls}{sub}{mg}/{sg}"
            else:
                m=pattern.search(raw)
                if not m: continue
                symbol="".join(m.group(i).upper() for i in (1,2,3,4))+"/"+m.group(5)
            symbol=clean(symbol,30)
            if not symbol: continue
            seq=integer(attr(node,"sequence"))
            pos=text(node,"symbol-position") or None; cval=text(node,"classification-value") or None
            level=text(node,"classification-level") or None
            office=text(first(node,"generating-office"),"country") or d["pubkey"][0]
            act,_=date_parts(text(first(node,"action-date"),"date"))
            class_items.append((d["appkey"],scheme,symbol,raw,pos,cval,level,office,nm,act,seq))
            patent_symbols.add((d["appkey"],scheme,symbol))
    for d in parsed:
        if local(d["root"])=="ep-patent-document":
            b510=first(first(d["root"],"SDOBI"),"B510EP")
            for node in allnodes(b510,"classification-ipcr"):
                raw=val(node); m=pattern.search(raw)
                if m:
                    symbol="".join(m.group(i).upper() for i in (1,2,3,4))+"/"+m.group(5)
                    class_items.append((d["appkey"],"IPC",symbol,raw,None,None,None,"EP","EP_IPCR",None,integer(attr(node,"sequence"))))
                    patent_symbols.add((d["appkey"],"IPC",symbol))
    # DOCDB legacy IPC is a distinct source representation, retained beside IPCR.
    for d in parsed:
        if local(d["root"])!="exchange-document": continue
        legacy=first(d["bib"],"classification-ipc")
        for nm in ("main-classification","further-classification"):
            for node in children(legacy,nm):
                raw=val(node); m=pattern.search(raw)
                if m:
                    symbol="".join(m.group(i).upper() for i in (1,2,3,4))+"/"+m.group(5)
                    class_items.append((d["appkey"],"IPC",symbol,raw,None,None,None,d["pubkey"][0],"LEGACY_IPC",None,None))
    for i,(app,scheme,symbol,*rest) in enumerate(class_items,1):
        sec=pattern.match(symbol)
        m=pattern.search(symbol)
        add("classification",["scheme_code","symbol","section","class_no","subclass","main_group","subgroup"],[scheme,symbol,m.group(1).upper() if m else None,m.group(2) if m else None,m.group(3).upper() if m else None,m.group(4) if m else None,m.group(5) if m else None])
        raw,pos,cval,level,office,stype,act,seq=rest
        add("patent_classification",["patent_classification_id","patent_id","scheme_code","symbol","symbol_raw","position","value","classification_level","generating_office","source_type","action_date","sequence_nr"],[i,app_id[app],scheme,symbol,clean(raw,60),clean(pos,1),clean(cval,1),clean(level,1),clean(office,2),clean(stype,20),act,seq])

    # Structured citations (US patent citations, EP B560, DOCDB references-cited).
    citation_id=npl_id=1
    for d in parsed:
        root,bib=d["root"],d["bib"]; citation_nodes=[]
        if local(root).startswith("us-patent-"):
            cited=first(bib,"us-references-cited")
            citation_nodes=allnodes(cited,"us-citation")
        elif local(root)=="ep-patent-document":
            b560=first(first(first(root,"SDOBI"),"B500"),"B560")
            if b560 is not None:
                citation_nodes=[x for x in list(b560) if local(x) in ("B561","B562")]
        else:
            refs=first(bib,"references-cited")
            citation_nodes=children(refs,"citation")
        for seq,node in enumerate(citation_nodes,1):
            pat=first(node,"patcit") or first(node,"B561")
            npl=first(node,"nplcit")
            if npl is None: npl=first(node,"B562")
            is_npl=npl is not None and pat is None
            docid=first(pat,"document-id") if pat is not None else None
            country=(text(docid,"country") or attr(docid,"country") or "") if docid is not None else ""
            num=text(docid,"doc-number") if docid is not None else ""
            kind=text(docid,"kind") if docid is not None else ""
            if not is_npl and docid is None:
                m=re.fullmatch(r"\s*([A-Z]{2})-([A-Z]\d?)-\s*([0-9 /]+)\s*",val(node))
                if m: country,kind,num=m.group(1),m.group(2),re.sub(r"\s+","",m.group(3))
            date,date_raw=date_parts(text(docid,"date") if docid is not None else "")
            raw=clean(val(npl) if is_npl else (val(pat) if pat is not None else val(node)),500)
            seqno=integer(attr(node,"num") or attr(pat,"num") or attr(npl,"num")) or seq
            cid=citation_id; citation_id+=1
            add("patent_citation",["citation_id","citing_patent_id","citing_publication_id","citation_type","cited_country","cited_doc_number","cited_doc_kind","cited_doc_date","cited_doc_date_raw","cited_raw_text","citn_seq","citn_origin"],
                [cid,app_id[d["appkey"]],pub_id[d["pubkey"]],"N" if is_npl else "P",clean(country,2) or None,clean(num,30),clean(kind,2),date,clean(date_raw,8),raw,seqno,"NPL" if is_npl else "PATENT"])
            if is_npl:
                add("non_patent_citation",["npl_id","citation_id","npl_type","npl_biblio"],[npl_id,cid,"NPL",clean(val(npl))]); npl_id+=1

    # Priorities from USPTO and DOCDB structured bibliographic sections.
    priority_id=1
    for d in parsed:
        root,bib=d["root"],d["bib"]; nodes=allnodes(bib,"priority-claim")
        for seq,node in enumerate(nodes,1):
            docid=first(node,"document-id")
            if docid is None: docid=node
            country=text(docid,"country"); nr=text(docid,"doc-number"); dt,raw=date_parts(text(docid,"date"))
            if not country or not nr: continue
            add("priority_claim",["priority_id","patent_id","sequence_nr","prior_country","prior_appln_nr","prior_date","prior_date_raw","priority_kind"],
                [priority_id,app_id[d["appkey"]],integer(attr(node,"sequence")) or seq,country[:2].upper(),clean(nr,50),dt,clean(raw,8),clean(attr(node,"kind"),20)]); priority_id+=1

    ORDER=["country_office","language","dataset","kind_code","application_type","classification_scheme","patent","publication","title","abstract","description_section","drawing","claim","claim_dependency","person","natural_person","organization","patent_applicant","patent_inventor","patent_assignee","patent_agent","patent_examiner","classification","patent_classification","patent_citation","non_patent_citation","priority_claim"]
    return locals()
