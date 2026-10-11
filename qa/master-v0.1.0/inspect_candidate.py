#!/usr/bin/env python3
"""Pre-install, non-executing review of ORIGINAL Devnet release ZIP (QA-only)."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

def sha256(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(1048576),b""):h.update(part)
    return h.hexdigest()

def main():
    if len(sys.argv)!=5:
        raise SystemExit("usage: inspect_candidate.py ZIP EXPECTED_SHA APP_ID REPORT")
    p=Path(sys.argv[1]);expected=sys.argv[2].lower();app=sys.argv[3];dest=Path(sys.argv[4])
    report={"format":"devnet-master-qa-inventory-v0.1.0","app":app,
        "archive_name":p.name,"sha256_expected":expected,"checks":{},
        "install_candidates":[],"uninstall_candidates":[],"service_units":[],
        "desktop_files":[],"packaged_tests":[],"versions":[],
        "static_risk_signals":{},"installer_source_review":"NOT_TESTED",
        "clean_install":"NOT_TESTED","upgrade":"NOT_TESTED",
        "rollback":"NOT_TESTED","uninstall":"NOT_TESTED",
        "gui":"NOT_TESTED","physical_hardware":"NOT_TESTED",
        "master_release_approval":"BLOCKED"}
    try:
        actual=sha256(p)
        report["sha256_observed"]=actual
        if actual!=expected:raise ValueError("Original ZIP digest mismatch")
        report["checks"]["exact_archive"]="PASS"
        with zipfile.ZipFile(p) as z:
            entries=z.infolist()
            if not entries or len(entries)>10000 or sum(i.file_size for i in entries)>64*1024*1024:
                raise ValueError("Unsafe archive size/count")
            seen=set()
            for entry in entries:
                n=entry.filename
                path=PurePosixPath(n)
                if n in seen or not n or n.startswith(("/", "\\")) or "\\" in n or ".." in path.parts or stat.S_ISLNK(entry.external_attr>>16):
                    raise ValueError("Unsafe member path/symlink/duplicate")
                seen.add(n)
            if z.testzip():raise ValueError("ZIP member CRC failed")
            report["checks"]["zip_safety_crc"]="PASS"
            for entry in entries:
                if entry.is_dir():continue
                name=entry.filename
                base=PurePosixPath(name).name.lower()
                parts=[x.lower() for x in PurePosixPath(name).parts]
                if base in ("install.sh","installer.sh","setup.sh","install.py","setup.py") or base.startswith("install-") and base.endswith(".sh"):
                    report["install_candidates"].append(name)
                if base in ("uninstall.sh","remove.sh","uninstaller.sh","uninstall.py") or base.startswith("uninstall-") and base.endswith(".sh"):
                    report["uninstall_candidates"].append(name)
                if base.endswith(".service"):report["service_units"].append(name)
                if base.endswith(".desktop"):report["desktop_files"].append(name)
                if len(parts)>=2 and "tests" in parts and (base.endswith((".py",".sh"))):
                    report["packaged_tests"].append(name)
                if base=="version" and entry.file_size<256:
                    report["versions"].append({"path":name,"value":z.read(entry).decode("utf-8","replace").strip()[:80]})
            # Report ONLY category counts; never report sensitive matched content.
            categories={
                "network_download_commands":r"\b(curl|wget|git\s+clone)\b",
                "system_service_changes":r"\bsystemctl\b|\bservice\b",
                "package_manager_commands":r"\b(pacman|paru|yay|apt-get|pip)\b",
                "root_or_sudo_commands":r"\bsudo\b|\bsu\s+-\b",
                "destructive_commands":r"\brm\s+-[A-Za-z]*[rf]|\bmkfs\b|\bdd\s+if=",
                "url_literals":r"https?://",
                "credential_key_words":r"(?i)(?:api[_-]?key|secret|password|token|private[_-]?key)"
            }
            counts={k:0 for k in categories}
            for entry in entries:
                n=entry.filename.lower()
                if entry.is_dir() or entry.file_size>512000 or not n.endswith((".sh",".py",".service",".desktop",".conf",".json",".md",".txt")):continue
                data=z.read(entry).decode("utf-8","replace")
                for k,pattern in categories.items():
                    counts[k]+=len(re.findall(pattern,data))
            report["static_risk_signals"]=counts
            report["member_count"]=len(entries)
            report["checks"]["inventory"]="PASS"
        report["ready_for_install_plan"]="REVIEW_REQUIRED"
    except Exception as exc:
        report["checks"]["inventory"]="FAIL"
        report["error_type"]=type(exc).__name__
        report["error_message"]=str(exc)[:180]
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))
    return 1 if "FAIL" in report["checks"].values() else 0

if __name__=="__main__":raise SystemExit(main())
