#!/usr/bin/env python3
"""Complete sample-backed PostgreSQL mappings from official CNIPA/IPDPS XML."""
from pathlib import Path
import datetime, re, subprocess, os, xml.etree.ElementTree as ET

from import_support import logical_roots, write_log, assert_source_snapshot

HERE=Path(__file__).resolve().parent
SAMPLES=HERE.parent/'05-官方来源'/'01-四类基础样例'
LEGAL=HERE.parent/'05-官方来源'/'02-IPDPS补充样例'/'03-法律状态原文'/'LEGSTAT-202122-EP-AppDateFrom20190314-0016.xml'
def tag(e): return e.tag.rsplit('}',1)[-1]
def direct(e,n): return [x for x in e if tag(x)==n] if e is not None else []
def nodes(e,n): return [x for x in e.iter() if tag(x)==n] if e is not None else []
def one(e,n): return next(iter(nodes(e,n)),None)
def value(e): return ''.join(e.itertext()).strip() if e is not None else ''
def txt(e,n): return value(one(e,n))
def q(x):
 if x is None:return 'NULL'
 if isinstance(x,int):return str(x)
 return "'"+str(x).replace("\x00","").replace("'","''")+"'"
def raw(x):return x
def sqlvals(items):
 return ','.join(str(x) if isinstance(x,Raw) else q(x) for x in items)
class Raw(str):pass
verification_queries=[]
def ins(table,cols,items):
 keys={'country_office':['ctry_code'],'dataset':['dataset_id'],'patent':['patent_id'],
 'publication':['publication_id'],'legal_event_code':['event_auth','event_code'],
 'patent_family':['family_id'],'family_abstract':['family_abstract_id'],'patent_family_member':['member_id'],
 'family_member_application_ref':['member_appln_ref_id'],'family_member_publication_ref':['member_publn_ref_id'],
 'legal_status_event':['event_id'],'designated_state':['patent_id','state_code','designation_type'],
 'citation_category':['category_code'],'related_application':['relation_id'],'international_application':['int_appln_id'],
 'ipc_techn_field':['ipc_maingroup_symbol']}[table]
 verification_queries.append("SELECT "+q(table)+" AS table_name, CASE WHEN EXISTS(SELECT 1 FROM patentdb."+table+" WHERE "+" AND ".join(c+" IS NOT DISTINCT FROM "+(str(v) if isinstance(v,Raw) else q(v)) for c,v in zip(cols,items))+") THEN 0 ELSE 1 END AS mismatches")
 update=[c+'=EXCLUDED.'+c for c in cols if c not in keys]
 action='DO UPDATE SET '+','.join(update) if update else 'DO NOTHING'
 stmts.append('INSERT INTO patentdb.'+table+' ('+','.join(cols)+') VALUES ('+sqlvals(items)+') ON CONFLICT ('+','.join(keys)+') '+action+';')
def dt(x):
 s=re.sub('[^0-9]','',x or '')[:8]
 if s=='99991231':return None
 try:return datetime.datetime.strptime(s,'%Y%m%d').date().isoformat() if len(s)==8 else None
 except ValueError:return None
def patt(auth,nr):
 return Raw('(SELECT patent_id FROM patentdb.patent WHERE appln_auth='+q(auth)+' AND appln_nr='+q(nr)+' ORDER BY patent_id LIMIT 1)')
def pub(auth,nr,kind=None):
 cond='publn_auth='+q(auth)+' AND publn_nr='+q(nr)
 if kind:cond+=' AND publn_kind='+q(kind)
 return Raw('(SELECT publication_id FROM patentdb.publication WHERE '+cond+' ORDER BY publication_id LIMIT 1)')
def docinfo(ref):
 d=one(ref,'document-id')
 return txt(d,'country'),txt(d,'doc-number'),txt(d,'kind'),txt(d,'date')
stmts=['BEGIN;','SET search_path TO patentdb,public;']
import sys
if '--refresh-reviewed' in sys.argv:
 stmts.append("DELETE FROM patentdb.family_abstract WHERE family_id IN (6030991,6034510);")
