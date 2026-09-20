#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate textbook-style E/R SVG and editable draw.io pages.

Notation follows Ullman/Widom chapter 4: rectangle=entity set, double
rectangle=weak entity set, diamond=relationship, double diamond=identifying
relationship, ellipse=attribute, triangle=ISA, edge labels=cardinality/role,
and a thick edge=total participation.

Conceptual E/R objects are deliberately kept separate from relation tables
produced by conversion. Association tables do not appear as entity boxes.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import subprocess
import sys

W, H = 210, 72

def N(i, label, shape, x, y, w=W, h=H):
    return dict(id=i, label=label, shape=shape, x=x, y=y, w=w, h=h)

def E(a, b, label='', thick=False, dashed=False):
    return dict(a=a, b=b, label=label, thick=thick, dashed=dashed)

DOMAINS = [
    ('域1-著录与文献', 1500, 760, [
        N('dataset','数据集\ndataset','E',40,70), N('patent','申请案\npatent','E',350,70),
        N('publication','公布文献\npublication','E',650,70),
        N('title','标题\ntitle','W',1080,30,170), N('abstract','摘要\nabstract','W',1280,30,170),
        N('claim','权利要求\nclaim','W',1080,210,170), N('drawing','附图\ndrawing','W',1280,210,170),
        N('section','说明书章节\ndescription_section','W',1080,390,190),
        N('r_ds','提供','R',270,200,110,70), N('r_pp','形成文献','R',560,200,125,70),
        N('r_t','含标题','IR',900,15,120,80), N('r_a','含摘要','IR',900,125,120,80),
        N('r_c','含权利要求','IR',895,235,130,80), N('r_d','含附图','IR',900,345,120,80),
        N('r_s','含章节','IR',900,455,120,80), N('r_cd','从属依赖','R',1060,600,130,75),
        N('r_tree','父子','R',1300,540,105,70),
        N('a_pk','patent_id（键）','A',350,5,180,45), N('u_pk','publication_id（键）','A',650,5,190,45),
        N('a_title','lang+type（部分键）','P',1070,115,190,45), N('a_claim','lang+number（部分键）','P',1060,300,210,45),
        N('a_sec','section_seq（部分键）','P',1280,475,200,45),
    ], [
        E('dataset','r_ds','1'),E('r_ds','patent','N'),E('patent','r_pp','1'),E('r_pp','publication','N',True),
        E('publication','r_t','1'),E('r_t','title','N',True),E('publication','r_a','1'),E('r_a','abstract','N',True),
        E('publication','r_c','1'),E('r_c','claim','N',True),E('publication','r_d','1'),E('r_d','drawing','N',True),
        E('publication','r_s','1'),E('r_s','section','N',True),E('claim','r_cd','从属角色 M'),E('r_cd','claim','被依赖角色 N'),
        E('section','r_tree','父 1'),E('r_tree','section','子 N'),
        E('a_pk','patent'),E('u_pk','publication'),E('a_title','title'),E('a_claim','claim'),E('a_sec','section'),
    ]),
    ('域2-人员与角色', 1540, 760, [
        N('person','当事人\nperson','E',80,100), N('isa','ISA（全覆盖、互斥）','I',330,95,170,105),
        N('natural','自然人\nnatural_person','E',570,25), N('org','机构\norganization','E',570,180),
        N('patent','申请案\npatent','E',80,500),
        N('r_app','申请人','R',420,380,120,75), N('r_inv','发明人','R',650,380,120,75),
        N('r_asg','权利人','R',880,380,120,75), N('r_agt','代理人','R',1110,380,120,75),
        N('r_exam','审查员','R',1300,380,120,75),
        N('a_person','person_id（键）','A',55,25,190,45),
        N('a_app','sequence/type（联系属性）','A',385,285,190,45),
        N('a_inv','sequence（联系属性）','A',625,285,170,45),
        N('a_asg','sequence/role（联系属性）','A',845,285,190,45),
        N('a_agt','sequence/rep_type（联系属性）','A',1070,285,210,45),
        N('a_exam','type/department（联系属性）','A',1300,285,210,45),
    ], [
        E('person','isa'),E('isa','natural'),E('isa','org'),
        E('patent','r_app','M'),E('person','r_app','N'),E('patent','r_inv','M'),E('person','r_inv','N'),
        E('patent','r_asg','M'),E('person','r_asg','N'),E('patent','r_agt','M'),E('person','r_agt','N'),
        E('patent','r_exam','M'),E('person','r_exam','N'),
        E('a_person','person'),E('a_app','r_app'),E('a_inv','r_inv'),E('a_asg','r_asg'),E('a_agt','r_agt'),E('a_exam','r_exam'),
    ]),
    ('域3-分类', 1300, 620, [
        N('scheme','分类体系\nclassification_scheme','E',60,80),
        N('classification','分类号\nclassification','E',520,80), N('patent','申请案\npatent','E',60,390),
        N('r_sc','定义','R',335,80,115,75), N('r_pc','赋予分类','R',370,300,140,80),
        N('tech','IPC技术领域\nipc_techn_field（增强）','E',900,80,230), N('r_tech','映射','R',810,260,115,75),
        N('a_ck','scheme+symbol（键）','A',500,5,230,45),
        N('a_role','position/value/source_type\n（联系属性）','A',550,300,250,58),
    ], [
        E('scheme','r_sc','1'),E('r_sc','classification','N',True),
        E('patent','r_pc','M'),E('r_pc','classification','N'),E('a_role','r_pc'),
        E('tech','r_tech','1'),E('r_tech','classification','N',False,True),E('a_ck','classification'),
    ]),
    ('域4-引用', 1450, 760, [
        N('publication','公布文献\npublication','E',60,70), N('occ','引用出现\ncitation occurrence','W',480,70,220),
        N('r_has','含引用','IR',320,65,120,80), N('pat1','申请案（引用方角色）\npatent','E',60,430,230),
        N('pat2','申请案（被引方角色）\n同一 patent 实体集','E',540,430,250), N('r_cites','引用（递归）','R',350,430,145,80),
        N('npl','非专利文献\nnon_patent_citation','E',930,70,230), N('r_npl','对应NPL','R',760,70,130,80),
        N('cat','引用类别\ncitation_category','E',930,300,220), N('r_cat','标注类别','R',750,300,130,80),
        N('a_occ','type+seq（部分键）','P',485,5,220,45), N('a_cit','origin/raw/date（联系属性）','A',320,535,230,50),
        N('note','库外被引文献：保留国别/号/种类/日期原文\n不强制 cited_patent_id 非空','NOTE',870,520,470,85),
    ], [
        E('publication','r_has','1'),E('r_has','occ','N',True),E('occ','r_npl','0..1'),E('r_npl','npl','1'),
        E('occ','r_cat','M'),E('r_cat','cat','N'),E('pat1','r_cites','引用方 M'),E('r_cites','pat2','被引方 N'),
        E('a_occ','occ'),E('a_cit','r_cites'),E('occ','r_cites','解析后',False,True),
    ]),
    ('域5-专利族与程序关系', 1600, 900, [
        N('family','专利族\npatent_family','E',40,70), N('member','族成员\npatent_family_member','W',405,70,230),
        N('r_mem','含成员','IR',270,65,115,80), N('appref','成员申请号引用\nfamily_member_application_ref','W',760,20,280),
        N('pubref','成员公布号引用\nfamily_member_publication_ref','W',760,150,280),
        N('r_ar','含申请号','IR',650,20,110,80), N('r_pr','含公布号','IR',650,150,110,80),
        N('fabs','族摘要\nfamily_abstract','W',390,240,220), N('r_fa','含族摘要','IR',235,240,130,80),
        N('patent','申请案\npatent','E',60,560), N('r_res','解析为本地申请','R',360,430,170,80),
        N('p2','申请案（在先/关联角色）\n同一 patent 实体集','E',730,560,270),
        N('r_prior','优先权（递归）','R',350,570,160,80), N('r_related','程序关联（递归）','R',520,690,170,80),
        N('office','国家/受理局\ncountry_office','E',1110,560,220), N('r_desig','指定国','R',900,700,130,80),
        N('fam2','专利族（被引角色）\n同一 family 实体集','E',1110,70,250), N('r_fcit','族引用（递归）','R',850,360,170,80),
        N('a_mem','member_seq（部分键）','P',405,5,220,45), N('a_ref','data_format+号码（部分键）','P',1080,235,250,48),
    ], [
        E('family','r_mem','1'),E('r_mem','member','N',True),E('member','r_ar','1'),E('r_ar','appref','N',True),
        E('member','r_pr','1'),E('r_pr','pubref','N',True),E('family','r_fa','1'),E('r_fa','fabs','N',True),
        E('member','r_res','N'),E('r_res','patent','0..1',False,True),E('patent','r_prior','在后 M'),E('r_prior','p2','在先 N'),
        E('patent','r_related','主案 M'),E('r_related','p2','关联案 N'),E('patent','r_desig','M'),E('r_desig','office','N'),
        E('family','r_fcit','引用方 M'),E('r_fcit','fam2','被引方 N'),E('a_mem','member'),E('a_ref','appref'),E('a_ref','pubref'),
    ]),
    ('域6-法律状态与关键词', 1350, 680, [
        N('patent','申请案\npatent','E',60,100), N('event','法律状态事件\nlegal_status_event','W',480,80,240),
        N('r_ev','发生事件','IR',320,85,125,80), N('code','法律事件码\nlegal_event_code','E',900,80,230),
        N('r_code','采用事件码','R',760,85,130,80), N('keyword','关键词\nkeyword','E',900,400,210),
        N('r_kw','具有关键词','R',460,390,150,80), N('a_ev','event_seq（部分键）','P',485,5,220,45),
        N('a_kw','weight/source（联系属性）','A',440,500,200,45),
    ], [
        E('patent','r_ev','1'),E('r_ev','event','N',True),E('event','r_code','N'),E('r_code','code','1'),
        E('patent','r_kw','M'),E('r_kw','keyword','N'),E('a_ev','event'),E('a_kw','r_kw'),
    ]),
]

