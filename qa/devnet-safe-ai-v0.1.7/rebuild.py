#!/usr/bin/env python3
"""Deterministically rebuild the exact v0.1.7 QA archive from immutable v0.1.6."""
import base64,hashlib,json,pathlib,subprocess,sys,zipfile,zlib
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
old=root/'qa/devnet-safe-ai-v0.1.6/candidate.zip'
subprocess.run([sys.executable,str(root/'qa/devnet-safe-ai-v0.1.6/rebuild.py'),str(root)],check=True)
assert hashlib.sha256(old.read_bytes()).hexdigest()=='5dda7c3355d754efe07f2d44a89ff65d9843d32fffc71e0bfdb80923bec69a25'
blob=(root/'qa/devnet-safe-ai-v0.1.7/patches-v017.zlib.b64').read_text().strip()
patch=json.loads(zlib.decompress(base64.b64decode(blob)))
out=root/'qa/devnet-safe-ai-v0.1.7/generated'
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(old) as z:
    assert z.testzip() is None
    for original,new in [('devnet-safe-ai-v0.1.6.py','devnet-safe-ai-v0.1.7.py'),('test_devnet_safe_ai_v0.1.6.py','test_devnet_safe_ai_v0.1.7.py')]:
        lines=z.read(original).decode().splitlines(keepends=True)
        for tag,lo,hi,replacement in reversed(patch[original]):
            assert tag in ('replace','insert','delete')
            lines[lo:hi]=replacement.splitlines(keepends=True)
        (out/new).write_text(''.join(lines))
    (out/'v0.1.2-baseline-permissions.json').write_bytes(z.read('v0.1.2-baseline-permissions.json'))
(out/'DEVNET-SAFE-AI-v0.1.7-README.md').write_text(patch['README'])
files=['devnet-safe-ai-v0.1.7.py','test_devnet_safe_ai_v0.1.7.py','v0.1.2-baseline-permissions.json','DEVNET-SAFE-AI-v0.1.7-README.md']
(out/'SHA256SUMS').write_text(''.join(hashlib.sha256((out/f).read_bytes()).hexdigest()+'  '+f+'\n' for f in files))
archive=root/'qa/devnet-safe-ai-v0.1.7/candidate.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(files+['SHA256SUMS']):
        zi=zipfile.ZipInfo(f,(2026,10,31,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=0o100644<<16
        z.writestr(zi,(out/f).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest=='46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6',digest
print('EXACT_V017_REBUILD_SHA256_PASS',digest)
