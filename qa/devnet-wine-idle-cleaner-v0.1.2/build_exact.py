#!/usr/bin/env python3
"""Reconstruct exact v0.1.2 from immutable original v0.1.1 ZIP; fail on byte drift."""
from pathlib import Path
import shutil,hashlib,zipfile,os,subprocess,json,stat,re
root=Path('/tmp/devnet-v012-git-simulation')
root.mkdir(parents=True,exist_ok=True)
zip_src=Path('qa/devnet-wine-idle-cleaner-v0.1.1/candidate.zip')
assert hashlib.sha256(zip_src.read_bytes()).hexdigest()=='f11cd9bd6e5ea0f4738ddf472be9ff8c79dcfa5c2fea85a843ca1a2d8bf8889b'
with zipfile.ZipFile(zip_src) as parent:
    assert parent.testzip() is None
    parent.extractall(root)
src=root/'devnet-wine-idle-cleaner-v0.1.1-QA-BLOCKED'
out=root/'devnet-wine-idle-cleaner-v0.1.2-QA-BLOCKED'
if out.exists(): raise RuntimeError('Refusing to overwrite v0.1.2 source')
out.mkdir()
for n in ('README.md','monitor.py','test_monitor.py','test_install.py','install.sh','uninstall.sh','devnet-wine-idle-cleaner.service','devnet-wine-idle-cleaner.timer'):
    shutil.copy2(src/n,out/n)
monitor=out/'monitor.py'; monitor.write_text(monitor.read_text().replace('VERSION = "0.1.1"','VERSION = "0.1.2"'))
service=out/'devnet-wine-idle-cleaner.service'
service.write_text('''[Unit]
Description=Devnet Wine prefix service-only cleanup (Fusion) — fail closed
[Service]
Type=oneshot
ExecStart=%h/.local/bin/devnet-wine-idle-cleaner tick --execute
NoNewPrivileges=yes
UMask=0077
# Do not use ProtectSystem/ProtectHome/ReadWritePaths in a user manager: these
# can require a private user namespace, denying /proc/PID/environ inspection.
# Scoped writes are implemented by the Python monitor; runs unprivileged.
''')
p=out/'test_monitor.py'; t=p.read_text(); pos=t.index('if __name__=="__main__":')
t=t[:pos]+'''class UserSystemdNamespaceTests(unittest.TestCase):
    def setUp(self):
        lines=(ROOT / "devnet-wine-idle-cleaner.service").read_text().splitlines()
        self.props=dict(line.split("=",1) for line in lines if line and not line.lstrip().startswith(('[','#')) and '=' in line)
    def test_no_mount_isolation_for_proc_environ_access(self):
        for key in ("ProtectSystem","ProtectHome","ReadWritePaths","PrivateUsers","PrivateTmp", "RootDirectory", "RootImage"):
            self.assertNotIn(key, self.props, f"{key} can isolate /proc or break Wine sockets")
    def test_user_service_retains_no_privilege_escalation(self):
        self.assertEqual(self.props.get("NoNewPrivileges"),"yes")
        self.assertEqual(self.props.get("UMask"),"0077")
        self.assertNotIn("User",self.props)
    def test_oneshot_exact_pinned_executable_and_args(self):
        self.assertEqual(self.props.get("Type"),"oneshot")
        self.assertEqual(self.props.get("ExecStart"),"%h/.local/bin/devnet-wine-idle-cleaner tick --execute")

'''+t[pos:]
p.write_text(t)
readme=out/'README.md'; s=readme.read_text().replace('v0.1.1','v0.1.2').replace('33/33 offline behavioural','36/36 offline behavioural');s+='''
## Revision v0.1.2 — systemd user-namespace compatibility fix

In real GitHub user-systemd integration, v0.1.1 passed all direct-process tests,
but systemd execution returned `INSPECTION_BLOCKED` because the unit's
`ProtectSystem=full`, `ProtectHome=read-only` and `ReadWritePaths=` enabled
mount namespace isolation. In a user-managed service this can involve a
separate user namespace, preventing read access to the original Wine process
`/proc/PID/environ`. The combined settings were removed **only** from the
service unit; `NoNewPrivileges=yes`, `UMask=0077`, existing rootless operation,
explicit-prefix-only stopping, double process scans, stale session protection,
and all fail-closed guards remain. These changes reduce filesystem isolation
from v0.1.1. The command is still an unprivileged Python program and performs
no shell execution except executing the configured prefix-specific Wine binary.
The source and installer preserve existing Wine prefixes and OpenCode setup.

Installation is explicitly BLOCKED pending fresh real GitHub native CachyOS VM
and user-systemd 180-second scheduled timer, active-app safety, rollback, and
host final acceptance checks on this **exact** ZIP. Do not install yet.
'''
readme.write_text(s)
files=['README.md','monitor.py','test_monitor.py','test_install.py','install.sh','uninstall.sh','devnet-wine-idle-cleaner.service','devnet-wine-idle-cleaner.timer']
(out/'SHA256SUMS').write_text(''.join(hashlib.sha256((out/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in files))
archive=root/'devnet-wine-idle-cleaner-v0.1.2-QA-BLOCKED.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name in files+['SHA256SUMS']:
    p=out/name;info=zipfile.ZipInfo(out.name+'/'+name);info.compress_type=zipfile.ZIP_DEFLATED;info.create_system=3;info.external_attr=(0o100755 if name in ('monitor.py','install.sh','uninstall.sh') else 0o100644)<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
h=hashlib.sha256(archive.read_bytes()).hexdigest()
assert h=='5cf355189c7ab0a815260724a9881bb729d69c112c4ae603defe78b1ad678d5d',f'exact archive drift: {h}'
print('EXACT_V012_RECONSTRUCTED_ARCHIVE_SHA256_PASS',h,'SIZE',archive.stat().st_size)