COLORS={'E':'#dbeafe','W':'#dbeafe','R':'#fee2e2','IR':'#fee2e2','I':'#ffedd5','A':'#fef9c3','P':'#fef9c3','NOTE':'#f3f4f6'}
def center(n): return n['x']+n['w']/2,n['y']+n['h']/2

def validate_no_node_overlap(title, nodes):
    """Fail generation when two E/R nodes would cover each other."""
    overlaps = []
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            overlap_x = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
            overlap_y = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
            if overlap_x > 0 and overlap_y > 0:
                overlaps.append(f"{a['id']}↔{b['id']}")
    if overlaps:
        raise ValueError(f'{title} 存在节点重叠：{", ".join(overlaps)}')

def svg_node(n):
    x,y,w,h=n['x'],n['y'],n['w'],n['h']; s=n['shape']; fill=COLORS[s]; out=[]
    if s in ('E','W','NOTE'):
        dash=' stroke-dasharray="7 5"' if s=='NOTE' else ''
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#334155" stroke-width="2"{dash}/>')
        if s=='W': out.append(f'<rect x="{x+6}" y="{y+6}" width="{w-12}" height="{h-12}" fill="none" stroke="#334155" stroke-width="2"/>')
    elif s in ('R','IR'):
        pts=f'{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}'
        out.append(f'<polygon points="{pts}" fill="{fill}" stroke="#991b1b" stroke-width="2"/>')
        if s=='IR':
            pts2=f'{x+w/2},{y+6} {x+w-8},{y+h/2} {x+w/2},{y+h-6} {x+8},{y+h/2}'
            out.append(f'<polygon points="{pts2}" fill="none" stroke="#991b1b" stroke-width="2"/>')
    elif s=='I': out.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h} {x},{y+h}" fill="{fill}" stroke="#9a3412" stroke-width="2"/>')
    else: out.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="#854d0e" stroke-width="2"/>')
    lines=n['label'].split('\n'); base=y+h/2-(len(lines)-1)*10
    for i,line in enumerate(lines):
        deco=' text-decoration="underline"' if '（键）' in line else ''
        out.append(f'<text x="{x+w/2}" y="{base+i*21}" text-anchor="middle" dominant-baseline="middle" font-size="15"{deco}>{escape(line)}</text>')
    return ''.join(out)

