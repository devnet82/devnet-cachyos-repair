from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from copy import copy
import json, stat, hashlib, sys
source=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/devnet-cachyos-repair-v0.1.19.zip')
target=Path(sys.argv[2]) if len(sys.argv)>2 else Path('/mnt/data/devnet-cachyos-repair-v0.1.20.zip')
oldpref='devnet-cachyos-repair-v0.1.19/'
newpref='devnet-cachyos-repair-v0.1.20/'
newtest='''"""Regression for the genuine CachyOS VM --cli --json crash (v0.1.20)."""
import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from devnet_cachyos_repair import cli

class CliJsonRegression(unittest.TestCase):
    def test_boot_doctor_json_export_no_shadowed_import(self):
        with tempfile.TemporaryDirectory() as td:
            dest=Path(td)/"private-report.json"
            sample={"root":{"source":"/home/private/should-never-export",
                            "fstype":"btrfs","is_snapshot":False,
                            "snapshot_id":"","writable":True}}
            with patch.object(cli,"do_scan",return_value=(sample,[])), patch.object(cli,"make_text_report",return_value="SAFE REPORT"):
                rc=cli.main(["--cli","--json",str(dest)])
            self.assertEqual(rc,0)
            self.assertTrue(dest.is_file())
            self.assertEqual(stat.S_IMODE(dest.stat().st_mode),0o600)
            content=dest.read_text()
            self.assertNotIn("/home/private",content)
            self.assertIsInstance(json.loads(content),dict)

if __name__ == "__main__": unittest.main()
'''
changed=[]
with ZipFile(source) as zin, ZipFile(target,'w',compression=ZIP_DEFLATED,compresslevel=7) as zout:
    for item in zin.infolist():
        assert item.filename.startswith(oldpref),item.filename
        relative=item.filename[len(oldpref):]
        content=zin.read(item)
        if relative=='devnet_cachyos_repair/cli.py':
            text=content.decode()
            old='            from .report import save_json\n'
            assert text.count(old)==1,(repr(old),text.count(old))
            content=text.replace(old,'').encode()
            changed.append(relative)
        elif relative=='README.md':
            text=content.decode()
            assert text.startswith('# Devnet CachyOS Repair v0.1.19')
            text=text.replace('# Devnet CachyOS Repair v0.1.19','# Devnet CachyOS Repair v0.1.20',1)
            text=text.replace('All application/package strings in this release are **0.1.19**.','All application/package strings in this release are **0.1.20**.')
            marker='## v0.1.17'
            assert text.count(marker)==1
            text=text.replace(marker,'''## v0.1.20 — Boot Doctor CLI JSON export fix (test candidate)

- Fix the confirmed CachyOS VM `--cli --json` failure by removing a redundant conditional `save_json` import that shadowed the existing module-level import.
- Add a regression test for a privacy-safe mode-0600 JSON export.
- Preserve the known-good v0.1.19 build. All destructive recovery and physical acceptance remain BLOCKED until tested.

'''+marker,1)
            content=text.encode()
            changed.append(relative)
        elif relative=='CHANGELOG.md':
            content=('''## 0.1.20 — 2026-10-10 (CachyOS VM CLI JSON export fix candidate)

- Fix `UnboundLocalError` when Boot Doctor CLI is called with `--cli --json`.
- Add direct regression of strict mode-0600 privacy-safe CLI JSON export.
- Preserve v0.1.19 as known good. New candidate is NOT APPROVED pending exact-build Master QA and physical acceptance.

'''+content.decode()).encode()
            changed.append(relative)
        elif relative=='QA_MANIFEST.json':
            m=json.loads(content)
            assert m['version']=='0.1.19'
            m['version']='0.1.20'
            m['checks'].append({'id':'cli_boot_doctor_json_export_0120','description':'Live CachyOS Boot Doctor --cli --json must write valid privacy-safe mode-0600 JSON without UnboundLocalError','required_environment':'REAL_CACHYOS_KDE_VM','required_evidence_kinds':['log','file'],'required_assertions':['no_traceback','valid_json','restricted_file_0600','no_private_paths']})
            assert len({x['id'] for x in m['checks']})==len(m['checks'])
            content=(json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode()
            changed.append(relative)
        elif relative=='QA_REPORT.md':
            t=content.decode().replace('v0.1.19 — QA evidence','v0.1.20 — QA evidence')
            t=t.replace('175/175 pure-Python','176/176 pure-Python')
            t=t.replace('**NOT TESTED HERE**: PySide6 real Qt widget tests, real CachyOS KDE VM (Wayland/X11),','**Earlier v0.1.19 VM evidence**: 19/19 packaged stages and 33/33 Qt checks under native KDE Wayland passed in Q35/PC guests. **NOT YET RETESTED FOR v0.1.20**: live VM,')
            content=t.encode()
            changed.append(relative)
        elif relative in {'qa.sh','install.sh','devnet_cachyos_repair/__init__.py','tests/test_version.py','tests/test_manifest_0115.py','tests/test_preupdate_0116.py'}:
            t=content.decode()
            assert '0.1.19' in t
            content=t.replace('0.1.19','0.1.20').encode()
            changed.append(relative)
        info=copy(item)
        info.filename=newpref+relative
        zout.writestr(info,content)
    info=ZipInfo(newpref+'tests/test_cli_json_0120.py')
    info.create_system=3
    info.external_attr=(stat.S_IFREG|0o644)<<16
    info.compress_type=ZIP_DEFLATED
    zout.writestr(info,newtest)
with ZipFile(target) as z:
    assert z.testzip() is None
    assert len(z.namelist())==56
print('SHA256',hashlib.sha256(target.read_bytes()).hexdigest())
print('SIZE',target.stat().st_size,'FILES',len(ZipFile(target).namelist()),'CHANGED',','.join(changed))