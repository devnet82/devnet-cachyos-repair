#!/usr/bin/env python3
"""Disposable installed CachyOS lifecycle test for low-risk user-scoped Devnet ZIPs."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def status(report,name,state,detail):
    report["checks"][name]={"status":state,"detail":detail}

def execute(cmd,cwd,home,uid,gid,log,label):
    env={"HOME":str(home),"USER":"nobody","LOGNAME":"nobody",
         "PATH":"/usr/local/bin:/usr/bin:/bin",
         "XDG_CONFIG_HOME":str(home/".config"),
         "XDG_DATA_HOME":str(home/".local/share"),
         "XDG_CACHE_HOME":str(home/".cache"),
         "DEVNET_QA_VM":"1",
         "DISPLAY":"","WAYLAND_DISPLAY":"","DBUS_SESSION_BUS_ADDRESS":""}
    try:
        p=subprocess.run(["runuser","-u","nobody","--","env",*(f"{k}={v}" for k,v in env.items()),*cmd],
            cwd=cwd,capture_output=True,text=True,errors="replace",timeout=120)
        result={"exit_code":p.returncode,"timeout":False}
        with log.open("a") as f:f.write("\n=== "+label+" ===\n"+(p.stdout+"\n"+p.stderr)[-16000:]+"\n")
        return result
    except subprocess.TimeoutExpired:
        with log.open("a") as f:f.write("\n=== "+label+" TIMEOUT=120 ===\n")
        return {"exit_code":None,"timeout":True}

def files(home):
    return {str(p.relative_to(home)) for p in home.rglob("*") if p.is_file() or p.is_symlink()}

def main():
    if len(sys.argv)!=6:raise SystemExit("usage: script ZIP SHA APP REPORT LOG")
    archive=Path(sys.argv[1]);sha=sys.argv[2];app=sys.argv[3]
    out=Path(sys.argv[4]);log=Path(sys.argv[5])
    report={"format":"devnet-installed-lifecycle-v0.1.0","app":app,"checks":{},
       "upgrade":"NOT_TESTED","app_internal_rollback":"NOT_TESTED",
       "config_migration":"NOT_TESTED","gui_tray":"NOT_TESTED",
       "hardware_acceptance":"NOT_TESTED","network_reconnect":"NOT_TESTED",
       "service_lifecycle":"NOT_TESTED","master_qa":"BLOCKED"}
    try:
        if Path("/etc/os-release").read_text().splitlines().count("ID=cachyos")!=1:raise ValueError("Not CachyOS")
        if subprocess.check_output(["findmnt","-no","FSTYPE","/"],text=True).strip()!="btrfs":raise ValueError("Not booted from BTRFS")
        if subprocess.check_output(["lsblk","-dn","-o","SERIAL","/dev/vdb"],text=True).strip()!="DEVNETQAONLY":raise ValueError("Unexpected system disk")
        if subprocess.check_output(["lsblk","-dn","-o","SERIAL","/dev/vda"],text=True).strip()!="DEVNETCONTROL":raise ValueError("Unexpected evidence disk")
        status(report,"isolated_installed_cachyos","PASS","booted native CachyOS, BTRFS, disk serial guards")
        if digest(archive)!=sha:raise ValueError("Exact package SHA256 mismatch")
        status(report,"original_zip","PASS","Exact original candidate hash")
        home=Path("/var/tmp/devnet-lifecycle-home")
        workspace=Path("/var/tmp/devnet-lifecycle-package")
        if home.exists() or workspace.exists():raise ValueError("Guest is not a clean lifecycle environment")
        home.mkdir(mode=0o700);workspace.mkdir(mode=0o700)
        nobody=pwd.getpwnam("nobody")
        with zipfile.ZipFile(archive) as z:
            infos=z.infolist()
            if not infos or len(infos)>10000 or sum(i.file_size for i in infos)>64*1024*1024:raise ValueError("Unsafe archive")
            names=set()
            for x in infos:
                n=x.filename
                if n in names or n.startswith(("/","\\")) or "\\" in n or ".." in PurePosixPath(n).parts or stat.S_ISLNK(x.external_attr>>16):
                    raise ValueError("Unsafe ZIP member")
                names.add(n)
            if z.testzip():raise ValueError("Bad ZIP CRC")
            z.extractall(workspace)
            for info in infos:
                p=workspace/info.filename
                if not info.is_dir() and p.is_file():
                    should_exec=bool((info.external_attr>>16)&0o111) or info.filename.endswith(".sh")
                    if should_exec:p.chmod(p.stat().st_mode|0o111)
        roots=[x for x in workspace.iterdir() if x.is_dir()]
        root=roots[0] if len(roots)==1 else workspace
        install=root/"install.sh";uninstall=root/"uninstall.sh"
        if not install.is_file() or not uninstall.is_file():
            status(report,"install_uninstall","NOT_TESTED","Expected root install.sh + uninstall.sh absent")
        else:
            for dirpath,ds,fs in os.walk(workspace):
                for n in ds+fs:
                    f=Path(dirpath)/n
                    if not f.is_symlink():os.chown(f,nobody.pw_uid,nobody.pw_gid)
            os.chown(workspace,nobody.pw_uid,nobody.pw_gid)
            os.chown(home,nobody.pw_uid,nobody.pw_gid)
            baseline=files(home)
            first=execute(["bash",str(install)],root,home,nobody.pw_uid,nobody.pw_gid,log,"CLEAN INSTALL")
            installed=files(home)
            added=installed-baseline
            report["install_process"]=first
            report["home_file_count_after_install"]=len(added)
            if first["exit_code"]==0 and added:
                status(report,"clean_install","PASS",f"installer exit=0; {len(added)} home files created")
            elif first["exit_code"]==0:
                status(report,"clean_install","NOT_TESTED","installer reported success but no user-home installation footprint; requires verification")
            else:
                status(report,"clean_install","FAIL",f"installer failed or timed out: {first}")
            if first["exit_code"]==0:
                un=execute(["bash",str(uninstall)],root,home,nobody.pw_uid,nobody.pw_gid,log,"UNINSTALL")
                remaining=files(home)&added
                report["uninstall_process"]=un
                report["home_file_count_remaining"]=len(remaining)
                if un["exit_code"]==0:
                    status(report,"uninstall","PASS",f"uninstaller exit=0; {len(remaining)} files remain (possibly config, requires residual audit)")
                else:status(report,"uninstall","FAIL",f"uninstall failed or timed out: {un}")
            else:status(report,"uninstall","NOT_TESTED","clean installation did not succeed")
        status(report,"package_checksum_and_unzip","PASS","verified and extracted only to disposable VM")
    except Exception as e:
        report["harness_error"]=repr(e)[:500]
        status(report,"lifecycle_harness","FAIL",type(e).__name__)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"app":app,"checks":report["checks"]},sort_keys=True))
    return 1 if any(x["status"]=="FAIL" for x in report["checks"].values()) else 0

if __name__=="__main__":raise SystemExit(main())
