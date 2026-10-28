"""Small, offline slide renderer: editable DrawingML, SVG/HTML, and Cairo PDF.

Uses system Cairo/fontconfig and the already installed Pillow. No network calls.
Coordinates are in a 1600 x 900 design canvas; PowerPoint uses 16 x 9 inches.
"""
from __future__ import annotations

import ctypes as C
import ctypes.util
import html
import json
import math
import os
from pathlib import Path
import zipfile
from xml.sax.saxutils import escape

W, H = 1600, 900
ROOT = Path(__file__).resolve().parent
FONT = "Microsoft YaHei"
PALETTE = {
    'bg': '#F5F3EC', 'ink': '#173331', 'muted': '#647874',
    'teal': '#127C72', 'mint': '#D9EBE2', 'orange': '#E76A3B',
    'sand': '#F4DEBF', 'red': '#B84F49', 'rose': '#F5DFD7',
    'white': '#FFFFFF', 'line': '#D6DED6', 'navy': '#102F32',
    'blue': '#3C7398', 'ice': '#E0EAF1', 'darkcard': '#1D4244',
    'lightmuted': '#ABC8BE', 'yellow': '#F1C887',
}


def color(v):
    return PALETTE.get(v, v)


def setup_fonts():
    fc = C.CDLL(ctypes.util.find_library('fontconfig'))
    fc.FcConfigGetCurrent.restype = C.c_void_p
    fc.FcConfigAppFontAddFile.argtypes = [C.c_void_p, C.c_char_p]
    fc.FcConfigAppFontAddFile.restype = C.c_int
    paths = [os.environ.get('AGENTD_REPORT_FONT', ''),
             '/mnt/c/Windows/Fonts/msyh.ttc', '/mnt/c/Windows/Fonts/msyhbd.ttc']
    for p in paths:
        if p and Path(p).is_file():
            fc.FcConfigAppFontAddFile(fc.FcConfigGetCurrent(), p.encode())


setup_fonts()
ca = C.CDLL(ctypes.util.find_library('cairo'))
P, D, I, S = C.c_void_p, C.c_double, C.c_int, C.c_char_p
SIGNATURES = {
    'cairo_image_surface_create': ([I, I, I], P),
    'cairo_pdf_surface_create': ([S, D, D], P),
    'cairo_pdf_surface_restrict_to_version': ([P, I], None),
    'cairo_pdf_surface_set_metadata': ([P, I, S], None),
    'cairo_create': ([P], P), 'cairo_destroy': ([P], None),
    'cairo_surface_destroy': ([P], None), 'cairo_surface_finish': ([P], None),
    'cairo_surface_status': ([P], I),
    'cairo_surface_write_to_png': ([P, S], I),
    'cairo_set_source_rgb': ([P, D, D, D], None),
    'cairo_select_font_face': ([P, S, I, I], None),
    'cairo_set_font_size': ([P, D], None),
    'cairo_move_to': ([P, D, D], None), 'cairo_line_to': ([P, D, D], None),
    'cairo_rectangle': ([P, D, D, D, D], None),
    'cairo_arc': ([P, D, D, D, D, D], None),
    'cairo_close_path': ([P], None), 'cairo_new_path': ([P], None),
    'cairo_fill': ([P], None), 'cairo_fill_preserve': ([P], None),
    'cairo_stroke': ([P], None), 'cairo_paint': ([P], None),
    'cairo_set_line_width': ([P, D], None), 'cairo_set_line_cap': ([P, I], None),
    'cairo_set_dash': ([P, C.POINTER(D), I, D], None),
    'cairo_show_text': ([P, S], None),
    'cairo_scale': ([P, D, D], None), 'cairo_show_page': ([P], None),
}
for name, (args, restype) in SIGNATURES.items():
    fn = getattr(ca, name)
    fn.argtypes, fn.restype = args, restype


class Extents(C.Structure):
    _fields_ = [(n, D) for n in ['x_bearing', 'y_bearing', 'width', 'height', 'x_advance', 'y_advance']]


ca.cairo_text_extents.argtypes = [P, S, C.POINTER(Extents)]
_ms = ca.cairo_image_surface_create(0, 1, 1)
_mc = ca.cairo_create(_ms)


def measure(text, size, bold=False):
    ca.cairo_select_font_face(_mc, FONT.encode(), 0, int(bold))
    ca.cairo_set_font_size(_mc, size)
    e = Extents()
    ca.cairo_text_extents(_mc, text.encode(), C.byref(e))
    return e.x_advance


