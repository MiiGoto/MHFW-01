from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/'tools'
spec=[('beremiz.zip',T/'beremiz',None),('beremiz151.zip',T/'beremiz151',('matiec/','revisions.txt','license.txt')),('beremiz-1.5.1-source.zip',T,None)]
for filename,destination,prefix in spec:
    with zipfile.ZipFile(T/filename) as z:
        for item in z.infolist():
            if prefix is not None and not item.filename.startswith(prefix): continue
            target=destination/item.filename
            if not target.resolve().is_relative_to(destination.resolve()): raise ValueError('Archive traversal')
            if target.exists() and (item.is_dir() or target.stat().st_size==item.file_size): continue
            z.extract(item,destination)
records=[]
for filename,_,_ in spec:
    p=T/filename
    with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
    records.append(dict(file=filename,bytes=p.stat().st_size,sha256=digest))
(ROOT/'docs/toolchain_hashes.json').write_text(json.dumps(records,indent=2))
print('Toolchain extracted; hashes recorded')
