import base64, hashlib, json, pathlib, sys, zipfile, zlib
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.')
base=root/'qa/devnet-safe-ai-v0.1.3/candidate.zip'
patchtext=(root/'qa/devnet-safe-ai-v0.1.4/patches-v014.zlib.b64').read_text()
patch=json.loads(zlib.decompress(base64.b64decode(patchtext)))
assert hashlib.sha256(base.read_bytes()).hexdigest()=='8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b'
out=root/'qa/devnet-safe-ai-v0.1.4/generated'
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(base) as z:
    assert z.testzip() is None
    for old,new in [('devnet-safe-ai-v0.1.3.py','devnet-safe-ai-v0.1.4.py'),('test_devnet_safe_ai_v0.1.3.py','test_devnet_safe_ai_v0.1.4.py')]:
        lines=z.read(old).decode().splitlines(keepends=True)
        for tag,lo,hi,replacement in reversed(patch[old]):
            assert tag in ('replace','insert','delete')
            lines[lo:hi]=replacement.splitlines(keepends=True)
        (out/new).write_text(''.join(lines))
    (out/'v0.1.2-baseline-permissions.json').write_bytes(z.read('v0.1.2-baseline-permissions.json'))
(out/'DEVNET-SAFE-AI-v0.1.4-README.md').write_text(patch['README'])
files=['devnet-safe-ai-v0.1.4.py','test_devnet_safe_ai_v0.1.4.py','v0.1.2-baseline-permissions.json','DEVNET-SAFE-AI-v0.1.4-README.md']
(out/'SHA256SUMS').write_text(''.join(hashlib.sha256((out/f).read_bytes()).hexdigest()+'  '+f+'\n' for f in files))
archive=root/'qa/devnet-safe-ai-v0.1.4/candidate.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(files+['SHA256SUMS']):
        zi=zipfile.ZipInfo(f,(2026,10,31,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=0o100644<<16
        z.writestr(zi,(out/f).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest=='deed961ee9c2c7be57c0a1e114ecba9d4250dd57041059eb29939f7b5c062781',digest
print('EXACT_V014_CANDIDATE_SHA256_PASS:',digest)