def wrap(text, size, width, bold=False):
    lines = []
    for paragraph in str(text).split('\n'):
        if not paragraph:
            lines.append('')
            continue
        line = ''
        for ch in paragraph:
            if line and measure(line + ch, size, bold) > width:
                # Keep short Latin words together where there is room.
                cut = line.rfind(' ')
                if ch.isascii() and ch.isalnum() and cut > len(line) - 18 and cut > 0:
                    lines.append(line[:cut].rstrip())
                    line = line[cut + 1:] + ch
                else:
                    lines.append(line.rstrip())
                    line = ch.lstrip()
            else:
                line += ch
        lines.append(line.rstrip())
    return lines


class Slide:
    def __init__(self, title, section, subtitle='', status='D · 候选设计', dark=False, sources=(), notes=''):
        self.title, self.section, self.subtitle = title, section, subtitle
        self.status, self.dark, self.sources, self.notes = status, dark, list(sources), notes
        self.elements = []
        self.ink = 'white' if dark else 'ink'
        self.muted = 'lightmuted' if dark else 'muted'
        self.cardfill = 'darkcard' if dark else 'white'
        self.rect(0, 0, W, H, 'navy' if dark else 'bg')

    def rect(self, x, y, w, h, fill='white', stroke=None, radius=0, lw=1.5):
        self.elements.append(dict(kind='rect', x=x, y=y, w=w, h=h, fill=color(fill) if fill else None,
                                  stroke=color(stroke) if stroke else None, radius=radius, lw=lw))

    def circle(self, x, y, r, fill='teal', stroke=None, lw=1.5):
        self.elements.append(dict(kind='circle', x=x, y=y, r=r, fill=color(fill) if fill else None,
                                  stroke=color(stroke) if stroke else None, lw=lw))

    def poly(self, points, fill='teal'):
        self.elements.append(dict(kind='poly', points=points, fill=color(fill)))

    def line(self, x1, y1, x2, y2, stroke='line', lw=2, dash=False, arrow=False):
        self.elements.append(dict(kind='line', x1=x1, y1=y1, x2=x2, y2=y2, stroke=color(stroke), lw=lw, dash=dash))
        if arrow:
            a = math.atan2(y2 - y1, x2 - x1)
            q = 12
            self.poly([(x2, y2), (x2-q*math.cos(a-.45), y2-q*math.sin(a-.45)),
                       (x2-q*math.cos(a+.45), y2-q*math.sin(a+.45))], stroke)

    def text(self, x, y, text, size=28, fill=None, bold=False, width=None, line_height=1.38, align='left'):
        fill = color(fill or self.ink)
        lines = wrap(text, size, width, bold) if width else str(text).split('\n')
        for i, line in enumerate(lines):
            if not line:
                continue
            mw = measure(line, size, bold)
            xx = x if align == 'left' else (x - mw/2 if align == 'center' else x - mw)
            self.elements.append(dict(kind='text', x=xx, y=y + i*size*line_height,
                                      text=line, size=size, fill=fill, bold=bold, measured=mw))
        return len(lines)*size*line_height

    def chip(self, x, y, label, fill='mint', textfill='teal', size=18, pad=16):
        w = measure(label, size, True) + 2*pad
        self.rect(x, y, w, 35, fill, radius=17)
        self.text(x+pad, y+5, label, size, textfill, True)
        return w

    def card(self, x, y, w, h, title, body='', tag=None, accent='teal', body_size=27, title_size=31):
        self.rect(x, y, w, h, self.cardfill, radius=18)
        self.rect(x, y+23, 5, 37, accent, radius=2)
        self.text(x+25, y+24, title, title_size, bold=True, width=w-50)
        if body:
            self.text(x+25, y+87, body, body_size, self.muted, width=w-50, line_height=1.46)
        if tag:
            self.chip(x+25, y+h-52, tag, 'mint' if not self.dark else 'navy',
                      'teal' if not self.dark else 'lightmuted', 17)

    def banner(self, text, y=746, fill='mint', textfill='teal', size=27):
        self.rect(80, y, 1440, 62, fill, radius=12)
        self.text(104, y+14, text, size, textfill, True, width=1392)

    def chrome(self, number, total):
        self.text(80, 40, f'AGENTD  /  {self.section}', 18, 'lightmuted' if self.dark else 'teal', True)
        if number != 1:
            self.text(80, 91, self.title, 48, bold=True, width=1430, line_height=1.15)
            if self.subtitle:
                self.text(82, 166, self.subtitle, 25, self.muted, width=1420)
        if self.status:
            sw = measure(self.status, 16, True)+24
            self.rect(1520-sw, 35, sw, 33, 'darkcard' if self.dark else 'white', radius=8)
            self.text(1532-sw, 40, self.status, 16, 'lightmuted' if self.dark else 'muted', True)
        self.line(80, 837, 1520, 837, 'darkcard' if self.dark else 'line', 1)
        source = '依据：' + '；'.join(s['short'] for s in self.sources[:3])
        if len(self.sources)>3:
            source += f' 等 {len(self.sources)} 份，详见备注'
        self.text(80, 852, source, 14, self.muted, width=1310)
        self.text(1520, 849, f'{number:02d} / {total:02d}', 19, self.muted, True, align='right')