def svg_edge(e,byid):
    x1,y1=center(byid[e['a']]); x2,y2=center(byid[e['b']])
    style='stroke:#475569;fill:none;'+('stroke-width:4;' if e['thick'] else 'stroke-width:2;')+('stroke-dasharray:8 6;' if e['dashed'] else '')
    out=[f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="{style}"/>']
    if e['label']:
        mx,my=(x1+x2)/2,(y1+y2)/2
        out += [f'<rect x="{mx-42}" y="{my-12}" width="84" height="23" fill="white" fill-opacity="0.86"/>',
                f'<text x="{mx}" y="{my}" text-anchor="middle" dominant-baseline="middle" font-size="13">{escape(e["label"])}</text>']
    return ''.join(out)

def svg_page(title,w,h,nodes,edges):
    byid={n['id']:n for n in nodes}; body=''.join(svg_edge(e,byid) for e in edges)+''.join(svg_node(n) for n in nodes)
    legend='矩形=实体集　双矩形=弱实体集　菱形=联系　双菱形=支持联系　椭圆=属性　三角形=ISA　粗线=全部参与'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="white"/><style>text{{font-family:"Noto Sans CJK SC","Microsoft YaHei",sans-serif;fill:#0f172a}}</style><text x="28" y="30" font-size="22" font-weight="700">{escape(title)}</text><text x="28" y="{h-22}" font-size="13">{legend}</text>{body}</svg>'

def drawio_page(title,w,h,nodes,edges):
    out=[f'<diagram id="{escape(title)}" name="{escape(title)}"><mxGraphModel pageWidth="{w}" pageHeight="{h}"><root><mxCell id="0"/><mxCell id="1" parent="0"/>']
    for n in nodes:
        shape=n['shape']; style='shape=rectangle;whiteSpace=wrap;html=1;'
        if shape=='W': style+='double=1;'
        elif shape in ('R','IR'): style='shape=rhombus;whiteSpace=wrap;html=1;'+('double=1;' if shape=='IR' else '')
        elif shape=='I': style='shape=triangle;direction=north;whiteSpace=wrap;html=1;'
        elif shape in ('A','P'): style='shape=ellipse;whiteSpace=wrap;html=1;'+('dashed=1;' if shape=='P' else '')
        elif shape=='NOTE': style+='dashed=1;fillColor=#f3f4f6;'
        val=escape(n['label']).replace(chr(10),'&#10;')
        out.append(f'<mxCell id="{n["id"]}" value="{val}" style="{style}" vertex="1" parent="1"><mxGeometry x="{n["x"]}" y="{n["y"]}" width="{n["w"]}" height="{n["h"]}" as="geometry"/></mxCell>')
    for i,e in enumerate(edges):
        style='endArrow=none;html=1;'+('strokeWidth=3;' if e['thick'] else '')+('dashed=1;' if e['dashed'] else '')
        out.append(f'<mxCell id="edge{i}" value="{escape(e["label"])}" style="{style}" edge="1" parent="1" source="{e["a"]}" target="{e["b"]}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return ''.join(out)+'</root></mxGraphModel></diagram>'

def main():
    out=Path(sys.argv[1] if len(sys.argv)>1 else '.'); out.mkdir(parents=True,exist_ok=True); svgs=[]; pages=[]
    for title,w,h,nodes,edges in DOMAINS:
        validate_no_node_overlap(title, nodes)
        svg=svg_page(title,w,h,nodes,edges); (out/f'ER教材-{title}.svg').write_text(svg); svgs.append((w,h,svg)); pages.append(drawio_page(title,w,h,nodes,edges))
    gap=30; tw=max(x[0] for x in svgs); th=sum(x[1] for x in svgs)+gap*(len(svgs)-1); parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" viewBox="0 0 {tw} {th}"><rect width="100%" height="100%" fill="white"/>']; y=0
    for _w,h,svg in svgs:
        parts.append(f'<g transform="translate(0,{y})">{svg[svg.index(">")+1:svg.rindex("</svg>")]}</g>'); y+=h+gap
    parts.append('</svg>'); overview=''.join(parts); (out/'ER教材-总览.svg').write_text(overview)
    (out/'ER教材-教材符号.drawio').write_text('<?xml version="1.0" encoding="UTF-8"?><mxfile host="app.diagrams.net" version="24.0.0">'+''.join(pages)+'</mxfile>')
    subprocess.run(['rsvg-convert',str(out/'ER教材-总览.svg'),'-o',str(out/'ER教材-总览.png')],check=True)
    print(f'wrote {len(svgs)} domain SVGs, overview SVG/PNG and drawio')

if __name__=='__main__': main()
