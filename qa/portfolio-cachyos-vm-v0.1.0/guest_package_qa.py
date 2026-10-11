#!/usr/bin/env python3
"""Read-only metadata checks plus UNPRIVILEGED packaged tests in disposable CachyOS VM.

No app installers, no privilege escalation of archive code, and no network attached.
Writes evidence only to explicit FAT /mnt locations.
"""
from __future__ import annotations
import ast
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
import time
import zipfile

MAX_TESTS=20
MAX_SIZE=64*1024*1024

def hash_file(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for data in iter(lambda:f.read(1024*1024),b""):h.update(data)
    return h.hexdigest()

def check(out, name, status, detail):
    out["checks"][name]={"status":status,"detail":detail}

def main():
    if len(sys.argv)!=6:
        raise SystemExit("usage: guest_package_qa.py ZIP SHA256 VERSION REPORT LOG")
    p=Path(sys.argv[1]);expected=sys.argv[2];version=sys.argv[3]
    report=Path(sys.argv[4]);logfile=Path(sys.argv[5])
    out={"format":"devnet-native-cachyos-vm-qa-v0.1.0",
         "package":p.name,"expected_version":version,
         "checks":{},"tests":[],"release_decision":"BLOCKED",
         "overall":"INCOMPLETE"}
    logfile.write_text("Disposable CachyOS guest test log\n")
    try:
        osrel=Path("/etc/os-release").read_text()
        native = any(line == "ID=cachyos" for line in osrel.splitlines())
        check(out,"native_cachyos","PASS" if native else "FAIL",
              "Guest /etc/os-release ID=cachyos (not Ubuntu host)" if native else "Unexpected guest /etc/os-release")
        if not native: raise ValueError("Not running inside CachyOS")
        # No host file exposure: QEMU passes a single explicitly labeled FAT disk.
        serial=subprocess.run(["lsblk","-dn","-o","SERIAL","/dev/vda"],
                              capture_output=True,text=True,timeout=10)
        disk_ok=(serial.returncode==0 and serial.stdout.strip()=="DEVNETCONTROL")
        check(out,"control_disk_identity","PASS" if disk_ok else "FAIL",
              "Expected disposable DEVNETCONTROL virtio disk only")
        if not disk_ok:raise ValueError("Unrecognized FAT disk; refusing to run")
        digest=hash_file(p)
        check(out,"exact_sha256","PASS" if digest==expected else "FAIL",
              "Observed: "+digest)
        if digest!=expected:raise ValueError("Wrong application archive hash")
        with zipfile.ZipFile(p) as z:
            infos=z.infolist()
            if not infos:raise ValueError("Empty ZIP")
            total=sum(i.file_size for i in infos)
            if total>MAX_SIZE or len(infos)>10000:raise ValueError("Unsafe unpack size/count")
            seen=set()
            for entry in infos:
                name=entry.filename
                if name in seen or name.startswith(("/","\\")) or "\\" in name or ".." in PurePosixPath(name).parts or stat.S_ISLNK(entry.external_attr>>16):
                    raise ValueError("Unsafe path/link/duplicate ZIP member: "+name)
                seen.add(name)
            bad=z.testzip()
            if bad is not None:raise ValueError("ZIP CRC error: "+bad)
            check(out,"zip_integrity","PASS",f"{len(infos)} members, CRC checked")
            ver=[x for x in infos if x.filename.endswith("/VERSION") or x.filename=="VERSION"]
            versions=[]
            for info in ver:
                if info.file_size<200:
                    versions.append(z.read(info).decode("utf-8","replace").strip())
            if not versions or version not in versions:
                check(out,"package_version","FAIL",repr(versions))
                raise ValueError("VERSION not found or mismatches expected")
            check(out,"package_version","PASS",repr(versions))
            counts={"python":0,"bash":0,"json":0,"xml":0}
            syntax_errors=[]
            for info in infos:
                if info.is_dir() or info.file_size>2*1024*1024:continue
                name=info.filename.lower()
                if name.endswith(".py"):
                    counts["python"]+=1
                    try:ast.parse(z.read(info),filename=info.filename)
                    except Exception as exc:syntax_errors.append(f"{info.filename}: {exc}")
                if name.endswith(".sh"):
                    counts["bash"]+=1
                    chk=subprocess.run(["bash","-n"],input=z.read(info),
                                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
                    if chk.returncode:syntax_errors.append(f"{info.filename}: bash -n failed")
                if name.endswith(".json"):
                    counts["json"]+=1
                    try:json.loads(z.read(info))
                    except Exception as exc:syntax_errors.append(f"{info.filename}: {exc}")
            check(out,"native_syntax","FAIL" if syntax_errors else "PASS",
                  f"{counts}; errors={syntax_errors[:6]}")
            if syntax_errors:raise ValueError("Syntax problems")
            workspace=Path(tempfile.mkdtemp(prefix="devnet-vm-",dir="/var/tmp"))
            z.extractall(workspace)
            roots=sorted({x.split("/",1)[0] for x in z.namelist() if x and "/" in x})
            pkgroot=workspace/roots[0] if len(roots)==1 and (workspace/roots[0]).is_dir() else workspace
            eligible=sorted(x for x in pkgroot.glob("tests/test*") if x.is_file() and x.suffix in (".sh",".py"))
            check(out,"tests_discovery","PASS" if eligible else "NOT_TESTED",
                  f"{len(eligible)} packaged shell/Python tests")
        # Refuse executing test code as root. Only unprivileged process, no host mounts or network.
        if eligible and not shutil.which("runuser"):
            check(out,"packaged_tests","NOT_TESTED","runuser absent; not executed as root")
        elif eligible:
            unpriv=pwd.getpwnam("nobody")
            tmp_home=Path(tempfile.mkdtemp(prefix="devnet-nobody-",dir="/var/tmp"))
            os.chown(tmp_home,unpriv.pw_uid,unpriv.pw_gid)
            os.chown(workspace,unpriv.pw_uid,unpriv.pw_gid)
            for root,dirs,files in os.walk(workspace):
                for name in dirs+files:
                    item=Path(root)/name
                    if not item.is_symlink():
                        os.chown(item,unpriv.pw_uid,unpriv.pw_gid)
            statuses=[]
            for test in eligible[:MAX_TESTS]:
                if test.suffix==".sh":argv=["bash",str(test)]
                else:argv=["python3",str(test)]
                env=dict(os.environ)
                env.update({"HOME":str(tmp_home),"TMPDIR":str(tmp_home),
                            "XDG_CONFIG_HOME":str(tmp_home/".config"),
                            "XDG_DATA_HOME":str(tmp_home/".local/share"),
                            "DEVNET_QA_VM":"1"})
                try:
                    result=subprocess.run(["runuser","-u","nobody","--","env",
                                           *[f"{k}={v}" for k,v in env.items()],
                                           *argv],cwd=pkgroot,capture_output=True,
                                          text=True,errors="replace",timeout=110)
                    status="PASS" if result.returncode==0 else "FAIL"
                    detail=f"exit={result.returncode}"
                    output=(result.stdout+"\n"+result.stderr)[-12000:]
                except subprocess.TimeoutExpired as exc:
                    status="FAIL";detail="timeout=110s";output=str(exc)
                out["tests"].append({"test":str(test.relative_to(pkgroot)),
                                     "status":status,"detail":detail})
                with logfile.open("a") as f:
                    f.write(f"\n=== {test.relative_to(pkgroot)} : {status} {detail} ===\n")
                    f.write(output+"\n")
                statuses.append(status)
            if len(eligible)>MAX_TESTS:
                check(out,"packaged_tests","NOT_TESTED","Test count exceeded safety limit")
            else:
                check(out,"packaged_tests","PASS" if all(x=="PASS" for x in statuses) else "FAIL",
                      f"PASS={statuses.count('PASS')}, FAIL={statuses.count('FAIL')}")
        else:
            check(out,"packaged_tests","NOT_TESTED","No packaged Python/Bash test runner")
        check(out,"installation_upgrade_rollback","NOT_TESTED","Not run on live ISO; needs separate disposable installed system")
        check(out,"kde_gui_hardware","NOT_TESTED","No device passthrough or GUI interaction")
    except Exception as exc:
        check(out,"harness","FAIL",repr(exc)[:400])
    statuses=[x["status"] for x in out["checks"].values()]
    out["overall"]="FAIL" if "FAIL" in statuses else "PARTIAL"
    report.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"overall":out["overall"],"checks":out["checks"],"tests":out["tests"]},sort_keys=True))
    return 0 if out["overall"]!="FAIL" else 1

if __name__=="__main__":
    raise SystemExit(main())