docs=[]
assert_source_snapshot(SAMPLES)
for path in sorted(p for p in SAMPLES.rglob('*') if p.is_file() and p.suffix.lower()=='.xml'):
 for root in logical_roots(path.read_bytes()): docs.append((root,path))
legal_text=LEGAL.read_text(encoding='utf-8')
if not legal_text.rstrip().endswith('</legal-status-documents>'):
 legal_text+='\n</legal-status-documents>'
legalroot=ET.fromstring(legal_text)
legaldocs=direct(legalroot,'legal-status-document')
if len(legaldocs)!=1:raise RuntimeError('Expected exactly one official legal-status sample document')
ld=legaldocs[0]
state_codes={value(x).upper() for x in nodes(ld,'country') if len(value(x))==2}
for code in sorted(state_codes):
 ins('country_office',['ctry_code','st3_name','organisation_flag','is_epo_member','is_eu_member','discontinued'],[code,code,None,None,None,None])
ins('dataset',['dataset_id','dataset_code','dataset_name_cn','dataset_name_en','office_code','data_category','file_format','manual_ref','description'],
 [5,'EP_LEGAL_STATUS','EP patent legal status sample','EP patent legal status sample','EP','legal-status','XML','https://ipdps.cnipa.gov.cn/#/MyHome','Official IPDPS sample EP-PA-PRSO-FILE, one logical document'])
app=one(ld,'application-reference'); publication=one(ld,'publication-reference')
aa,an,ak,ad=docinfo(app);pa,pn,pk,pd=docinfo(publication)
if not all((aa,an,ad,pa,pn,pk,pd)):raise RuntimeError('Incomplete legal sample bibliographic identifiers')
ins('patent',['patent_id','dataset_id','appln_auth','appln_nr','appln_kind','appln_nr_original','appln_filing_date','appln_filing_date_raw','appln_lang','int_phase','reg_phase','nat_phase'],
 [1001,5,aa,an,ak or 'NA',an,dt(ad),ad,publication.get('lang','en').upper()[:2],'N','N','N'])
ins('publication',['publication_id','patent_id','dataset_id','publn_auth','publn_nr','publn_kind','publn_date','publn_date_raw','publn_lg','publn_first_grant','docdb_doc_id'],
 [1001,1001,5,pa,pn,pk,dt(pd),pd,publication.get('lang','en').upper()[:2],'N',publication.get('doc-id')])
legal_categories={}
for ev in direct(ld,'legal-event'):
 code=txt(ev,'event-code');office=ev.get('providing-office','EP')
 desc=next((value(x) for x in nodes(ev,'event-description') if x.get('lang')=='en'),code)
 legal_categories[(office,code)]=desc[:250]
for (office,code),desc in sorted(legal_categories.items()):
 ins('legal_event_code',['event_auth','event_code','event_descr','event_descr_orig'],[office,code,desc,desc])
