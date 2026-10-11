"""Generate PLCopen project from reviewable IEC Structured Text sources.
No Python controller: this only converts declarations into IDE XML."""
from pathlib import Path
import re, json, xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
NS='http://www.plcopen.org/xml/tc6_0201'; XHTML='http://www.w3.org/1999/xhtml'
E.register_namespace('',NS); E.register_namespace('xhtml',XHTML)
def sub(p,n,**a): return E.SubElement(p,'{'+NS+'}'+n,a)
def variable(parent,name,typ):
    v=sub(parent,'variable',name=name); t=sub(v,'type')
    if typ.startswith('FB_'): sub(t,'derived',name=typ)
    else: sub(t,typ)
    return v
def main():
    dst=ROOT/'plc/beremiz'; dst.mkdir(parents=True,exist_ok=True)
    p=E.Element('{'+NS+'}project')
    sub(p,'fileHeader',companyName='Independent MHFW-01',productName='MHFW-01',productVersion='Rev A',creationDateTime='2026-10-11T00:00:00')
    h=sub(p,'contentHeader',name='MHFW-01'); ci=sub(h,'coordinateInfo')
    for k in ['fbd','ld','sfc']: sub(sub(ci,k),'scaling',x='1',y='1')
    ty=sub(p,'types'); sub(ty,'dataTypes'); pous=sub(ty,'pous')
    files=sorted((ROOT/'plc/function_blocks').glob('*.st'))+sorted((ROOT/'plc/programs').glob('*.st'))
    for f in files:
        source=f.read_text(); kind,name=re.search(r'(FUNCTION_BLOCK|PROGRAM)\s+(\w+)',source).groups()
        pou=sub(pous,'pou',name=name,pouType='functionBlock' if kind=='FUNCTION_BLOCK' else 'program'); interface=sub(pou,'interface')
        for modifier,decl in re.findall(r'VAR(_INPUT|_OUTPUT|_EXTERNAL)?\s*\n(.*?)END_VAR',source,re.S):
            group=sub(interface,{'_INPUT':'inputVars','_OUTPUT':'outputVars','_EXTERNAL':'externalVars','':'localVars'}[modifier])
            for names,typ in re.findall(r'([\w, ]+)\s*:\s*(\w+)\s*;',decl):
                for n in names.split(','): variable(group,n.strip(),typ)
        body=re.sub(r'VAR(?:_INPUT|_OUTPUT|_EXTERNAL)?\s*\n.*?END_VAR','',source,flags=re.S)
        body=re.sub(r'^(FUNCTION_BLOCK|PROGRAM)\s+\w+','',body).replace('END_FUNCTION_BLOCK','').replace('END_PROGRAM','').strip()
        E.SubElement(sub(sub(pou,'body'),'ST'),'{'+XHTML+'}p').text=body
    conf=sub(sub(sub(p,'instances'),'configurations'),'configuration',name='config')
    resource=sub(conf,'resource',name='resource1'); task=sub(resource,'task',name='Scan20ms',priority='0',interval='T#20ms')
    sub(task,'pouInstance',name='machine',typeName='PRG_PackagingMachine')
    E.ElementTree(p).write(dst/'plc.xml',encoding='utf-8',xml_declaration=True)
    (dst/'beremiz.xml').write_text('<BeremizRoot URI_location="LOCAL://"><TargetType><Win32/></TargetType><Libraries Enable_Python_Library="false" Enable_SVGHMI_Library="false"/></BeremizRoot>')
    node=dst/'virtual_io@c_ext'; node.mkdir(exist_ok=True)
    (node/'baseconfnode.xml').write_text('<BaseParams Name="virtual_io" IEC_Channel="0"/>')
    (node/'confnode.xml').write_text('<CExtension CFLAGS="" LDFLAGS="-lws2_32"/>')
    mapping=json.loads((ROOT/'plc/io_mapping/signals.json').read_text())
    c=E.Element('CFile'); sections={}
    for name in ['includes','variables','globals','initFunction','cleanUpFunction','retrieveFunction','publishFunction']:
        sections[name]=E.SubElement(c,name)
    for direction in ['inputs','outputs']:
        for name in mapping[direction]: E.SubElement(sections['variables'],'variable',name=name,type='REAL',initial='0.0')
    template=(ROOT/'plc/io_mapping/adapter.c').read_text()
    parts=re.split(r'/\* SECTION (\w+) \*/',template)
    for i in range(1,len(parts),2): E.SubElement(sections[parts[i]],'{'+XHTML+'}p').text=parts[i+1]
    retrieve='\n'.join(f'{n} = frame.values[{i}];' for i,n in enumerate(mapping['inputs']))
    publish='\n'.join(f'reply.values[{i}] = {n};' for i,n in enumerate(mapping['outputs']))
    for element in c.iter():
        if element.text: element.text=element.text.replace('INPUT_ASSIGNMENTS',retrieve).replace('OUTPUT_ASSIGNMENTS',publish)
    E.ElementTree(c).write(node/'cfile.xml',encoding='utf-8',xml_declaration=True)
    print('PLCopen generated:',dst)
if __name__=='__main__': main()