def rgb(hexval):
    return tuple(int(hexval.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))


def paint(cr, c):
    ca.cairo_set_source_rgb(cr, *rgb(c))


def rounded(cr, x, y, w, h, r):
    if not r:
        ca.cairo_rectangle(cr, x, y, w, h)
        return
    ca.cairo_new_path(cr)
    for xx, yy, a, b in [(x+w-r,y+r,-math.pi/2,0),(x+w-r,y+h-r,0,math.pi/2),
                          (x+r,y+h-r,math.pi/2,math.pi),(x+r,y+r,math.pi,math.pi*1.5)]:
        ca.cairo_arc(cr,xx,yy,r,a,b)
    ca.cairo_close_path(cr)


def draw_cairo(cr, slide):
    for e in slide.elements:
        k = e['kind']
        ca.cairo_new_path(cr)
        if k == 'text':
            paint(cr,e['fill'])
            ca.cairo_select_font_face(cr,FONT.encode(),0,int(e['bold']))
            ca.cairo_set_font_size(cr,e['size'])
            ca.cairo_move_to(cr,e['x'],e['y']+e['size'])
            ca.cairo_show_text(cr,e['text'].encode())
        elif k == 'line':
            paint(cr,e['stroke']);ca.cairo_set_line_width(cr,e['lw'])
            ca.cairo_set_dash(cr,(D*2)(8,6) if e['dash'] else None,2 if e['dash'] else 0,0)
            ca.cairo_move_to(cr,e['x1'],e['y1']);ca.cairo_line_to(cr,e['x2'],e['y2']);ca.cairo_stroke(cr)
            ca.cairo_set_dash(cr,None,0,0)
        elif k == 'poly':
            paint(cr,e['fill'])
            for i,(x,y) in enumerate(e['points']):
                (ca.cairo_move_to if i==0 else ca.cairo_line_to)(cr,x,y)
            ca.cairo_close_path(cr);ca.cairo_fill(cr)
        else:
            if k=='rect':
                rounded(cr,e['x'],e['y'],e['w'],e['h'],e['radius'])
            elif k=='circle':
                ca.cairo_arc(cr,e['x'],e['y'],e['r'],0,2*math.pi)
            if e.get('fill'):
                paint(cr,e['fill']);ca.cairo_fill_preserve(cr)
            if e.get('stroke'):
                paint(cr,e['stroke']);ca.cairo_set_line_width(cr,e['lw']);ca.cairo_stroke(cr)
            else:
                ca.cairo_new_path(cr)


def export_pdf(slides,path):
    surface=ca.cairo_pdf_surface_create(str(path).encode(),1152,648)
    ca.cairo_pdf_surface_restrict_to_version(surface,0)  # PDF 1.4; portable and inspectable.
    ca.cairo_pdf_surface_set_metadata(surface,0,'agentd · 需求与架构报告'.encode())
    ca.cairo_pdf_surface_set_metadata(surface,2,'项目设计快照 2026-10-28；36 页；含需求、架构与设计取舍'.encode())
    cr=ca.cairo_create(surface)
    ca.cairo_scale(cr,.72,.72)
    for slide in slides:
        draw_cairo(cr,slide);ca.cairo_show_page(cr)
    ca.cairo_destroy(cr);ca.cairo_surface_finish(surface)
    assert ca.cairo_surface_status(surface)==0,'PDF render error'
    ca.cairo_surface_destroy(surface)


def export_png(slide,path,scale=1):
    surface=ca.cairo_image_surface_create(0,int(W*scale),int(H*scale))
    cr=ca.cairo_create(surface);ca.cairo_scale(cr,scale,scale)
    draw_cairo(cr,slide)
    assert ca.cairo_surface_write_to_png(surface,str(path).encode())==0
    ca.cairo_destroy(cr);ca.cairo_surface_destroy(surface)


