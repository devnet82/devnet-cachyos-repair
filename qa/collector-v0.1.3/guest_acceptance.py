#!/usr/bin/env python3
"""Installed CachyOS GRUB/BTRFS QEMU-only collector CLI acceptance.

Execute as unprivileged nobody from the guarded VM boot script. Never reads the
real user's host. All fixtures are constructed under a disposable VM /var/tmp.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

VERSION='0.1.3'

def sha(blob):return hashlib.sha256(blob).hexdigest()

def need(ok,message):
    if not ok:raise AssertionError(message)

def run(cmd,home):
    env=dict(os.environ);env.update({'HOME':str(home),'USER':'nobody','LOGNAME':'nobody',
      'XDG_CONFIG_HOME':str(home/'.config'),'XDG_DATA_HOME':str(home/'.local/share'),
      'DEVNET_QA_VM':'1','PYTHONNOUSERSITE':'1'})
    return subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=50)

def put(home,name,data):
    path=home/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    return path

def main():
    report={'schema':'devnet-installed-cachyos-collector-qa-v0.1.3',
      'app_version':VERSION,'candidate_sha256_expected':sys.argv[2],
      'checks':{},'gui_tray':'NOT_APPLICABLE_CLI',
      'app_hardware_acceptance':'NOT_TESTED','real_user_PC':'NOT_TESTED',
      'actual_installed_app_source_completeness':'NOT_TESTED',
      'release_approval':'BLOCKED'}
    collector=Path(sys.argv[1]);out=Path(sys.argv[3]);tmp=None
    try:
        need(os.geteuid()!=0,'root execution forbidden')
        need('ID=cachyos' in Path('/etc/os-release').read_text(),'not actual CachyOS')
        need(run(['findmnt','-no','FSTYPE','/'],Path('/tmp')).stdout.strip()=='btrfs',
            'not real BTRFS')
        report['checks']['real_installed_cachyos_btrfs']='PASS'
        need(sha(collector.read_bytes())==sys.argv[2],'collector source hash mismatch')
        need('VERSION = "0.1.3"' in collector.read_text(),'wrong candidate version')
        report['checks']['exact_candidate_integrity']='PASS'
        tmp=tempfile.TemporaryDirectory(prefix='devnet-collector-qa-',dir='/var/tmp')
        home=Path(tmp.name)/'home';home.mkdir();downloads=home/'Downloads';downloads.mkdir()
        bin=home/'.local/bin';bin.mkdir(parents=True)
        core={
          '.local/bin/vr-control':b'VR control binary fixture\n',
          '.local/bin/vr-control-gui':b'VR GUI binary fixture\n',
          '.local/bin/vr-doctor':b'VR Doctor fixture\n',
          '.local/bin/vr-stackd':b'VR daemon fixture\n',
          '.local/share/devnet-wayvr-watch-manager/doctor.py':b'APP_VERSION = "0.1.34"\n',
          '.local/share/devnet-wayvr-watch-manager/manager.py':b'MANAGER = True\n',
          '.local/share/devnet-wayvr-watch-manager/metrics.py':b'METRICS = True\n',
          '.local/share/devnet-wayvr-watch-manager/watchlib.py':b'WATCHLIB = True\n',
          '.local/share/devnet-wayvr-watch-manager/watch.xml':b'<watch>fixture</watch>\n',
          '.local/share/devnet-wayvr-watch-manager/devnet-hmd.svg':b'<svg></svg>\n',
          '.config/systemd/user/vr-stack-control.service':b'[Service]\nExecStart=/usr/bin/env true\n',
          '.local/share/applications/vr-control-panel.desktop':b'[Desktop Entry]\nName=Devnet VR\n',
        }
        for name,data in core.items():put(home,name,data)
        put(home,'.config/vr-stack/private.json',b'{"password":"DO_NOT_COLLECT"}')
        put(home,'.ssh/id_rsa',b'BEGIN RSA PRIVATE KEY\nDO_NOT_COLLECT')
        original={name:sha(data) for name,data in core.items()}
        installer=collector.parent/'install.sh';uninstaller=collector.parent/'uninstall.sh'
        need(run(['bash',str(installer),'--dry-run'],home).returncode==0,'install dry run failed')
        need(not (bin/'devnet-export-installed-apps').exists(),'dry run mutated HOME')
        need(run(['bash',str(installer)],home).returncode==0,'clean install failed')
        installed=bin/'devnet-export-installed-apps'
        need(installed.is_file(),'collector not installed')
        need(run([str(installed),'--doctor'],home).returncode==0,'Doctor failed')
        report['checks']['clean_install_and_doctor']='PASS'
        need(run([str(installed),'--version'],home).stdout.strip()==VERSION,'version mismatch')
        report['checks']['version_consistency']='PASS'
        first=run([str(installed),'--output-dir',str(downloads)],home)
        need(first.returncode==0,'normal collector export failed: '+first.stderr[-180:])
        files=list(downloads.glob('*.zip'))
        need(len(files)==1,'unexpected archive count')
        archive=files[0]
        need(archive.stat().st_mode&0o777==0o600,'archive not owner-private')
        with zipfile.ZipFile(archive) as z:
            need(z.testzip() is None,'ZIP CRC failed')
            m=json.loads(z.read('manifest.json'))
            need(m['tool_version']==VERSION,'report version mismatch')
            need(all(a['required_count']==a['required_found'] for a in m['applications'].values()),'incomplete app collected')
            for entry in m['files']:
                p=entry['path']
                need(sha(z.read('payload/'+p))==entry['sha256'],'ZIP sha mismatch')
                need(sha((home/p).read_bytes())==entry['sha256'],'source sha mismatch')
            need(not any(x.startswith('payload/.ssh/') or 'private.json' in x for x in z.namelist()),'private files copied')
            need(len(m['files'])==len(core),'unexpected file count')
        report['checks']['complete_export_and_zip_sha256']='PASS'
        report['checks']['private_settings_and_ssh_exclusion']='PASS'
        report['checks']['0600_archive_permissions']='PASS'
        privacy=home/'.local/bin/vr-doctor';contents=privacy.read_bytes()
        privacy.write_bytes(b'api_key = QA_FAKE_SENSITIVE_VALUE\n')
        count_before=len(list(downloads.glob('*.zip')))
        blocked=run([str(installed)],home)
        need(blocked.returncode!=0 and 'privacy indicators' in blocked.stderr,'privacy fail-close broken')
        need('QA_FAKE_SENSITIVE_VALUE' not in blocked.stderr,'private value leaked')
        need(len(list(downloads.glob('*.zip')))==count_before,'ZIP produced on privacy block')
        privacy.write_bytes(contents)
        report['checks']['privacy_default_fail_closed']='PASS'
        missing=home/'.local/bin/vr-stackd';data=missing.read_bytes();missing.unlink()
        blocked=run([str(installed)],home)
        need(blocked.returncode!=0 and 'Incomplete' in blocked.stderr,'incomplete app falsely accepted')
        need(len(list(downloads.glob('*.zip')))==count_before,'ZIP produced for incomplete app')
        missing.write_bytes(data)
        report['checks']['missing_source_fail_closed']='PASS'
        need(run(['bash',str(installer)],home).returncode==0,'repeat install failed')
        need(run(['bash',str(uninstaller),'--dry-run'],home).returncode==0,'uninstall dry-run failed')
        need(installed.is_file(),'uninstall dry-run removed file')
        need(run(['bash',str(uninstaller)],home).returncode==0,'uninstall failed')
        need(not installed.exists(),'uninstall left CLI')
        need(run(['bash',str(uninstaller)],home).returncode==0,'repeated uninstall failed')
        report['checks']['idempotent_install_uninstall']='PASS'
        need({name:sha((home/name).read_bytes()) for name in core}==original,'target app files were modified')
        report['checks']['target_app_read_only']='PASS'
    except BaseException as exc:
        report['checks']['guest_acceptance']='FAIL'
        report['error']=f'{type(exc).__name__}: {str(exc)[:230]}'
    finally:
        out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'checks':report['checks'],'app':VERSION},sort_keys=True))
        if tmp is not None:tmp.cleanup()
    return 1 if 'FAIL' in report['checks'].values() else 0

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('usage: guest_acceptance.py COLLECTOR SHA256 OUTJSON')
    raise SystemExit(main())