# The two DOCDB records carry authentic source-family identifiers and multi-valued member references.
for d,path in docs:
 if tag(d)!='exchange-document':continue
 fid=int(d.attrib['family-id']); fam=one(d,'patent-family')
 if fam is None:continue
 ins('patent_family',['family_id','family_type','source_family_id','dataset_id','representative_publication_id','note'],
  [fid,'DOCDB',fid,4,pub(d.get('country','EP'),d.get('doc-number'),d.get('kind')),'IPDPS DOCDB exchange-document family-id'])
 for ai,ab in enumerate(direct(fam,'abstract'),1):
  ins('family_abstract',['family_abstract_id','family_id','abstract_seq','lang_code','abstract_text','data_format','abstract_source','source_country','source_doc_number','source_kind'],
   [fid*100+ai,fid,ai,ab.get('lang','en').upper()[:2],value(ab),ab.get('data-format'),ab.get('abstract-source'),ab.get('country'),ab.get('doc-number'),ab.get('kind')])
 for seq,member in enumerate(direct(fam,'family-member'),1):
  mid=fid*100+seq
  ar=next((r for r in direct(member,'application-reference') if r.get('data-format')=='docdb'),None)
  ca,na,ka,da=docinfo(ar)
  rep=ar.get('is-representative','NO') if ar is not None else 'NO'
  ins('patent_family_member',['member_id','family_id','member_patent_id','member_seq','is_representative','member_type'],
   [mid,fid,patt(ca,na) if ca and na else None,seq,'Y' if rep=='YES' else 'N','DOCDB'])
  for ri,ref in enumerate(direct(member,'application-reference'),1):
   country,number,kind,date=docinfo(ref)
   if not number:continue
   ins('family_member_application_ref',['member_appln_ref_id','member_id','data_format','is_representative','doc_id','country_code','appln_nr','appln_kind'],
    [mid*100+ri,mid,ref.get('data-format','unknown'),'Y' if ref.get('is-representative')=='YES' else 'N',ref.get('doc-id'),country or None,number,kind or None])
  for ri,ref in enumerate(direct(member,'publication-reference'),1):
   country,number,kind,date=docinfo(ref)
   if not number:continue
   ins('family_member_publication_ref',['member_publn_ref_id','member_id','data_format','sequence_nr','doc_id','country_code','publn_nr','publn_kind','publn_date_raw'],
    [mid*100+ri,mid,ref.get('data-format','unknown'),int(ref.get('sequence','1')),ref.get('doc-id'),country or None,number,kind or None,date or None])
# DOCDB contracting states are multivalued, too.
for d,path in docs:
 if tag(d)!='exchange-document':continue
 aa,an,ak,ad=docinfo(next((r for r in nodes(one(d,'bibliographic-data'),'application-reference') if r.get('data-format')=='docdb'),None))
 for country in nodes(one(d,'designation-epc'),'country'):
  if value(country):ins('designated_state',['patent_id','state_code','designation_type'],[patt(aa,an),value(country).upper(),'CONTRACT'])
# INPADOC legal-status example: separate source family with a real family ID.
lfid=int(ld.get('family-id'))
ins('patent_family',['family_id','family_type','source_family_id','dataset_id','representative_publication_id','note'],
 [lfid,'INPADOC',lfid,5,1001,'IPDPS EP legal-status-document family-id'])
lmid=lfid*100+1
ins('patent_family_member',['member_id','family_id','member_patent_id','member_seq','is_representative','member_type'],[lmid,lfid,1001,1,'Y','INPADOC'])
ins('family_member_application_ref',['member_appln_ref_id','member_id','data_format','doc_id','country_code','appln_nr','appln_kind'],
 [lmid*100+1,lmid,'legal-status',app.get('doc-id'),aa,an,ak or None])
ins('family_member_publication_ref',['member_publn_ref_id','member_id','data_format','sequence_nr','doc_id','country_code','publn_nr','publn_kind','publn_date_raw'],
 [lmid*100+1,lmid,'legal-status',1,publication.get('doc-id'),pa,pn,pk,pd])
for ev in direct(ld,'legal-event'):
 seq=int(ev.get('sequence-number'))
 office=ev.get('providing-office','EP');code=txt(ev,'event-code')
 desc=next((value(x) for x in nodes(ev,'event-description') if x.get('lang')=='en'),code)
 detail=txt(ev,'text') or desc
 ins('legal_status_event',['event_id','patent_id','dataset_id','event_seq_nr','event_type','event_auth','event_code','event_publn_date','event_effective_date','event_text','ref_doc_auth','ref_doc_nr','ref_doc_kind'],
  [int(ev.get('event-id')),1001,5,seq,txt(ev,'event-class') or None,office,code,dt(txt(ev,'event-date')),dt(txt(ev,'event-date-effective')),detail[:1000],pa,pn,pk])
 for country in [value(x) for ds in nodes(ev,'designated-states') for x in direct(ds,'country')]:
  ins('designated_state',['patent_id','state_code','designation_type'],[1001,country.upper(),'CONTRACT'])