def svg(slide):
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(slide.title,quote=True)}">']
    for e in slide.elements:
        k=e['kind']
        if k=='text':
            out.append(f'<text x="{e["x"]:.2f}" y="{e["y"]+e["size"]:.2f}" fill="{e["fill"]}" font-family="Microsoft YaHei, PingFang SC, Noto Sans CJK SC, sans-serif" font-size="{e["size"]}" font-weight="{700 if e["bold"] else 400}">{html.escape(e["text"])}</text>')
        elif k=='line':
            out.append(f'<line x1="{e["x1"]}" y1="{e["y1"]}" x2="{e["x2"]}" y2="{e["y2"]}" stroke="{e["stroke"]}" stroke-width="{e["lw"]}"'+(' stroke-dasharray="8 6"' if e['dash'] else '')+'/>')
        elif k=='poly':
            out.append(f'<polygon points="'+ ' '.join(f'{x:.2f},{y:.2f}' for x,y in e['points'])+f'" fill="{e["fill"]}"/>')
        else:
            common=f'fill="{e.get("fill") or "none"}" stroke="{e.get("stroke") or "none"}" stroke-width="{e["lw"]}"'
            if k=='rect':
                out.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" rx="{e["radius"]}" {common}/>')
            else:
                out.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="{e["r"]}" {common}/>')
    out.append('</svg>')
    return ''.join(out)


NS='xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
HEAD='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
EMU=9144


def fillxml(c):
    return f'<a:solidFill><a:srgbClr val="{c.lstrip(chr(35))}"/></a:solidFill>' if c else '<a:noFill/>'


def xfrm(x,y,w,h,flipx=False,flipy=False):
    return f'<a:xfrm'+(' flipH="1"' if flipx else '')+(' flipV="1"' if flipy else '')+f'><a:off x="{round(x*EMU)}" y="{round(y*EMU)}"/><a:ext cx="{max(1,round(w*EMU))}" cy="{max(1,round(h*EMU))}"/></a:xfrm>'


def shape_xml(e, i):
    k=e['kind']; name=f'{k} {i}'
    nv=f'<p:nvSpPr><p:cNvPr id="{i}" name="{name}"/><p:cNvSpPr'+(' txBox="1"' if k=='text' else '')+'/><p:nvPr/></p:nvSpPr>'
    tx=''
    if k=='text':
        fs=round(e['size']*.72*100)
        tr=xfrm(e['x'],e['y']+2,max(e['measured']+12,20),e['size']*1.55)
        geo='<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        style='<a:noFill/><a:ln><a:noFill/></a:ln>'
        rpr=f'<a:rPr lang="zh-CN" sz="{fs}" b="{int(e["bold"])}" dirty="0">{fillxml(e["fill"])}<a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="Arial"/></a:rPr>'
        tx=f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr marL="0" marR="0"><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft></a:pPr><a:r>{rpr}<a:t xml:space="preserve">{escape(e["text"])}</a:t></a:r><a:endParaRPr lang="zh-CN" sz="{fs}"/></a:p></p:txBody>'
    elif k=='line':
        x1,y1,x2,y2=e['x1'],e['y1'],e['x2'],e['y2']
        tr=xfrm(min(x1,x2),min(y1,y2),abs(x2-x1),abs(y2-y1),x2<x1,y2<y1)
        geo='<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
        style=f'<a:noFill/><a:ln w="{round(e["lw"]*EMU)}">{fillxml(e["stroke"])}'+('<a:prstDash val="dash"/>' if e['dash'] else '')+'</a:ln>'
    elif k=='poly':
        xs=[p[0] for p in e['points']];ys=[p[1] for p in e['points']]
        x,y,w,h=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
        tr=xfrm(x,y,max(w,.1),max(h,.1))
        points=[(round((px-x)*EMU),round((py-y)*EMU)) for px,py in e['points']]
        geo='<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst>'+f'<a:path w="{max(1,round(w*EMU))}" h="{max(1,round(h*EMU))}"><a:moveTo><a:pt x="{points[0][0]}" y="{points[0][1]}"/></a:moveTo>'+''.join(f'<a:lnTo><a:pt x="{px}" y="{py}"/></a:lnTo>' for px,py in points[1:])+'</a:path></a:pathLst></a:custGeom>'
        geo=geo.replace('</a:path>','<a:close/></a:path>')
        style=fillxml(e['fill'])+'<a:ln><a:noFill/></a:ln>'
    else:
        x,y,w,h=(e['x']-e['r'],e['y']-e['r'],e['r']*2,e['r']*2) if k=='circle' else (e['x'],e['y'],e['w'],e['h'])
        tr=xfrm(x,y,w,h)
        typ='ellipse' if k=='circle' else ('roundRect' if e['radius'] else 'rect')
        adj=f'<a:gd name="adj" fmla="val {round(e.get("radius",0)/min(w,h)*100000)}"/>' if typ=='roundRect' else ''
        geo=f'<a:prstGeom prst="{typ}"><a:avLst>{adj}</a:avLst></a:prstGeom>'
        style=fillxml(e['fill'])+(f'<a:ln w="{round(e["lw"]*EMU)}">{fillxml(e["stroke"])}</a:ln>' if e['stroke'] else '<a:ln><a:noFill/></a:ln>')
    return f'<p:sp>{nv}<p:spPr>{tr}{geo}{style}</p:spPr>{tx}</p:sp>'


