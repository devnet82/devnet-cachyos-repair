#!/usr/bin/env python3
"""Isolated non-root integration with exact preview ZIP source bytes; no app execution."""
import hashlib,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
import pwd
ROOT=Path(__file__).resolve().parent
COLLECTOR=ROOT/'devnet-export-installed-apps-v0.1.2.py'
ORIGINALS={
 'vr':'/mnt/data/devnet_full_qa/devnet-vr-stack-control-v0.6.135-QA-PREVIEW.zip',
 'wayvr':'/mnt/data/devnet_full_qa/devnet-wayvr-watch-manager-v0.1.38-QA-PREVIEW.zip',
}

def sha(b):return hashlib.sha256(b).hexdigest()

def prepare(home):
    exact={}
    for app,archive in ORIGINALS.items():
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                if name.endswith('/'):continue
                parts=name.split('/')
                if len(parts)<3:continue
                folder=parts[1];relative='/'.join(parts[2:]);dest=None
                if app=='vr':
                    if folder=='bin':dest=home/'.local/bin'/relative
                    elif folder=='desktop':dest=home/'.local/share/applications'/relative
                    elif folder=='systemd':dest=home/'.config/systemd/user'/relative
                else:
                    if folder=='bin':dest=home/'.local/bin'/relative
                    elif folder=='desktop':dest=home/'.local/share/applications'/relative
                    elif folder=='systemd':dest=home/'.config/systemd/user'/relative
                    elif folder=='app':dest=home/'.local/share/devnet-wayvr-watch-manager'/relative
                if dest is None:continue
                payload=z.read(name)
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(payload)
                exact[str(dest.relative_to(home))]=sha(payload)
    return exact

def invoke(home,*args):
    return subprocess.run(['runuser','-u','nobody','--','env','HOME='+str(home),'USER=nobody','LOGNAME=nobody',*args],capture_output=True,text=True,timeout=50)

def assert_success(p,desc):
    if p.returncode!=0:raise AssertionError(f'{desc} exited {p.returncode}: {p.stdout[-1000:]} {p.stderr[-1000:]}')

with tempfile.TemporaryDirectory(prefix='devnet-master-qa-') as td:
    root=Path(td);root.chmod(0o755)
    home=root/'home';home.mkdir();out=home/'Downloads';out.mkdir()
    sources=prepare(home)
    # Preview binaries remain files; none are executed by integration collector.
    original_snapshot={s:sha((home/s).read_bytes()) for s in sources}
    nobody=pwd.getpwnam('nobody')
    for path in sorted(home.rglob('*'),key=lambda p:len(p.parts)):
        if not path.is_symlink():os.chown(path,nobody.pw_uid,nobody.pw_gid)
    os.chown(home,nobody.pw_uid,nobody.pw_gid)
    assert_success(invoke(home,'bash',str(ROOT/'install.sh'),'--dry-run'),'clean install dry-run')
    if (home/'.local/bin/devnet-export-installed-apps').exists():raise AssertionError('dry-run modified home')
    assert_success(invoke(home,'bash',str(ROOT/'install.sh')),'clean install')
    installed=home/'.local/bin/devnet-export-installed-apps'
    assert installed.exists() and 'VERSION = "0.1.2"' in installed.read_text()
    assert_success(invoke(home,str(installed),'--doctor'),'doctor')
    # Insert a temporary privacy fixture to test fail-closed CLI behaviour;
    # restore the exact original preview source bytes before final export.
    privacy_file=home/'.local/bin/vr-doctor'
    unmodified=privacy_file.read_bytes()
    privacy_file.write_bytes(unmodified+b"\n# api_key = qa_marker\n")
    direct=invoke(home,str(installed),'--output-dir',str(out))
    if direct.returncode != 2 or 'privacy indicators' not in direct.stderr:
        raise AssertionError('Privacy gate unexpectedly passed: '+direct.stderr[-300:]+direct.stdout[-300:])
    if list(out.glob('*.zip')):raise AssertionError('Privacy gate produced an archive')
    privacy_file.write_bytes(unmodified)
    completed=invoke(home,str(installed),'--output-dir',str(out),'--allow-privacy-flags')
    assert_success(completed,'review-approved private export')
    archives=list(out.glob('*.zip'))
    assert len(archives)==1,archives
    archive=archives[0]
    assert archive.stat().st_mode & 0o777==0o600,oct(archive.stat().st_mode)
    with zipfile.ZipFile(archive) as z:
        report=json.loads(z.read('manifest.json'))
        assert report['tool_version']=='0.1.2'
        assert report['files_collected']>9
        assert all(v['required_count']==v['required_found'] for v in report['applications'].values())
        for r in report['files']:
            source=home/r['path']
            assert sha(source.read_bytes())==r['sha256']
            assert sha(z.read('payload/'+r['path']))==r['sha256']
            assert original_snapshot[r['path']]==r['sha256']
    assert_success(invoke(home,'bash',str(ROOT/'install.sh')),'repeat install')
    assert_success(invoke(home,'bash',str(ROOT/'uninstall.sh'),'--dry-run'),'uninstall dry run')
    assert installed.exists()
    assert_success(invoke(home,'bash',str(ROOT/'uninstall.sh')),'uninstall')
    assert not installed.exists()
    assert_success(invoke(home,'bash',str(ROOT/'uninstall.sh')),'repeat uninstall')
    assert {s:sha((home/s).read_bytes()) for s in original_snapshot}==original_snapshot, 'Collector altered source apps'
    print(json.dumps({'status':'PASS','source':'exact v0.6.135 and v0.1.38 preview ZIP bytes',
         'source_file_count':len(sources),'collected_files':report['files_collected'],
         'privacy_flagged_files':report['privacy_indicator_file_count'],
         'archive_private_mode':'0600','install':'PASS','doctor':'PASS','privacy_block':'PASS',
         'opt_in_export':'PASS','manifest_sha256':'PASS','repeat_install':'PASS',
         'uninstall':'PASS','repeat_uninstall':'PASS','source_modified':False},sort_keys=True))
