#!/usr/bin/env python3
"""Master QA safety, install and failure-path regression suite: CLI only."""
import contextlib
import datetime
import errno
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'devnet-export-installed-apps-v0.1.2.py'
spec=importlib.util.spec_from_file_location('collector_012',SOURCE)
collector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class CollectorMasterQATests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.home=self.root/'home'
        self.home.mkdir()
        self.output=self.root/'Downloads'
        self.output.mkdir()

    def put(self,name,data=b'#!/usr/bin/env python3\nprint("hello")\n'):
        p=self.home/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(data)
        return p

    def setup_apps(self,apps=('vr_stack','wayvr')):
        for app in apps:
            for x in collector.REQUIRED[app]:
                self.put(x)

    def export(self,apps=('vr_stack','wayvr'),**kwargs):
        return collector.export(self.home,self.output,apps,**kwargs)

    def assert_no_output(self):
        self.assertFalse(list(self.output.glob('*.zip')))
        self.assertFalse(list(self.output.glob('*.partial')))

    def test_version_consistency(self):
        self.assertEqual(collector.VERSION,'0.1.2')
        self.assertEqual((ROOT/'VERSION').read_text().strip(),collector.VERSION)
        self.assertIn('DEVNET_COLLECTOR_MANAGED',SOURCE.read_text()[:120])

    def test_success_both_full_fixtures(self):
        self.setup_apps()
        p,r=self.export()
        self.assertEqual(r['files_collected'],9)
        self.assertEqual(set(r['selected_apps']),set(collector.REQUIRED))
        self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
        self.assertTrue(all(v['required_found']==v['required_count'] for v in r['applications'].values()))
        with zipfile.ZipFile(p) as z:
            self.assertIsNone(z.testzip())
            m=json.loads(z.read('manifest.json'))
            self.assertEqual(m['schema'],'devnet-installed-app-source-export-v2')
            for x in m['files']:
                self.assertEqual(hashlib.sha256(z.read('payload/'+x['path'])).hexdigest(),x['sha256'])

    def test_incomplete_vr_fails_and_no_zip(self):
        self.put('.local/bin/vr-control')
        with self.assertRaisesRegex(collector.ExportBlocked,'Incomplete'):
            self.export()
        self.assert_no_output()

    def test_full_vr_but_missing_wayvr_fails_default(self):
        self.setup_apps(('vr_stack',))
        with self.assertRaisesRegex(collector.ExportBlocked,'wayvr 0/5'):
            self.export()
        self.assert_no_output()

    def test_explicit_single_app_allowed(self):
        self.setup_apps(('vr_stack',))
        p,r=self.export(('vr_stack',))
        self.assertEqual(r['selected_apps'],['vr_stack'])
        self.assertEqual(r['files_collected'],4)
        self.assertTrue(p.is_file())

    def test_empty_fails(self):
        with self.assertRaises(collector.ExportBlocked):self.export()
        self.assert_no_output()

    def test_doctor_missing_reports_nonzero_no_output(self):
        x=io.StringIO()
        with contextlib.redirect_stdout(x):status=collector.doctor(self.home,tuple(collector.REQUIRED))
        self.assertEqual(status,2)
        self.assertIn('MISSING:',x.getvalue())
        self.assert_no_output()

    def test_doctor_success_complete(self):
        self.setup_apps()
        with contextlib.redirect_stdout(io.StringIO()):status=collector.doctor(self.home,tuple(collector.REQUIRED))
        self.assertEqual(status,0)

    def test_source_dir_symlink_refused(self):
        external=self.root/'external';external.mkdir()
        self.setup_apps(('vr_stack',))
        d=self.home/'.local/share/devnet-wayvr-watch-manager';d.parent.mkdir(parents=True,exist_ok=True)
        d.symlink_to(external,target_is_directory=True)
        with self.assertRaisesRegex(collector.ExportBlocked,'unsafe or symlinked'):
            self.export()
        self.assert_no_output()

    def test_nested_dir_symlink_does_not_escape_home(self):
        external=self.root/'external';external.mkdir()
        for name in ['doctor.py','manager.py','metrics.py','watchlib.py','watch.xml']:
            (external/name).write_text('secret outsider')
        self.setup_apps(('vr_stack',))
        dest=self.home/'.local/share';dest.mkdir(parents=True)
        (dest/'devnet-wayvr-watch-manager').symlink_to(external,target_is_directory=True)
        with self.assertRaises(collector.ExportBlocked):self.export()
        self.assert_no_output()

    def test_required_leaf_symlink_rejected(self):
        self.setup_apps()
        p=self.home/'.local/bin/vr-stackd';p.unlink()
        outside=self.root/'secret';outside.write_text('secret key = PRIVATE')
        p.symlink_to(outside)
        with self.assertRaisesRegex(collector.ExportBlocked,'Incomplete'):
            self.export()
        self.assert_no_output()

    def test_source_hardlink_rejected(self):
        self.setup_apps()
        p=self.home/'.local/bin/vr-stackd';other=self.root/'linked'
        os.link(p,other)
        with self.assertRaisesRegex(collector.ExportBlocked,'Incomplete'):
            self.export()
        self.assert_no_output()

    def test_forbidden_asset_directories_excluded(self):
        self.setup_apps()
        self.put('.local/share/devnet-wayvr-watch-manager/backups/old.py',b'PRIVATE')
        self.put('.local/share/devnet-wayvr-watch-manager/state/token.txt',b'PRIVATE')
        self.put('.local/share/devnet-wayvr-watch-manager/logs/log.py',b'PRIVATE')
        p,r=self.export()
        with zipfile.ZipFile(p) as z:
            paths='\n'.join(z.namelist())
            self.assertNotIn('backups/',paths)
            self.assertNotIn('state/',paths)
            self.assertNotIn('logs/',paths)

    def test_no_private_xdg_config_included(self):
        self.setup_apps()
        self.put('.config/devnet-wayvr-watch-manager/config.json',b'{"password":"sensitive"}')
        self.put('.config/vr-stack/secrets.py',b'token=PRIVATE')
        p,_=self.export()
        with zipfile.ZipFile(p) as z:
            self.assertNotIn('payload/.config/vr-stack/secrets.py',z.namelist())
            self.assertNotIn('payload/.config/devnet-wayvr-watch-manager/config.json',z.namelist())

    def test_ssh_and_downloads_not_read(self):
        self.setup_apps()
        self.put('.ssh/id_rsa',b'BEGIN RSA PRIVATE KEY')
        self.put('Downloads/secret.txt',b'password = important')
        p,_=self.export()
        with zipfile.ZipFile(p) as z:
            self.assertFalse(any('/.ssh/' in x or '/Downloads/' in x for x in z.namelist()))

    def test_privacy_signal_blocks_before_zip_created(self):
        self.setup_apps()
        self.put('.local/bin/vr-doctor',b'api_key = super_secret_value\n')
        with self.assertRaisesRegex(collector.ExportBlocked,'privacy indicators') as e:
            self.export()
        self.assertNotIn('super_secret_value',str(e.exception))
        self.assert_no_output()

    def test_explicit_privacy_optin_preserves_original(self):
        self.setup_apps()
        source=b'api_key = known_test_value\n'
        self.put('.local/bin/vr-doctor',source)
        p,report=self.export(allow_privacy_flags=True)
        self.assertEqual(report['privacy_indicator_file_count'],1)
        self.assertEqual(report['privacy_flagged_paths'],['.local/bin/vr-doctor'])
        with zipfile.ZipFile(p) as z:
            self.assertEqual(z.read('payload/.local/bin/vr-doctor'),source)

    def test_private_path_signal_blocks(self):
        self.setup_apps()
        self.put('.local/bin/vr-doctor',b'log_path = "/home/privateuser/Desktop"\n')
        with self.assertRaisesRegex(collector.ExportBlocked,'privacy indicators'):self.export()
        self.assert_no_output()

    def test_symlink_output_dir_blocked(self):
        self.setup_apps()
        alias=self.root/'alias';alias.symlink_to(self.output,target_is_directory=True)
        with self.assertRaisesRegex(collector.ExportBlocked,'symlinks'):
            collector.export(self.home,alias,tuple(collector.REQUIRED))
        self.assert_no_output()

    def test_parent_symlink_output_blocked(self):
        self.setup_apps()
        alias=self.root/'alias';alias.symlink_to(self.output,target_is_directory=True)
        with self.assertRaisesRegex(collector.ExportBlocked,'symlinks'):
            collector.export(self.home,alias/'nested',tuple(collector.REQUIRED))
        self.assert_no_output()

    def test_missing_outdir_created_private(self):
        self.setup_apps()
        new=self.root/'PrivateExports'
        p,_=collector.export(self.home,new,tuple(collector.REQUIRED))
        self.assertTrue(p.is_file())
        self.assertEqual(stat.S_IMODE(new.stat().st_mode),0o700)

    def test_unwritable_output_fails(self):
        self.setup_apps()
        with mock.patch.object(collector.os,'access',return_value=False):
            with self.assertRaisesRegex(collector.ExportBlocked,'not writable'):self.export()
        self.assert_no_output()

    def test_simulated_disk_full_leaves_no_partial_file(self):
        self.setup_apps()
        original=zipfile.ZipFile.writestr
        def fault(z,*args,**kwargs):
            if len(z.namelist())>=2:raise OSError(errno.ENOSPC,'Simulated disk full')
            return original(z,*args,**kwargs)
        with mock.patch.object(zipfile.ZipFile,'writestr',fault):
            with self.assertRaises(OSError):self.export()
        self.assert_no_output()

    def test_archive_never_overwrites_first_or_conflicting_target(self):
        self.setup_apps()
        first,_=self.export()
        old=first.read_bytes()
        second,_=self.export()
        self.assertNotEqual(first,second)
        self.assertEqual(first.read_bytes(),old)
        self.assertTrue(first.is_file() and second.is_file())

    def test_stale_partial_files_unmodified(self):
        self.setup_apps()
        old=self.output/'.devnet-collector-prior.partial';old.write_bytes(b'old unrelated file')
        self.export()
        self.assertEqual(old.read_bytes(),b'old unrelated file')

    def test_source_change_detected(self):
        self.setup_apps()
        path=self.home/'.local/bin/vr-control'
        original_read=collector.os.read
        flag={'done':False}
        def changed(fd,n):
            chunk=original_read(fd,n)
            if chunk and not flag['done']:
                flag['done']=True
                path.write_bytes(b'CHANGED')
            return chunk
        with mock.patch.object(collector.os,'read',side_effect=changed):
            with self.assertRaisesRegex(collector.ExportBlocked,'Incomplete'):
                self.export()
        self.assert_no_output()

    def test_unsafe_dotdot_path_read_blocked(self):
        with self.assertRaises(collector.ExportBlocked):
            collector._safe_read(self.home,Path('../secrets'))

    def test_max_file_limit_enforced(self):
        self.setup_apps()
        self.put('.local/bin/vr-control',b'x'*(collector.MAX_FILE+1))
        with self.assertRaisesRegex(collector.ExportBlocked,'Incomplete'):self.export()

    def test_total_limit_enforced(self):
        self.setup_apps()
        with mock.patch.object(collector,'MAX_TOTAL',10):
            with self.assertRaisesRegex(collector.ExportBlocked,'limit exceeded'):self.export()
        self.assert_no_output()

    def test_asset_count_limit_is_not_silent(self):
        self.setup_apps()
        self.put('.local/share/devnet-wayvr-watch-manager/extra.py')
        with mock.patch.object(collector,'MAX_FILES',5):
            with self.assertRaises(collector.ExportBlocked):self.export()

    def test_exact_known_app_resources_included(self):
        self.setup_apps()
        for name in ['devnet-controller_l.svg','devnet-controller_r.svg','devnet-hmd.svg','toggle.py','adbsetup.py']:
            self.put('.local/share/devnet-wayvr-watch-manager/'+name,b'EXAMPLE ASSET')
        p,_=self.export()
        with zipfile.ZipFile(p) as z:
            for name in ['devnet-controller_l.svg','devnet-controller_r.svg','devnet-hmd.svg','toggle.py','adbsetup.py']:
                self.assertIn('payload/.local/share/devnet-wayvr-watch-manager/'+name,z.namelist())

    def test_doctor_never_creates_archive(self):
        self.setup_apps()
        with contextlib.redirect_stdout(io.StringIO()):
            result=collector.main(['--home',str(self.home),'--output-dir',str(self.output),'--doctor'])
        # Running unit suite as root must not be mistaken for app acceptance.
        self.assertEqual(result,2 if os.geteuid()==0 else 0)
        self.assert_no_output()

    def test_user_cli_root_refusal(self):
        if os.geteuid()!=0:self.skipTest('root-only safeguard')
        out=subprocess.run([sys.executable,str(SOURCE),'--doctor'],capture_output=True,text=True)
        self.assertEqual(out.returncode,2)
        self.assertIn('do not run',out.stderr)

    def test_no_implicit_network_or_service_execution(self):
        source=SOURCE.read_text()
        for marker in ('requests.get','socket.connect','subprocess.run','os.system','systemctl','adb shell','sudo '):
            self.assertNotIn(marker,source)

if __name__=='__main__':
    unittest.main(verbosity=2)
