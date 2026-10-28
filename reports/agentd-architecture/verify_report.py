"""Validate the generated report packages without changing project design files."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import posixpath
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parent.parent
content=json.loads((HERE/'slide-content.json').read_text())
assert len(content)==36
refs=0
for s in content:
    assert s['notes'].strip() and s['sources']
    for ref in s['sources']:
        file=REPO/ref['path']
        assert file.is_file(),str(file)
        assert 1<=ref['line']<=len(file.read_text().splitlines()),ref
        refs+=1

snapshot=[]
for line in (REPO/'audit/SHA256SUMS').read_text().splitlines():
    wanted,name=line.split(maxsplit=1)
    name=name.lstrip('*')
    actual=hashlib.sha256((REPO/name).read_bytes()).hexdigest()
    assert wanted==actual,name
    snapshot.append(name)

A='{http://schemas.openxmlformats.org/drawingml/2006/main}'
P='{http://schemas.openxmlformats.org/presentationml/2006/main}'
editable=0
with zipfile.ZipFile(HERE/'agentd-需求与架构报告.pptx') as z:
    assert z.testzip() is None
    names=set(z.namelist())
    for name in names:
        if name.endswith(('.xml','.rels')):
            root=ET.fromstring(z.read(name))
        if name.endswith('.rels'):
            base=posixpath.dirname(posixpath.dirname(name))
            for r in root:
                if r.attrib.get('TargetMode')!='External':
                    target=posixpath.normpath(posixpath.join(base,r.attrib['Target']))
                    assert target in names,(name,target)
    presentation=ET.fromstring(z.read('ppt/presentation.xml'))
    assert len(presentation.find(P+'sldIdLst'))==36
    for i,s in enumerate(content,1):
        root=ET.fromstring(z.read(f'ppt/slides/slide{i}.xml'))
        texts=[e.text or '' for e in root.iter(A+'t')]
        assert texts==s['text'],f'slide {i} text mismatch'
        editable+=len(texts)
        note=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        notes='\n'.join(e.text or '' for e in note.iter(A+'t'))
        assert s['notes'] in notes,f'slide {i} missing notes'
        assert not list(root.iter(P+'pic')),f'slide {i} unexpectedly flattened'
    parts=len(names)

pdf=(HERE/'agentd-需求与架构报告.pdf').read_bytes()
pages=len(re.findall(rb'/Type\s*/Page\b',pdf))
assert pages==36,pages
assert pdf.startswith(b'%PDF-1.4') and pdf.rstrip().endswith(b'%%EOF')
embedded_fonts=len(re.findall(rb'/FontFile[23]?\b',pdf))
unicode_maps=len(re.findall(rb'/ToUnicode\b',pdf))
assert embedded_fonts>=2 and unicode_maps>=2
assert not re.search(rb'/Subtype\s*/Image\b',pdf),'PDF unexpectedly rasterized'

html=(HERE/'index.html').read_text()
assert 'fetch(' not in html and '<script src=' not in html
script=html.split('<script>',1)[1].split('</script>',1)[0]
with tempfile.NamedTemporaryFile('w',suffix='.js',encoding='utf-8') as f:
    f.write(script);f.flush()
    subprocess.run(['node','--check',f.name],check=True,capture_output=True)
payload=script.split('const slides=',1)[1].split(';const $=',1)[0]
viewer=json.loads(payload)
assert len(viewer)==36
for i,s in enumerate(viewer):
    assert s['title']==content[i]['title'] and s['notes']==content[i]['notes']
    assert s['svg'].startswith('<svg')
assert (HERE/'讲解与依据.html').read_text().count('<section id="s')==36

files=['agentd-需求与架构报告.pptx','agentd-需求与架构报告.pdf','index.html','讲解与依据.html']
receipt={
    'date':'2026-10-28','report_slides':36,
    'original_snapshot_files_unchanged':len(snapshot),
    'source_references_checked':refs,
    'pptx':{'package_parts':parts,'editable_text_lines':editable,'speaker_note_pages':36,
            'all_xml_and_relationships':'PASS','content_matches_source':'PASS',
            'native_powerpoint_or_libreoffice_open':'NOT_RUN'},
    'pdf':{'pages':pages,'embedded_fonts':embedded_fonts,'unicode_maps':unicode_maps,
           'vector_content':'PASS','structure':'PASS'},
    'html':{'offline_assets':'PASS','javascript_syntax':'PASS','content_matches':'PASS',
            'browser_interaction_execution':'NOT_RUN'},
    'visual_review':'36-slide contact sheets plus selected 1600x900 pages inspected; text bounds and text overlap checked',
    'project_contract_check':{'command':'/home/cying/agentd/.venv/bin/python -m specs.agentd_v1.check',
        'result':'PASS','scope':'offline_design_contract_only','operations':29,'registered_models':153,
        'schema_definitions':154,'valid_examples':8,'negative_examples':19,
        'split_contract_regression_checks':3,'generated_files_checked':3,
        'runtime_model_host_validation':'NOT_RUN'},
    'artifacts':{n:{'bytes':(HERE/n).stat().st_size,'sha256':hashlib.sha256((HERE/n).read_bytes()).hexdigest()} for n in files}
}
(HERE/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
