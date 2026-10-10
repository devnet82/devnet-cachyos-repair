#!/usr/bin/env python3
"""Read-only Devnet portfolio package audit. No host installs or hardware claims."""
from __future__ import annotations
import hashlib, json, os, re, stat, subprocess, sys, tempfile, time, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

APPS = {
 "devnet-cachyos-repair": ("cachyos-repair-qa-assets-v0.1.19", "devnet-cachyos-repair-v0.1.19.zip", "435bc2a88a99eef4cd5e85d71d50ca36e3d3f40361efe53db85e57e2d20fea0c"),
 "devnet-rgb-control": ("v8.8", "devnet-rgb-control-v8.8.zip", "92ad889e178291ea07241095ea683524d5b7d677375bf02b03467df464209b00"),
 "vr-stack-control": ("v0.6.85", "vr-stack-control-v0.6.85.zip", "db9af6ff47f3abcf07cf452ddd91e91cbd75a10296c0c6050bb5c612980d9cf3"),
 "devnet-wayvr-watch-manager": None,
 "devnet-chatbox": None,
 "devnet-proton-rtsp": None,
 "wivrn-stack-control": None,
}
PINNED_OTHER_BUILDS = {
 "devnet-cachyos-repair": "v0.1.20 tested VM candidate, not on main or permanent Release",
 "devnet-rgb-control": "v8.9 ZIP in Project Library, not checked out by CI",
 "vr-stack-control": "v0.6.129 ZIP in Project Library, not checked out by CI",
 "devnet-wayvr-watch-manager": "v0.1.33 was used on Quest; current GitHub main is v0.1.14",
 "devnet-chatbox": "v0.1.3.131 GTK ZIP in Project Library; GitHub repo empty",
 "devnet-proton-rtsp": "v1.76 test ZIP in Project Library; GitHub repo empty",
 "wivrn-stack-control": "GitHub repository has no source",
}
def cmd(argv, cwd=None, timeout=180, env=None):
    try:
        p=subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True,
                         errors="replace", timeout=timeout, check=False)
        return p.returncode, (p.stdout+"\n"+p.stderr)[-10000:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 124, str(exc)

def zip_verification(path:Path):
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        names=set()
        total=0
        for item in members:
            name=item.filename
            parts=Path(name).parts
            if name.startswith("/") or ".." in parts or "\\" in name or name in names:
                return False, "Unsafe or duplicate member "+name[:120]
            names.add(name)
            total+=item.file_size
            if len(names)>25000 or total>1_000_000_000 or stat.S_ISLNK(item.external_attr >> 16):
                return False,"Unsafe size or member"
        bad=z.testzip()
        if bad:return False,"CRC failure: "+bad
        return True,f"{len(members)} ZIP members, CRC/safe-member PASS"

def main():
    if len(sys.argv)!=3 or sys.argv[1] not in APPS:
        raise SystemExit("Usage: portfolio_qa.py <known_repo> <evidence_dir>")
    app=sys.argv[1]; evidence=Path(sys.argv[2]); evidence.mkdir(parents=True,exist_ok=True)
    report={"qa_version":"0.1.0","repository":"devnet82/"+app,"scope":"Ubuntu CI package/static audit only",
            "source_revision":None,"checks":{},"logs":{},"known_other_build":PINNED_OTHER_BUILDS[app],
            "hardware_acceptance":"NOT_TESTED","vm_acceptance":"NOT_TESTED"}
    def mark(key,state,note):
        assert state in ("PASS","FAIL","NOT_TESTED")
        report["checks"][key]={"status":state,"evidence":str(note)[:650]}
    with tempfile.TemporaryDirectory(prefix="devnet-portfolio-") as tmp:
        root=Path(tmp)/app
        rc,out=cmd(["git","clone","--quiet","--depth","1","https://github.com/devnet82/"+app+".git",str(root)],timeout=100)
        report["logs"]["checkout"]=out[-1200:]
        if rc!=0:
            mark("clone_repository","FAIL",f"Git clone exit {rc}: {out[:300]}")
            mark("source_available","NOT_TESTED","Repository could not be checked out")
        else:
            mark("clone_repository","PASS","Public repository cloned read-only")
            rc,out=cmd(["git","rev-parse","HEAD"],cwd=root)
            report["source_revision"]=out.strip() if rc==0 else None
            entries=[p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
            has_source=any(p.name in ("install.sh","uninstall.sh") or p.suffix==".py" or
                           "bin" in p.parts or "app" in p.parts or "tests" in p.parts for p in entries)
            if not has_source:
                mark("source_available","NOT_TESTED","No testable application source in repository default branch")
            else:
                mark("source_available","PASS",f"{len(entries)} checked-out files, commit {report['source_revision']}")
                bad=[]; counts={"bash":0,"python":0,"xml":0,"json":0}
                for f in entries:
                    if f.stat().st_size>2_000_000:continue
                    src=f.read_bytes()
                    first=src.split(b"\n",1)[0]
                    if f.suffix==".py" or first.startswith(b"#!/usr/bin/env python"):
                        counts["python"]+=1
                        try:compile(src, str(f), "exec")
                        except (SyntaxError,ValueError) as e:bad.append(f"{f.relative_to(root)}: {e}")
                    if f.suffix==".sh" or first.startswith(b"#!/usr/bin/env bash") or first.startswith(b"#!/bin/bash"):
                        counts["bash"]+=1
                        rc,_=cmd(["bash","-n",str(f)],timeout=15)
                        if rc:bad.append(f"bash -n {f.relative_to(root)} (exit {rc})")
                    if f.suffix in (".xml",".svg"):
                        counts["xml"]+=1
                        try:ET.fromstring(src)
                        except ET.ParseError as e:bad.append(f"XML {f.relative_to(root)}: {e}")
                    if f.suffix==".json":
                        counts["json"]+=1
                        try:json.loads(src)
                        except (ValueError,UnicodeDecodeError) as e:bad.append(f"JSON {f.relative_to(root)}: {e}")
                if bad:
                    mark("static_syntax","FAIL","; ".join(bad[:8]))
                else:
                    mark("static_syntax","PASS","Checked "+str(counts))
                z=Path(tmp)/"source.zip"
                rc,out=cmd(["git","archive","--format=zip","-o",str(z),"HEAD"],cwd=root,timeout=45)
                if rc or not z.is_file():
                    mark("source_archive_integrity","FAIL","git archive exit "+str(rc))
                else:
                    try:
                        good,msg=zip_verification(z)
                        mark("source_archive_integrity","PASS" if good else "FAIL",msg)
                    except (OSError,zipfile.BadZipFile) as e:mark("source_archive_integrity","FAIL",str(e))
                suite=None
                if app=="devnet-rgb-control" and (root/"tests/test-package.sh").is_file():
                    suite=["bash","tests/test-package.sh"]
                elif app=="devnet-wayvr-watch-manager" and (root/"tests/test_all.py").is_file():
                    suite=["python3","tests/test_all.py"]
                if suite:
                    rc,out=cmd(suite,cwd=root,timeout=320,env=dict(os.environ,HOME=str(Path(tmp)/"home"),XDG_CONFIG_HOME=str(Path(tmp)/"home/.config")))
                    report["logs"]["package_test"]=out
                    mark("packaged_regression_suite","PASS" if rc==0 else "FAIL",f"{' '.join(suite)} exit {rc}; see logs")
                else:
                    mark("packaged_regression_suite","NOT_TESTED","No safe pre-existing package test suite selected for this repository")
        release=APPS[app]
        if release:
            tag,archive,sha=release
            download_dir=Path(tmp)/"release";download_dir.mkdir(exist_ok=True)
            rc,out=cmd(["gh","release","download",tag,"--repo","devnet82/"+app,"--pattern",archive,
                        "--dir",str(download_dir)],timeout=180)
            f=download_dir/archive
            if rc or not f.is_file():
                mark("published_release_zip","FAIL",f"Could not download declared release ({rc}): {out[:280]}")
            else:
                actual=hashlib.sha256(f.read_bytes()).hexdigest()
                try:good,msg=zip_verification(f)
                except (OSError,zipfile.BadZipFile) as e:good,msg=False,str(e)
                mark("published_release_zip","PASS" if good and actual==sha else "FAIL",
                     f"{archive}, expected sha256 {sha}, actual {actual}, {msg}")
        else:
            mark("published_release_zip","NOT_TESTED","No release asset available in GitHub for this application")
    statuses=[z["status"] for z in report["checks"].values()]
    report["source_package_gate"]="FAIL" if "FAIL" in statuses else "INCOMPLETE" if "NOT_TESTED" in statuses else "PASS"
    report["master_release_gate"]="BLOCKED"
    output=evidence/(app+".json")
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    for k,val in report["checks"].items():
        print(f"{app} {k}: {val['status']} | {val['evidence']}")
    print(app,"source package gate:",report["source_package_gate"])
    print("MASTER_QA_100_PERCENT_BLOCKED: hardware, VM, rollback, migration, and newer build evidence are separate")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
