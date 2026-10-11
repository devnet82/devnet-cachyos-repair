#!/usr/bin/env python3
"""Strict stage gate for preserved installed CachyOS app lifecycle evidence.

DO NOT infer app installation success from GitHub job conclusion or BTRFS reboot.
QA-only v0.1.1; doesn't execute downloaded software or modify releases.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

def classify(app,log,status):
    if status=="PASS":return "PASS"
    if "OpenRGB is not installed" in log:return "BLOCKED_ENVIRONMENT_OPENRGB"
    if "sudo: a terminal is required" in log or "sudo: a password is required" in log:
        return "BLOCKED_ENVIRONMENT_PRIVILEGES_DEPENDENCIES"
    if "VRChat Proton prefix/Tools folder was not found" in log:
        return "BLOCKED_ENVIRONMENT_STEAM_PREFIX"
    if "vr-control-gui not found" in log or "doctor.py" in log:
        return "PACKAGE_OR_INSTALLER_FAILURE"
    if status=="NOT_TESTED":return "NOT_TESTED"
    return "INSTALLATION_FAILURE_UNCLASSIFIED"

def gate(folder,app):
    folder=Path(folder)
    src=json.loads((folder/"app-lifecycle-result.json").read_text())
    log=(folder/"app-lifecycle.log").read_text(errors="replace")
    if src.get("format")!="devnet-installed-lifecycle-v0.1.0":
        raise ValueError("Unexpected guest report schema")
    if src.get("app")!=app:
        raise ValueError("Report app identity mismatch")
    c=src.get("checks",{})
    def passed(name):return c.get(name,{}).get("status")=="PASS"
    root={k:passed(k) for k in ("isolated_installed_cachyos","original_zip","package_checksum_and_unzip")}
    rollback=(folder/"app-snapshot-rollback.txt").read_text().strip()=="APP_BTRFS_SNAPSHOT_ROLLBACK_PASS"
    reboot="INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS" in (folder/"installed-restored-pass.txt").read_text()
    install=c.get("clean_install",{}).get("status","NOT_TESTED")
    uninstall=c.get("uninstall",{}).get("status","NOT_TESTED")
    classified=classify(app,log,install)
    candidate_lifecycle_pass=all(root.values()) and rollback and reboot and install=="PASS" and uninstall=="PASS"
    result={"gate":"devnet-master-qa-strict-installed-v0.1.1","app":app,
        "native_installed_verified":all(root.values()),
        "checks":root,
        "guest_btrfs_snapshot_rollback":"PASS" if rollback and reboot else "FAIL",
        "app_clean_install":install,
        "app_uninstall":uninstall,
        "installation_classification":classified,
        "app_upgrade":"NOT_TESTED","app_internal_rollback":"NOT_TESTED",
        "gui_tray":"NOT_TESTED","physical_hardware":"NOT_TESTED",
        "candidate_lifecycle_gate":"PASS" if candidate_lifecycle_pass else "BLOCKED",
        "master_qa_release_approval":"BLOCKED"}
    return result

def main():
    if len(sys.argv)!=4:raise SystemExit("usage: strict_gate.py EVIDENCE_DIR APP OUTPUT_JSON")
    result=gate(Path(sys.argv[1]),sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True))
    if result["candidate_lifecycle_gate"]!="PASS":
        print("QA BLOCKED: completed VM workflow is NOT proof of successful application installation",file=sys.stderr)
        return 1
    return 0

if __name__=="__main__":raise SystemExit(main())