# USPTO source category is a document-level citation label.
for code,english in [('APPLICANT','cited by applicant'),('EXAMINER','cited by examiner')]:
 ins('citation_category',['category_code','category_desc_en','category_desc_cn','source_standard','note'],
  [code,english,english,'USPTO_XML','us-citation/category in official US grant samples'])
stmts.append('CREATE TEMP TABLE sample_citation_category(pubnr text, pubkind text, seq int, category_code text) ON COMMIT DROP;')
catrows=[]
for d,path in docs:
 if not tag(d).startswith('us-patent-'):continue
 bib=one(d,'us-bibliographic-data-application') or one(d,'us-bibliographic-data-grant')
 p=one(bib,'publication-reference')
 country,pnr,pkind,pdate=docinfo(p)
 cites=nodes(one(bib,'us-references-cited'),'us-citation')
 for i,cit in enumerate(cites,1):
  cat=txt(cit,'category').lower()
  if cat not in ('cited by applicant','cited by examiner'):continue
  seq=int(cit.get('num') or i)
  catrows.append((pnr,pkind,seq,'APPLICANT' if 'applicant' in cat else 'EXAMINER'))
  if len(catrows)==200:
   stmts.append('INSERT INTO sample_citation_category VALUES '+','.join('('+sqlvals(x)+')' for x in catrows)+';');catrows=[]
if catrows:stmts.append('INSERT INTO sample_citation_category VALUES '+','.join('('+sqlvals(x)+')' for x in catrows)+';')
stmts.append("""INSERT INTO patentdb.patent_citation_category(citation_id,category_code,relevant_claim)
SELECT DISTINCT c.citation_id,m.category_code,0 FROM sample_citation_category m
JOIN patentdb.publication p ON p.publn_nr=m.pubnr AND p.publn_kind=m.pubkind AND p.publn_auth='US'
JOIN patentdb.patent_citation c ON c.citing_publication_id=p.publication_id AND c.citn_seq=m.seq
ON CONFLICT DO NOTHING;""")
# USPTO continuation, reissue, provisional and related-publication references.
relation_id=20000
for d,path in docs:
 if not tag(d).startswith('us-patent-'):continue
 bib=one(d,'us-bibliographic-data-application') or one(d,'us-bibliographic-data-grant')
 aa,an,ak,ad=docinfo(one(bib,'application-reference'))
 rel=one(bib,'us-related-documents')
 if rel is None:rel=ET.Element('empty')
 seq=0
 for group in list(rel):
  typ=tag(group).upper().replace('-','_')[:20]
  relation=one(group,'relation')
  ref=one(relation,'parent-doc') if relation is not None else group
  country,number,kind,date=docinfo(ref)
  if not number:continue
  seq+=1;relation_id+=1
  grant=one(ref,'parent-grant-document')
  gnr=docinfo(grant)[1] if grant is not None else (number if typ=='RELATED_PUBLICATION' else None)
  ins('related_application',['relation_id','patent_id','relation_type','related_country','related_appln_nr','related_filing_date','related_publn_nr','parent_status','sequence_nr'],
   [relation_id,patt(aa,an),typ,country or None,number if typ!='RELATED_PUBLICATION' else None,dt(date),gnr,txt(ref,'parent-status') or None,seq])
 pct=one(bib,'pct-or-regional-filing-data')
 if pct is not None:
  country,number,kind,date=docinfo(pct)
  if number:
   ins('international_application',['int_appln_id','patent_id','int_appln_nr','int_filing_date','receiving_office','regional_office','national_phase_date'],
    [2001,patt(aa,an),number,dt(date),country or None,'US',dt(txt(pct,'us-371c124-date'))])
