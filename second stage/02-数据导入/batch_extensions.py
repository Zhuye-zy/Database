"""Source-backed DOCDB families and ancillary mappings for arbitrary reviewed batches."""
from sample_mapping import *
def extend(ns):
    add=ns["add"];unique=ns["unique_cols"];order=ns["ORDER"]
    definitions={
      "patent_family":["family_type","source_family_id"],
      "patent_family_member":["family_id","member_seq"],
      "family_member_application_ref":["member_id","data_format","appln_nr"],
      "family_member_publication_ref":["member_id","data_format","sequence_nr","publn_nr"],
      "family_abstract":["family_id","abstract_seq"],
      "designated_state":["patent_id","state_code","designation_type"],
      "citation_category":["category_code"],
      "patent_citation_category":["citation_id","category_code","relevant_claim"],
      "related_application":["patent_id","sequence_nr"],
      "international_application":["patent_id"]}
    unique.update(definitions);order.extend(definitions)
    def info(ref):
        doc=first(ref,"document-id")
        return text(doc,"country"),text(doc,"doc-number"),text(doc,"kind"),text(doc,"date")
    def findapp(country,nr):
        return next((v for k,v in ns["app_id"].items() if k[0]==country and k[1]==nr),None)
    mid=arid=prid=abid=rid=iid=0
    for d in ns["parsed"]:
        root=d["root"];pid=ns["app_id"][d["appkey"]];pubid=ns["pub_id"][d["pubkey"]]
        if local(root)=="exchange-document":
            fam=first(root,"patent-family");fid=integer(root.get("family-id"))
            if fam is not None and fid:
                add("patent_family",["family_id","family_type","source_family_id","dataset_id","representative_publication_id","note"],
                    [fid,"DOCDB",fid,d["dataset_id"],pubid,"IPDPS DOCDB exchange-document family-id"])
                for seq,member in enumerate(children(fam,"family-member"),1):
                    mid+=1;ref=next((x for x in children(member,"application-reference") if x.get("data-format")=="docdb"),None)
                    ca,na,ka,da=info(ref)
                    add("patent_family_member",["member_id","family_id","member_patent_id","member_seq","is_representative","member_type"],
                        [mid,fid,findapp(ca,na),seq,"Y" if attr(ref,"is-representative")=="YES" else "N","DOCDB"])
                    for ref in children(member,"application-reference"):
                        ca,na,ka,da=info(ref)
                        if not na:continue
                        arid+=1
                        add("family_member_application_ref",["member_appln_ref_id","member_id","data_format","is_representative","doc_id","country_code","appln_nr","appln_kind"],
                            [arid,mid,ref.get("data-format","unknown"),"Y" if ref.get("is-representative")=="YES" else "N",ref.get("doc-id"),ca or None,na,ka or None])
                    for ref in children(member,"publication-reference"):
                        ca,na,ka,da=info(ref)
                        if not na:continue
                        prid+=1
                        add("family_member_publication_ref",["member_publn_ref_id","member_id","data_format","sequence_nr","doc_id","country_code","publn_nr","publn_kind","publn_date_raw"],
                            [prid,mid,ref.get("data-format","unknown"),integer(ref.get("sequence"),1),ref.get("doc-id"),ca or None,na,ka or None,da or None])
                for seq,ab in enumerate(children(fam,"abstract"),1):
                    abid+=1
                    add("family_abstract",["family_abstract_id","family_id","abstract_seq","lang_code","abstract_text","data_format","abstract_source","source_country","source_doc_number","source_kind"],
                        [abid,fid,seq,lang(ab.get("lang")),val(ab),ab.get("data-format"),ab.get("abstract-source"),ab.get("country"),ab.get("doc-number"),ab.get("kind")])
            for country in allnodes(first(root,"designation-epc"),"country"):
                if val(country):add("designated_state",["patent_id","state_code","designation_type"],[pid,val(country).upper(),"CONTRACT"])
        if local(root).startswith("us-patent-"):
            bib=d["bib"]
            for seq,cit in enumerate(allnodes(first(bib,"us-references-cited"),"us-citation"),1):
                label=text(cit,"category").lower()
                if label not in ("cited by applicant","cited by examiner"):continue
                code="APPLICANT" if "applicant" in label else "EXAMINER"
                add("citation_category",["category_code","category_desc_en","category_desc_cn","source_standard","note"],
                    [code,label,label,"USPTO_XML","us-citation/category in official US grant samples"])
                number=integer(cit.get("num"),seq)
                for cols,row in ns["tables"]["patent_citation"]:
                    c=dict(zip(cols,row))
                    if c["citing_publication_id"]==pubid and c["citn_seq"]==number:
                        add("patent_citation_category",["citation_id","category_code","relevant_claim"],[c["citation_id"],code,0])
            rel=first(bib,"us-related-documents");sequence=0
            for group in list(rel) if rel is not None else []:
                typ=local(group).upper().replace("-","_")[:20]
                relation=first(group,"relation")
                ref=first(relation,"parent-doc") if relation is not None else group
                ca,na,ka,da=info(ref)
                if not na:continue
                rid+=1;sequence+=1;grant=first(ref,"parent-grant-document")
                gnr=info(grant)[1] if grant is not None else (na if typ=="RELATED_PUBLICATION" else None)
                add("related_application",["relation_id","patent_id","relation_type","related_country","related_appln_nr","related_filing_date","related_publn_nr","parent_status","sequence_nr"],
                    [rid,pid,typ,ca or None,na if typ!="RELATED_PUBLICATION" else None,date_parts(da)[0],gnr,text(ref,"parent-status") or None,sequence])
            pct=first(bib,"pct-or-regional-filing-data")
            if pct is not None:
                ca,na,ka,da=info(pct)
                if na:
                    iid+=1
                    add("international_application",["int_appln_id","patent_id","int_appln_nr","int_filing_date","receiving_office","regional_office","national_phase_date"],
                        [iid,pid,na,date_parts(da)[0],ca or None,"US",date_parts(text(pct,"us-371c124-date"))[0]])