def group_root():
    return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'


def rels(items):
    return HEAD+'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{typ}" Target="{target}"/>' for i,typ,target in items)+'</Relationships>'


def export_pptx(slides,path):
    files={}
    files['_rels/.rels']=rels([('rId1','officeDocument','ppt/presentation.xml'),('rId2','extended-properties','docProps/app.xml')])
    files['ppt/presentation.xml']=HEAD+f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rMaster"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rNotes"/></p:notesMasterIdLst><p:sldIdLst>'+''.join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1,len(slides)+1))+'</p:sldIdLst><p:sldSz cx="14630400" cy="8229600"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>'
    files['ppt/_rels/presentation.xml.rels']=rels([('rMaster','slideMaster','slideMasters/slideMaster1.xml'),('rNotes','notesMaster','notesMasters/notesMaster1.xml')]+[(f'rId{i}','slide',f'slides/slide{i}.xml') for i in range(1,len(slides)+1)])
    cmap='<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
    files['ppt/slideMasters/slideMaster1.xml']=HEAD+f'<p:sldMaster {NS}><p:cSld name="Agentd"><p:spTree>{group_root()}</p:spTree></p:cSld>{cmap}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>'
    files['ppt/slideMasters/_rels/slideMaster1.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','theme','../theme/theme1.xml')])
    files['ppt/slideLayouts/slideLayout1.xml']=HEAD+f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group_root()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
    files['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml')])
    files['ppt/notesMasters/notesMaster1.xml']=HEAD+f'<p:notesMaster {NS}><p:cSld><p:spTree>{group_root()}</p:spTree></p:cSld>{cmap}<p:notesStyle/></p:notesMaster>'
    files['ppt/notesMasters/_rels/notesMaster1.xml.rels']=rels([('rId1','theme','../theme/theme1.xml')])
    cols={'dk1':'173331','lt1':'FFFFFF','dk2':'102F32','lt2':'F5F3EC','accent1':'127C72','accent2':'E76A3B','accent3':'3C7398','accent4':'B84F49','accent5':'F1C887','accent6':'ABC8BE','hlink':'127C72','folHlink':'3C7398'}
    clr='<a:clrScheme name="Agentd">'+''.join(f'<a:{n}><a:srgbClr val="{v}"/></a:{n}>' for n,v in cols.items())+'</a:clrScheme>'
    fonts='<a:fontScheme name="Agentd">'+''.join(f'<a:{t}Font><a:latin typeface="{FONT}"/><a:ea typeface="{FONT}"/><a:cs typeface="Arial"/></a:{t}Font>' for t in ['major','minor'])+'</a:fontScheme>'
    fills='<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'*3
    fmt=f'<a:fmtScheme name="Agentd"><a:fillStyleLst>{fills}</a:fillStyleLst><a:lnStyleLst>'+('<a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:prstDash val="solid"/></a:ln>'*3)+'</a:lnStyleLst><a:effectStyleLst>'+('<a:effectStyle><a:effectLst/></a:effectStyle>'*3)+f'</a:effectStyleLst><a:bgFillStyleLst>{fills}</a:bgFillStyleLst></a:fmtScheme>'
    files['ppt/theme/theme1.xml']=HEAD+f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Agentd"><a:themeElements>{clr}{fonts}{fmt}</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
    for i,slide in enumerate(slides,1):
        files[f'ppt/slides/slide{i}.xml']=HEAD+f'<p:sld {NS}><p:cSld name="{escape(slide.title)}"><p:spTree>{group_root()}'+''.join(shape_xml(e,n) for n,e in enumerate(slide.elements,2))+'</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
        files[f'ppt/slides/_rels/slide{i}.xml.rels']=rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml'),('rId2','notesSlide',f'../notesSlides/notesSlide{i}.xml')])
        note=slide.title+'\n\n'+slide.notes+'\n\n文件依据：\n'+'\n'.join(s['path']+':'+str(s['line'])+' — '+s['short'] for s in slide.sources)
        paras=''.join('<a:p><a:r><a:rPr lang="zh-CN" sz="1400"><a:ea typeface="Microsoft YaHei"/></a:rPr><a:t xml:space="preserve">'+escape(p)+'</a:t></a:r></a:p>' for p in note.split('\n'))
        body='<p:sp><p:nvSpPr><p:cNvPr id="2" name="Speaker notes"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="685800" y="914400"/><a:ext cx="5486400" cy="6858000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr><p:txBody><a:bodyPr/><a:lstStyle/>'+paras+'</p:txBody></p:sp>'
        files[f'ppt/notesSlides/notesSlide{i}.xml']=HEAD+f'<p:notes {NS}><p:cSld><p:spTree>{group_root()}{body}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'
        files[f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels']=rels([('rId1','notesMaster','../notesMasters/notesMaster1.xml'),('rId2','slide',f'../slides/slide{i}.xml')])
    files['docProps/app.xml']=HEAD+'<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>agentd architecture report</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>'+str(len(slides))+'</Slides><Notes>'+str(len(slides))+'</Notes></Properties>'
    types={'ppt/presentation.xml':'presentation','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout','ppt/notesMasters/notesMaster1.xml':'notesMaster'}
    for i in range(1,len(slides)+1):
        types[f'ppt/slides/slide{i}.xml']='slide';types[f'ppt/notesSlides/notesSlide{i}.xml']='notesSlide'
    overrides=''.join(f'<Override PartName="/{p}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{t}+xml"/>' for p,t in types.items())
    overrides=overrides.replace('presentationml.presentation+xml','presentationml.presentation.main+xml')
    files['[Content_Types].xml']=HEAD+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>'+overrides+'<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/></Types>'
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in files.items():
            z.writestr(name,data)


def export_html(slides,path):
    data=[dict(title=s.title,section=s.section,notes=s.notes,sources=s.sources,svg=svg(s)) for s in slides]
    payload=json.dumps(data,ensure_ascii=False).replace('</',r'<\/')
    template='''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>agentd · 需求与架构报告</title><style>
    :root{color-scheme:dark;font-family:"Microsoft YaHei","PingFang SC",sans-serif}*{box-sizing:border-box}body{margin:0;background:#0b2225;color:#e5eee9}button,a{font:inherit}button{color:inherit;background:#244447;border:1px solid #42605c;border-radius:8px;padding:8px 14px;cursor:pointer}button:hover{background:#365e5c}button:disabled{opacity:.35;cursor:default}button:focus-visible,a:focus-visible{outline:3px solid #efc68e;outline-offset:3px}a{color:#a8dbca}header{height:64px;padding:0 26px;display:flex;gap:12px;align-items:center;border-bottom:1px solid #315052}.brand{font-weight:bold;letter-spacing:.08em;margin-right:auto}.hint{font-size:12px;color:#9bbab3}.layout{height:calc(100dvh - 116px);display:flex;justify-content:center;gap:18px;padding:22px 28px}.stage{display:flex;align-items:center;justify-content:center;min-width:0;flex:1}.slide{width:100%;max-width:calc((100dvh - 160px)*16/9);aspect-ratio:16/9;box-shadow:0 16px 60px #0007}.slide svg{display:block;width:100%;height:100%}aside{width:390px;flex-shrink:0;overflow:auto;background:#153539;border-radius:14px;padding:24px;font-size:15px;line-height:1.85}aside h2{font-size:20px;line-height:1.5;margin-top:0}.notes{white-space:pre-line}aside li{margin-bottom:10px;font-size:13px;overflow-wrap:anywhere}.hidden{display:none!important}footer{height:52px;display:flex;align-items:center;gap:20px;padding:0 28px;border-top:1px solid #315052;font-size:13px}.progress{height:4px;background:#34534f;flex:1;border-radius:2px}.progress i{display:block;height:100%;background:#e98b5d;transition:width .2s}.title{max-width:45%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}dialog{width:min(1400px,94vw);height:90vh;background:#102f32;color:#e5eee9;border:1px solid #43605b;border-radius:18px;padding:24px}dialog::backdrop{background:#001013cc}.gridhead{display:flex;align-items:center;gap:14px;position:sticky;top:-24px;background:#102f32;padding:16px 0;z-index:2}input{flex:1;font:inherit;border:1px solid #43605b;border-radius:8px;padding:11px;background:#082327;color:#fff}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}.thumb{padding:0;overflow:hidden;border:2px solid #43605b;text-align:left;background:#153539}.thumb.active{border-color:#e98b5d}.thumb svg{display:block;width:100%}.thumb p{margin:9px 12px;font-size:13px;line-height:1.5}.printslides{display:none}#counter{min-width:66px;text-align:center}#title{flex:0 1 auto}.mobile{display:none}
    @media(max-width:1000px){.hint,.brand span{display:none}header{padding:0 12px;gap:6px}button{padding:7px 10px}.layout{padding:10px;flex-direction:column;height:auto;min-height:calc(100dvh - 116px)}.slide{max-width:none}aside{width:100%;max-height:45vh}.stage{min-height:40vh}footer{padding:0 12px}.title{max-width:50%}}
    @media print{@page{size:16in 9in;margin:0}body{background:white}header,.layout,footer,dialog{display:none!important}.printslides{display:block}.printslides>section{width:16in;height:9in;page-break-after:always;break-after:page}.printslides>section:last-child{page-break-after:auto;break-after:auto}.printslides svg{width:100%;height:100%}}
    </style></head><body><header><div class="brand">agentd <span> / 需求与架构</span></div><span class="hint">← → 翻页 · N 备注 · G 目录 · F 全屏</span><button id="outline">目录</button><button id="notesBtn" aria-pressed="false">讲解备注</button><button id="full">全屏</button><a href="agentd-需求与架构报告.pdf">PDF</a><a href="agentd-需求与架构报告.pptx">PPTX</a></header><main class="layout"><div class="stage"><div class="slide" id="slide" aria-live="polite"></div></div><aside id="aside" class="hidden"><h2 id="noteTitle"></h2><div class="notes" id="notes"></div><h3>文件依据</h3><ul id="sources"></ul></aside></main><footer><button id="prev" aria-label="上一页">←</button><span id="counter"></span><button id="next" aria-label="下一页">→</button><span id="title" class="title"></span><div class="progress"><i id="bar"></i></div><span class="hint">01–06 快速概览 / 07–30 深入 / 31–36 附录</span></footer><dialog id="dialog"><div class="gridhead"><strong>36 页报告</strong><input id="search" type="search" placeholder="搜索页标题或章节"><button id="close">关闭</button></div><div id="grid" class="grid"></div></dialog><div class="printslides" id="print"></div><script>
    const slides=__DATA__;const $=id=>document.getElementById(id);let n=Math.min(slides.length-1,Math.max(0,(parseInt(location.hash.slice(1))||1)-1));let showNotes=false;
    function render(){const s=slides[n];$('slide').innerHTML=s.svg;$('title').textContent=s.title;$('noteTitle').textContent=String(n+1).padStart(2,'0')+' · '+s.title;$('notes').textContent=s.notes;$('sources').replaceChildren(...s.sources.map(x=>{let li=document.createElement('li'),a=document.createElement('a');a.href='../../'+x.path;a.target='_blank';a.textContent=x.short+' · '+x.path+' 第 '+x.line+' 行';li.append(a);return li}));$('counter').textContent=String(n+1).padStart(2,'0')+' / '+slides.length;$('bar').style.width=(n+1)/slides.length*100+'%';$('prev').disabled=n===0;$('next').disabled=n===slides.length-1;history.replaceState(null,'','#'+(n+1));document.title=(n+1)+' · '+s.title+' | agentd';}
    function go(v){n=Math.max(0,Math.min(slides.length-1,v));render()}
    function toggleNotes(){showNotes=!showNotes;$('aside').classList.toggle('hidden',!showNotes);$('notesBtn').setAttribute('aria-pressed',showNotes)}
    function grid(){const q=$('search').value.toLowerCase();$('grid').replaceChildren(...slides.map((s,i)=>{if(!(s.title+s.section).toLowerCase().includes(q))return null;let b=document.createElement('button');b.className='thumb'+(i===n?' active':'');b.innerHTML=s.svg;let p=document.createElement('p');p.textContent=String(i+1).padStart(2,'0')+' · '+s.title;b.append(p);b.onclick=()=>{go(i);$('dialog').close()};return b}).filter(Boolean))}
    function openGrid(){grid();$('dialog').showModal();$('search').focus()}
    function full(){if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen?.().catch(()=>{})}
    $('prev').onclick=()=>go(n-1);$('next').onclick=()=>go(n+1);$('notesBtn').onclick=toggleNotes;$('outline').onclick=openGrid;$('search').oninput=grid;$('close').onclick=()=>$('dialog').close();$('full').onclick=full;
    document.addEventListener('keydown',e=>{if(e.target.tagName==='INPUT'||$('dialog').open)return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();go(n+1)}else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(n-1)}else if(e.key==='Home'){e.preventDefault();go(0)}else if(e.key==='End'){e.preventDefault();go(slides.length-1)}else if(e.key.toLowerCase()==='n')toggleNotes();else if(e.key.toLowerCase()==='g')openGrid();else if(e.key.toLowerCase()==='f')full()});
    let touchX=0;$('slide').addEventListener('touchstart',e=>touchX=e.changedTouches[0].clientX,{passive:true});$('slide').addEventListener('touchend',e=>{let d=e.changedTouches[0].clientX-touchX;if(Math.abs(d)>60)go(n+(d<0?1:-1))},{passive:true});
    window.addEventListener('beforeprint',()=>{$('print').innerHTML=slides.map(s=>'<section>'+s.svg+'</section>').join('')});render();
    </script></body></html>'''
    path.write_text(template.replace('__DATA__',payload),encoding='utf-8')


def export_handout(slides,path):
    sections=[]
    for i,s in enumerate(slides,1):
        sources=''.join(f'<li><a href="../../{html.escape(x["path"])}">{html.escape(x["short"])}</a> · 第 {x["line"]} 行</li>' for x in s.sources)
        sections.append(f'<section id="s{i}"><h2>{i:02d} · {html.escape(s.title)}</h2><div class="visual">{svg(s)}</div><p>{html.escape(s.notes).replace(chr(10),"<br>")}</p><ul>{sources}</ul><a href="index.html#{i}">打开此页幻灯片</a></section>')
    nav=''.join(f'<li><a href="#s{i}">{i:02d} {html.escape(s.title)}</a></li>' for i,s in enumerate(slides,1))
    path.write_text('<!DOCTYPE html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>agentd 报告逐页讲解与依据</title><style>body{font-family:"Microsoft YaHei","PingFang SC",sans-serif;background:#f5f3ec;color:#173331;max-width:1050px;padding:40px 25px;margin:auto;line-height:1.9}h1,h2{line-height:1.4}h2{margin-top:60px}a{color:#127c72}p{font-size:17px}li{font-size:14px}.visual svg{width:100%;box-shadow:0 5px 30px #17333115}nav ol{columns:2}section{border-bottom:1px solid #d6ded6;padding-bottom:30px}@media print{nav{display:none}section{break-before:page}a{color:#173331}}</style><h1>agentd · 需求与架构报告</h1><p>逐页讲解与来源索引 · 2026-10-28<br>1–6 页：快速概览；7–30 页：需求、架构与取舍；31–36 页：追踪与证据。<br>这是对项目候选设计的整理，不代表新服务已经实施。情境、界面和统计算例均在对应页面标注为示意。</p><nav><ol>'+nav+'</ol></nav>'+''.join(sections)+'</html>',encoding='utf-8')


def export_all(slides):
    for i,s in enumerate(slides,1):
        s.chrome(i,len(slides))
    bounds=[]
    for i,s in enumerate(slides,1):
        for e in s.elements:
            if e['kind']=='text' and (e['x']<-1 or e['y']<0 or e['x']+e['measured']>W-10 or e['y']+e['size']>H-8):
                bounds.append({'slide':i,'text':e['text'],'x':e['x'],'y':e['y'],'width':e['measured']})
    if bounds:
        raise ValueError('Text outside canvas: '+json.dumps(bounds,ensure_ascii=False))
    export_pptx(slides,ROOT/'agentd-需求与架构报告.pptx')
    export_pdf(slides,ROOT/'agentd-需求与架构报告.pdf')
    export_html(slides,ROOT/'index.html')
    export_handout(slides,ROOT/'讲解与依据.html')
    for i,s in enumerate(slides,1):
        export_png(s,ROOT/'previews'/f'{i:02d}.png')
    (ROOT/'slide-content.json').write_text(json.dumps([dict(number=i,title=s.title,section=s.section,status=s.status,notes=s.notes,sources=s.sources,text=[e['text'] for e in s.elements if e['kind']=='text']) for i,s in enumerate(slides,1)],ensure_ascii=False,indent=2),encoding='utf-8')
    from PIL import Image, ImageDraw, ImageFont
    thumb_w,thumb_h=400,225
    for batch in range((len(slides)+11)//12):
        subset=slides[batch*12:batch*12+12]
        canvas=Image.new('RGB',(3*thumb_w,4*(thumb_h+32)), '#DEDED5')
        draw=ImageDraw.Draw(canvas)
        font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
        for j,_ in enumerate(subset):
            i=batch*12+j+1;x=(j%3)*thumb_w;y=(j//3)*(thumb_h+32)
            im=Image.open(ROOT/'previews'/f'{i:02d}.png').convert('RGB').resize((thumb_w,thumb_h),Image.Resampling.LANCZOS)
            canvas.paste(im,(x,y));draw.text((x+10,y+thumb_h+6),f'{i:02d}',font=font,fill='#173331')
        canvas.save(ROOT/'previews'/f'contact-{batch+1}.png')
    print(json.dumps({'slides':len(slides),'text_bounds_errors':len(bounds),'output_directory':str(ROOT),'outputs':['agentd-需求与架构报告.pptx','agentd-需求与架构报告.pdf','index.html','讲解与依据.html']},ensure_ascii=False))
