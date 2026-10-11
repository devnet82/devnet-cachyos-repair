#!/usr/bin/env python3
"""Non-root installation, upgrade, uninstall and concurrency QA in sandboxed HOME."""
import concurrent.futures
import hashlib,json,os,shutil,stat,subprocess,tempfile,unittest,pwd
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INSTALL=ROOT/'install.sh';UNINSTALL=ROOT/'uninstall.sh'
SOURCE=ROOT/'devnet-export-installed-apps-v0.1.3.py'
COLLECTOR='devnet-export-installed-apps'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class InstallLifecycle(unittest.TestCase):
 def setUp(self):
  if os.geteuid()!=0:self.skipTest('requires root only to create a disposable nobody fixture')
  self.temp=tempfile.TemporaryDirectory(prefix='collector-upgrade-QA-')
  self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name);self.root.chmod(0o755)
  self.home=self.root/'nobody-home';self.home.mkdir()
  self.out=self.home/'Downloads';self.out.mkdir()
  user=pwd.getpwnam('nobody');self.uid=user.pw_uid;self.gid=user.pw_gid
  os.chown(self.home,self.uid,self.gid);os.chown(self.out,self.uid,self.gid)
  self.target=self.home/'.local/bin'/COLLECTOR

 def runner(self,argv,path=None):
  env={'HOME':str(self.home),'USER':'nobody','LOGNAME':'nobody','PATH':str(path) if path else '/usr/local/bin:/usr/bin:/bin'}
  return subprocess.run(['runuser','-u','nobody','--','env',*(f'{k}={v}' for k,v in env.items()),*map(str,argv)],capture_output=True,text=True,timeout=45)

 def assert_ok(self,r):
  self.assertEqual(r.returncode,0,r.stdout+'\n'+r.stderr)

 def make_target(self,content):
  self.assert_ok(self.runner(['mkdir','-p',self.target.parent]))
  self.assert_ok(self.runner(['bash','-c','cat > "$1"','bash',self.target],path='/usr/bin:/bin') if False else self.runner(['cp',SOURCE,self.target]))
  self.target.write_text(content)
  os.chown(self.target,self.uid,self.gid)
  self.target.chmod(0o755)

 def test_clean_install_and_dry_run(self):
  self.assert_ok(self.runner(['bash',INSTALL,'--dry-run']))
  self.assertFalse(self.target.exists())
  self.assert_ok(self.runner(['bash',INSTALL]))
  self.assertTrue(self.target.is_file())
  self.assertEqual(sha(self.target),sha(SOURCE))
  self.assertEqual(stat.S_IMODE(self.target.stat().st_mode),0o755)

 def test_idempotent_reinstall(self):
  self.assert_ok(self.runner(['bash',INSTALL]))
  a=sha(self.target)
  self.assert_ok(self.runner(['bash',INSTALL]))
  self.assertEqual(sha(self.target),a)
  self.assertFalse((self.home/'.local/share/devnet-installed-apps-collector/backups').exists())

 def test_upgrade_older_managed_candidate_preserves_backup(self):
  self.assert_ok(self.runner(['bash',INSTALL]))
  older=self.target.read_text().replace('VERSION = "0.1.3"','VERSION = "0.1.1"')
  self.target.write_text(older);os.chown(self.target,self.uid,self.gid)
  oldsha=sha(self.target)
  self.assert_ok(self.runner(['bash',INSTALL]))
  self.assertEqual(sha(self.target),sha(SOURCE))
  backups=list((self.home/'.local/share/devnet-installed-apps-collector/backups').iterdir())
  self.assertEqual(len(backups),1)
  self.assertEqual(sha(backups[0]),oldsha)
  self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode),0o600)
  self.assert_ok(self.runner(['bash',UNINSTALL]))
  self.assertFalse(self.target.exists())
  self.assertTrue(backups[0].is_file())

 def test_uninstall_idempotence(self):
  self.assert_ok(self.runner(['bash',INSTALL]))
  self.assert_ok(self.runner(['bash',UNINSTALL,'--dry-run']))
  self.assertTrue(self.target.exists())
  self.assert_ok(self.runner(['bash',UNINSTALL]))
  self.assertFalse(self.target.exists())
  self.assert_ok(self.runner(['bash',UNINSTALL]))

 def test_unmanaged_target_refused_no_overwrite(self):
  self.make_target('#!/usr/bin/env python3\nprint("original user program")\n')
  before=sha(self.target)
  r=self.runner(['bash',INSTALL]);self.assertNotEqual(r.returncode,0)
  self.assertEqual(before,sha(self.target))
  r=self.runner(['bash',UNINSTALL]);self.assertNotEqual(r.returncode,0)
  self.assertEqual(before,sha(self.target))

 def test_symlink_target_refused(self):
  self.assert_ok(self.runner(['mkdir','-p',self.target.parent]))
  outsider=self.home/'private';outsider.write_text('user data');os.chown(outsider,self.uid,self.gid)
  self.target.symlink_to(outsider)
  self.assertNotEqual(self.runner(['bash',INSTALL]).returncode,0)
  self.assertNotEqual(self.runner(['bash',UNINSTALL]).returncode,0)
  self.assertEqual(outsider.read_text(),'user data')

 def test_malicious_symlink_backup_dir_refused(self):
  self.assert_ok(self.runner(['bash',INSTALL]))
  older=self.target.read_text().replace('VERSION = "0.1.3"','VERSION = "0.1.1"')
  self.target.write_text(older);os.chown(self.target,self.uid,self.gid)
  old=sha(self.target)
  fake=self.home/'outside';fake.mkdir();os.chown(fake,self.uid,self.gid)
  base=self.home/'.local/share/devnet-installed-apps-collector';base.mkdir(parents=True)
  base.chmod(0o755);os.chown(base,self.uid,self.gid)
  (base/'backups').symlink_to(fake)
  self.assertNotEqual(self.runner(['bash',INSTALL]).returncode,0)
  self.assertEqual(old,sha(self.target))
  self.assertFalse(list(fake.iterdir()))

 def test_directory_permissions_preserved(self):
  self.assert_ok(self.runner(['mkdir','-p',self.target.parent]))
  self.assert_ok(self.runner(['chmod','700',self.target.parent]))
  self.assert_ok(self.runner(['bash',INSTALL]))
  self.assertEqual(stat.S_IMODE(self.target.parent.stat().st_mode),0o700)

 def test_permission_denied_no_clobber(self):
  self.assert_ok(self.runner(['mkdir','-p',self.target.parent]))
  self.assert_ok(self.runner(['chmod','500',self.target.parent]))
  r=self.runner(['bash',INSTALL]);self.assertNotEqual(r.returncode,0)
  self.assertFalse(self.target.exists())

 def test_abort_during_atomic_rename_no_clobber(self):
  self.assert_ok(self.runner(['bash',INSTALL]))
  older=self.target.read_text().replace('VERSION = "0.1.3"','VERSION = "0.1.1"')
  self.target.write_text(older);os.chown(self.target,self.uid,self.gid)
  old=sha(self.target)
  fakebin=self.root/'fake-bin';fakebin.mkdir()
  fake=fakebin/'mv';fake.write_text('#!/bin/sh\nexit 23\n');fake.chmod(0o755)
  r=self.runner(['bash',INSTALL],path=str(fakebin)+':/usr/bin:/bin')
  self.assertNotEqual(r.returncode,0)
  self.assertEqual(old,sha(self.target))
  self.assertFalse(list(self.target.parent.glob('.devnet-export-installed-apps.*')))

 def test_cli_requires_nonroot(self):
  r=subprocess.run(['bash',str(INSTALL)],capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0)
  self.assertIn('sudo/root',r.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
