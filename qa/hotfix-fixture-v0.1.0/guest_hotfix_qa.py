#!/usr/bin/env python3
"""Hotfix upgrade/rollback fixture QA in disposable installed CachyOS.

Runs as an unprivileged user with an isolated HOME. Does not assert
full prior application binary/hardware acceptance: baselines are *fixtures*
faithfully exercising the update contract from the original packaged tests.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""):h.update(b)
    return h.hexdigest()

def call(argv,root,home,extra=None):
    env=dict(os.environ)
    env.update({"HOME":str(home),"XDG_CONFIG_HOME":str(home/".config"),
                "XDG_DATA_HOME":str(home/".local/share"),
                "DEVNET_TEST_HOME":str(home),"LC_ALL":"C",
                "DEVNET_QA_VM":"1"})
    if extra:env.update(extra)
    try:
        p=subprocess.run(argv,cwd=root,env=env,capture_output=True,
                         text=True,errors="replace",timeout=100)
        return p.returncode, (p.stdout+"\n"+p.stderr)[-4000:]
    except subprocess.TimeoutExpired:return 124,"timeout"

def require(condition,message):
    if not condition:raise AssertionError(message)

def prepare_vr(home,ver):
    p=home/".local/bin";p.mkdir(parents=True,exist_ok=True)
    gui=p/"vr-control-gui";doctor=p/"vr-doctor"
    gui.write_text("#!/usr/bin/env python3\nimport sys\nAPP_VERSION = \""+ver+"\"\nif '--version' in sys.argv:print(APP_VERSION)\n")
    doctor.write_text("#!/usr/bin/env python3\nVERSION = \""+ver+"\"\nprint('VR Stack Control Doctor '+VERSION)\n")
    gui.chmod(0o755);doctor.chmod(0o755)
    return gui,doctor

def test_vr(package,home,report):
    base="v0.6.131"
    gui,doctor=prepare_vr(home,base)
    old=(sha(gui),sha(doctor))
    rc,detail=call(["bash","install.sh"],package,home)
    require(rc==0,"upgrade from fixture baseline failed: "+detail)
    require('APP_VERSION = "v0.6.132"' in gui.read_text(),"GUI version not updated")
    require('VERSION = "v0.6.132"' in doctor.read_text(),"Doctor version not updated")
    backups=list((home/".local/share/vr-stack-control/backups").glob("v0.6.132-*"))
    require(len(backups)==1,"upgrade backup missing/ambiguous")
    report["checks"]["fixture_upgrade"]="PASS"
    before=(sha(gui),sha(doctor))
    rc,detail=call(["bash","install.sh"],package,home)
    require(rc==0 and "already installed" in detail and before==(sha(gui),sha(doctor)),"idempotent rerun failed: "+detail)
    require(len(list((home/".local/share/vr-stack-control/backups").glob("v0.6.132-*")))==1,"idempotency created extra backup")
    report["checks"]["idempotent_reinstall"]="PASS"
    rc,detail=call(["bash","uninstall.sh"],package,home)
    require(rc==0 and old==(sha(gui),sha(doctor)),"baseline rollback failed: "+detail)
    report["checks"]["fixture_application_rollback"]="PASS"
    rc,detail=call(["bash","install.sh"],package,home,{"DEVNET_VRSTACK_TEST_FAIL_AFTER_GUI":"1"})
    require(rc!=0 and old==(sha(gui),sha(doctor)),"injected interrupted upgrade did not restore fixture baseline")
    report["checks"]["interrupted_upgrade_recovery"]="PASS"
    gui.write_text(gui.read_text().replace(base,"v0.6.99"))
    doctor.write_text(doctor.read_text().replace(base,"v0.6.99"))
    original=(sha(gui),sha(doctor))
    rc,detail=call(["bash","install.sh"],package,home)
    require(rc!=0 and original==(sha(gui),sha(doctor)),"unsupported baseline not rejected safely")
    report["checks"]["unsupported_baseline_protection"]="PASS"

def prepare_wayvr(home,ver):
    p=home/".local/share/devnet-wayvr-watch-manager"
    c=home/".config/devnet-wayvr-watch-manager"
    p.mkdir(parents=True,exist_ok=True);c.mkdir(parents=True,exist_ok=True)
    (p/"doctor.py").write_text(
        'from dataclasses import dataclass\nAPP_VERSION = "'+ver+'"\n'
        '@dataclass\nclass Check:\n    level: str\n    name: str\n    detail: str\n'
        'def make_headset_only(): return Check("FAIL", "Metrics bridge output", "missing write command(s): headset")\n'
        'def make_controller_failure(): return Check("FAIL", "Metrics bridge output", "missing write command(s): left controller")\n')
    (p/"watchlib.py").write_text('APP_VERSION = "'+ver+'"\n')
    (p/"metrics.py").write_text('APP_VERSION = "0.1.31"\n# DEVNET_V0131_SUPPRESS_CUSTOM_HMD_RUNTIME\n')
    (p/"watch.xml").write_text('<!-- DEVNET_WAYVR_WATCH_MANAGER -->\n<watch><text id="devnet_quest_left_battery"/><text id="devnet_quest_right_battery"/></watch>\n')
    (c/"state.json").write_text(json.dumps({"installed_version":ver})+"\n")
    return p,c

def test_wayvr(package,home,report):
    base="0.1.33"
    p,c=prepare_wayvr(home,base)
    original={n:sha(p/n) for n in ("doctor.py","watchlib.py","metrics.py","watch.xml")}
    rc,detail=call(["bash","install.sh","--yes"],package,home)
    require(rc==0,"upgrade from v0.1.33 fixture baseline failed: "+detail)
    require('APP_VERSION = "0.1.34"' in (p/"doctor.py").read_text(),"Doctor version mismatch")
    require('APP_VERSION = "0.1.34"' in (p/"watchlib.py").read_text(),"watchlib version mismatch")
    require(original["metrics.py"]==sha(p/"metrics.py") and original["watch.xml"]==sha(p/"watch.xml"),"protected watch/metrics were changed")
    namespace={}
    exec(compile((p/"doctor.py").read_text(),str(p/"doctor.py"),"exec"),namespace)
    require(namespace["make_headset_only"]().level=="PASS","headset expected suppression rejected")
    require(namespace["make_controller_failure"]().level=="FAIL","controller failure incorrectly suppressed")
    report["checks"]["fixture_upgrade"]="PASS"
    report["checks"]["doctor_regression_and_protected_files"]="PASS"
    before={n:sha(p/n) for n in ("doctor.py","watchlib.py","metrics.py","watch.xml")}
    num=len(list((c/"backups").glob("*")))
    rc,detail=call(["bash","install.sh","--yes"],package,home)
    require(rc==0 and len(list((c/"backups").glob("*")))==num,"idempotent upgrade made unexpected backups: "+detail)
    require(all(before[n]==sha(p/n) for n in before),"idempotent upgrade changed files")
    report["checks"]["idempotent_reinstall"]="PASS"
    rc,detail=call(["bash","uninstall.sh"],package,home)
    require(rc==0,"rollback command failed: "+detail)
    require(all(original[n]==sha(p/n) for n in original),"rollback changed protected or baseline files")
    require(json.loads((c/"state.json").read_text())["installed_version"]==base,"state rollback failed")
    report["checks"]["fixture_application_rollback"]="PASS"
    rc,detail=call(["bash","install.sh","--yes"],package,home,{"DEVNET_WAYVR_TEST_FAIL_AFTER_DOCTOR":"1"})
    require(rc!=0 and all(original[n]==sha(p/n) for n in original),"injected failure did not restore baseline")
    report["checks"]["interrupted_upgrade_recovery"]="PASS"
    (p/"doctor.py").write_text((p/"doctor.py").read_text().replace(base,"0.1.30"))
    (p/"watchlib.py").write_text((p/"watchlib.py").read_text().replace(base,"0.1.30"))
    old=(sha(p/"doctor.py"),sha(p/"watchlib.py"))
    rc,detail=call(["bash","install.sh","--yes"],package,home)
    require(rc!=0 and old==(sha(p/"doctor.py"),sha(p/"watchlib.py")),"unsupported baseline wrongly accepted")
    report["checks"]["unsupported_baseline_protection"]="PASS"

def main():
    if len(sys.argv)!=6:raise SystemExit("usage: script APP ZIP SHA HOME REPORT")
    app,archive,sha256,home,reportfile=sys.argv[1:]
    archive=Path(archive);home=Path(home);reportfile=Path(reportfile)
    d={"schema":"devnet-installed-cachyos-hotfix-fixtures-v0.1.0",
       "app":app,"expected_archive_sha256":sha256,"checks":{},
       "baseline_type":"SYNTHETIC_FIXTURE_FROM_ORIGINAL_PACKAGE_TESTS",
       "actual_previously_installed_app_upgrade":"NOT_TESTED",
       "physical_hardware":"NOT_TESTED","GUI_runtime":"NOT_TESTED",
       "full_clean_install":"NOT_APPLICABLE_UPDATE_ONLY","release_approval":"BLOCKED"}
    try:
        require("ID=cachyos" in Path("/etc/os-release").read_text(),"not native CachyOS")
        require(subprocess.run(["findmnt","-no","FSTYPE","/"],capture_output=True,text=True).stdout.strip()=="btrfs","not installed BTRFS")
        d["checks"]["native_installed_cachyos_btrfs"]="PASS"
        require(sha(archive)==sha256,"original candidate hash mismatch")
        d["checks"]["exact_original_archive"]="PASS"
        with zipfile.ZipFile(archive) as z:
            require(z.testzip() is None,"ZIP corruption")
            members=z.infolist()
            require(all(not x.filename.startswith(("/","\\")) and ".." not in Path(x.filename).parts for x in members),"Unsafe ZIP path")
            z.extractall(home/"package")
        package=home/"package"/next(x.name for x in (home/"package").iterdir() if x.is_dir())
        if app=="vr_stack":test_vr(package,home,d)
        elif app=="wayvr":test_wayvr(package,home,d)
        else:raise RuntimeError("Unsupported app")
    except Exception as exc:
        d["checks"]["hotfix_lifecycle"]="FAIL"
        d["error"]=str(exc)[:300]
    reportfile.parent.mkdir(parents=True,exist_ok=True)
    reportfile.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"app":app,"checks":d["checks"],"baseline_type":d["baseline_type"]},sort_keys=True))
    return 1 if "FAIL" in d["checks"].values() else 0

if __name__=="__main__":raise SystemExit(main())