# Derived searchable title tokens keep the underlying source exactly traceable.
stmts.append("""INSERT INTO patentdb.keyword(keyword_text,lang_code,source)
SELECT DISTINCT lower(tok),t.lang_code,'TITLE_DERIVED'
FROM patentdb.title t CROSS JOIN LATERAL regexp_split_to_table(t.title_text,'[^A-Za-z]+') AS tok
WHERE t.lang_code='EN' AND length(tok)>=5
ON CONFLICT DO NOTHING;""")
stmts.append("""INSERT INTO patentdb.patent_keyword(patent_id,keyword_id,weight,source)
SELECT DISTINCT p.patent_id,k.keyword_id,1.0,'TITLE_DERIVED'
FROM patentdb.title t JOIN patentdb.publication u USING(publication_id)
JOIN patentdb.patent p USING(patent_id)
CROSS JOIN LATERAL regexp_split_to_table(t.title_text,'[^A-Za-z]+') AS tok
JOIN patentdb.keyword k ON k.keyword_text=lower(tok) AND k.lang_code=t.lang_code
WHERE t.lang_code='EN' AND length(tok)>=5
ON CONFLICT DO NOTHING;""")
# WIPO IPC technology concordance: H04L is Digital communication, field 4.
ins('ipc_techn_field',['ipc_maingroup_symbol','techn_field_nr','techn_sector','techn_field'],
 ['H04L9/00',4,'Electrical engineering','Digital communication'])
# Only derive family edges when BOTH families are actually identified in source data.
stmts.append("""INSERT INTO patentdb.family_citation(citing_family_id,cited_family_id)
SELECT DISTINCT src.family_id,dst.family_id
FROM patentdb.patent_citation c
JOIN patentdb.publication p ON p.publication_id=c.citing_publication_id
JOIN patentdb.family_member_publication_ref sr ON sr.country_code=p.publn_auth
 AND sr.publn_nr=p.publn_nr AND sr.publn_kind=p.publn_kind
JOIN patentdb.patent_family_member src ON src.member_id=sr.member_id
JOIN patentdb.family_member_publication_ref dr ON dr.country_code=c.cited_country
 AND dr.publn_nr=c.cited_doc_number AND dr.publn_kind=c.cited_doc_kind
JOIN patentdb.patent_family_member dst ON dst.member_id=dr.member_id
WHERE src.family_id<>dst.family_id ON CONFLICT DO NOTHING;""")
for table,col in [('patent','patent_id'),('publication','publication_id'),('keyword','keyword_id'),('patent_family','family_id'),('patent_family_member','member_id'),('family_member_application_ref','member_appln_ref_id'),('family_member_publication_ref','member_publn_ref_id'),('family_abstract','family_abstract_id'),('legal_status_event','event_id'),('related_application','relation_id'),('international_application','int_appln_id')]:
 stmts.append("SELECT setval(pg_get_serial_sequence('patentdb."+table+"','"+col+"'),(SELECT max("+col+") FROM patentdb."+table+"),true);")
stmts.append('COMMIT;')
sql='\n'.join(stmts)+'\n'
if __name__=='__main__':
 import sys
 if '--dry-run' in sys.argv:
  print('source_docs',len(docs),'legal_docs',len(legaldocs),'citation_category_rows',len([x for d,p in docs for x in nodes(d,'category') if tag(x)=='category']))
  print('sql_bytes',len(sql.encode()))
  sys.exit(0)
 result=subprocess.run(['docker','exec','-i',os.environ.get('PATENT_CONTAINER','patentdb'),'psql','-U','postgres','-d','patentdb','-v','ON_ERROR_STOP=1'],input=sql,text=True,capture_output=True)
 write_log('enrichment-import',{'source_docs':len(docs),'legal_docs':len(legaldocs),'returncode':result.returncode,'database_error':result.stderr if result.returncode else None,'repair':'missing outer legal-status-documents closing tag appended in memory'})
 if result.returncode:
  print(result.stdout[-3000:]);print(result.stderr[-3000:],file=sys.stderr);sys.exit(result.returncode)
 print('Supplemental official-source transaction committed')
 print('Prepared supplementary source rows:',len(verification_queries))
