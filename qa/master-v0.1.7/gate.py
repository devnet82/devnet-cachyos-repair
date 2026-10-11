#!/usr/bin/env python3
"""Devnet Master QA v0.1.7: fail-closed evidence gate; NEVER executes apps.

Accepts only reports from pinned, original QA runs. Each application's evidence
is placed under EVIDENCE_ROOT/APP_ID/{native,inventory,installed,strict}/.
Original ZIPs are OPTIONAL inputs for a re-hash, but are NEVER repackaged.
No implicit PASS from a GitHub workflow's green conclusion.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION="0.1.7"
STATES={"PASS","FAIL","NOT_TESTED"}
CHECKS=[
 "archive_integrity","native_cachyos_package_tests","installed_grub_btrfs",
 "clean_install","uninstall","upgrade_from_known_good","application_rollback",
 "configuration_migration","gui_tray_single_instance","doctor_self_check",
 "service_process_lifecycle","failure_and_recovery","network_offline_reconnect",
 "permissions_low_disk_corrupt_inputs","regression_coverage","hardware_portability",
 "security_destructive_guards","physical_hardware_acceptance"
]
NATIVE_CHECKS=(
 "native_cachyos","control_disk_identity","exact_sha256",
 "zip_integrity","package_version","native_syntax","packaged_tests"
)
INSTALL_CHECKS=("isolated_installed_cachyos","original_zip","package_checksum_and_unzip")

def load(path):
    """Only caller-supplied report paths; reject symlinks and duplicate JSON keys."""
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>8*1024*1024:
        raise ValueError("missing/unsafe evidence: "+str(p))
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError("duplicate JSON key: "+k)
            out[k]=v
        return out
    result=json.loads(p.read_text(encoding="utf-8"),object_pairs_hook=unique)
    if not isinstance(result,dict):raise ValueError("JSON report must be an object")
    return result

def check_status(report,key):
    return report.get("checks",{}).get(key,{}).get("status","NOT_TESTED")

def set_check(result,key,status,proof):
    if status not in STATES:raise ValueError("invalid evidence status "+repr(status))
    result["checks"][key]={"status":status,"evidence":proof}

def hash_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    return h.hexdigest()

def proven_file(root,app,section,file):
    return root/app/section/file

def evaluate(c,root):
    app=c["id"]
    a={"id":app,"application":c["name"],"version":c["version"],
       "repository":c.get("repo"),"checks":{},"evidence_runs":{},
       "master_qa_release_approval":"BLOCKED"}
    for requirement in CHECKS:set_check(a,requirement,"NOT_TESTED","no complete verified evidence")
    if c.get("original_unuploaded"):
        a["note"]="Private-content review in prior session is not a native CachyOS installed test; ZIP remains unuploaded"
        return a
    if c.get("hardware_specific"):
        a["note"]="Sonic Pad physical-device testing cannot be substituted by desktop VM"
        return a
    if "native" not in c:
        if c.get("platform_vm"):
            a["evidence_runs"]["platform_vm"]=c["platform_vm"]["run"]
            a["note"]="Existing GRUB/BTRFS recovery smoke covers platform only, not candidate lifecycle"
        return a

    # Four immutable historical artifact groups, downloaded by app-local workflow.
    for section in ("native","inventory","installed","strict"):
        a["evidence_runs"][section]=c[section]["run"]
    native_path=proven_file(root,app,"native","qa-result.json")
    inventory_path=proven_file(root,app,"inventory","installation-inventory.json")
    installed_path=proven_file(root,app,"installed","app-lifecycle-result.json")
    strict_path=proven_file(root,app,"strict","strict-gate-result.json")

    if native_path.is_file():
        native=load(native_path)
        if not str(native.get("format","")).startswith("devnet-native-cachyos-vm-qa-v0.1."):
            raise ValueError(app+": invalid original native report schema")
        if native.get("expected_version")!=c["version"]:
            raise ValueError(app+": native report expected version differs")
        testrows=native.get("tests",[])
        if not isinstance(testrows,list) or len(testrows)!=c["native"]["packaged_tests"]:
            raise ValueError(app+": packaged regression test count differs")
        if len({x.get("test") for x in testrows})!=len(testrows):
            raise ValueError(app+": duplicate test names")
        ok=all(check_status(native,k)=="PASS" for k in NATIVE_CHECKS) and all(
            x.get("status")=="PASS" and x.get("detail","").startswith("exit=0") for x in testrows)
        # Old/native reports intentionally have release_decision BLOCKED.
        if native.get("release_decision")!="BLOCKED":
            raise ValueError(app+": unsafe release decision in native report")
        set_check(a,"native_cachyos_package_tests","PASS" if ok else "FAIL",
                  f"native CachyOS run {c['native']['run']}, {len(testrows)} packaged entries")
        digest_match=c["sha256"] in check_detail(native,"exact_sha256")
        if not digest_match:raise ValueError(app+": native package hash evidence mismatch")
    if inventory_path.is_file():
        inv=load(inventory_path)
        if inv.get("format")!="devnet-master-qa-inventory-v0.1.0" or inv.get("app")!=c["guest_app"]:
            raise ValueError(app+": inventory schema or app identity mismatched")
        if inv.get("archive_name")!=c["archive"] or inv.get("sha256_expected")!=c["sha256"] or inv.get("sha256_observed")!=c["sha256"]:
            raise ValueError(app+": original archive identity/digest mismatch")
        good=all(check_status(inv,k)=="PASS" for k in ("exact_archive","zip_safety_crc","inventory"))
        set_check(a,"archive_integrity","PASS" if good else "FAIL",f"exact archived ZIP inventory run {c['inventory']['run']}")

    # Optional direct rehash of draft ZIP downloaded in own repository job.
    original=root/app/"candidate.zip"
    if original.is_file():
        if original.is_symlink() or original.name!=c["archive"] and not original.name=="candidate.zip":
            raise ValueError(app+": unsafe candidate path")
        observed=hash_file(original)
        if observed!=c["sha256"]:raise ValueError(app+": candidate ZIP bytes changed")
        # Must also have independently corroborating inventory/native evidence.
        if check(a,"archive_integrity")!="PASS" or check(a,"native_cachyos_package_tests")!="PASS":
            raise ValueError(app+": missing independent exact candidate evidence")
        a["candidate_sha256_verified"]=observed

    if installed_path.is_file():
        installed=load(installed_path)
        if installed.get("format")!="devnet-installed-lifecycle-v0.1.0" or installed.get("app")!=c["guest_app"]:
            raise ValueError(app+": wrong installed guest schema/app")
        rootchecks=all(check_status(installed,k)=="PASS" for k in INSTALL_CHECKS)
        marker=proven_file(root,app,"installed","app-snapshot-rollback.txt")
        reboot=proven_file(root,app,"installed","installed-restored-pass.txt")
        evidence_root=marker.is_file() and reboot.is_file() and (
            "APP_BTRFS_SNAPSHOT_ROLLBACK_PASS" in marker.read_text(errors="replace")
            and "INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS" in reboot.read_text(errors="replace"))
        set_check(a,"installed_grub_btrfs","PASS" if rootchecks and evidence_root else "FAIL",
                  f"booted installed GRUB/BTRFS, system snapshot restore and reboot, run {c['installed']['run']}")
        for source,dest in (("clean_install","clean_install"),("uninstall","uninstall")):
            s=check_status(installed,source)
            if s not in STATES:raise ValueError(app+": invalid guest lifecycle state")
            set_check(a,dest,s,f"real installed guest report from run {c['installed']['run']}")
        a["installed_guest_snapshot_rollback"]="PASS" if evidence_root else "FAIL"
        a["application_rollback_not_implied"]=True

    if strict_path.is_file():
        strict=load(strict_path)
        if strict.get("gate")!="devnet-master-qa-strict-installed-v0.1.1" or strict.get("app")!=c["guest_app"]:
            raise ValueError(app+": strict v0.1.1 gate identity/schema mismatch")
        if strict.get("master_qa_release_approval")!="BLOCKED":
            raise ValueError(app+": original strict gate unexpectedly approved")
        if installed_path.is_file():
            if strict.get("app_clean_install")!=check(a,"clean_install") or strict.get("app_uninstall")!=check(a,"uninstall"):
                raise ValueError(app+": inconsistent strict vs installed lifecycle status")
            actual="PASS" if all(check(a,k)=="PASS" for k in ("clean_install","uninstall","installed_grub_btrfs")) else "BLOCKED"
            if strict.get("candidate_lifecycle_gate")!=actual:
                raise ValueError(app+": strict gate contradicts guest outcome")
            a["installation_classification"]=strict.get("installation_classification","UNCLASSIFIED")
        a["strict_evidence_gate_v0_1_1"]="VERIFIED"
    else:a["strict_evidence_gate_v0_1_1"]="NOT_TESTED"

    # Require strict v0.1.1 corroboration even if guest script reported success.
    if a["strict_evidence_gate_v0_1_1"]!="VERIFIED":
        set_check(a,"clean_install","NOT_TESTED","independent strict report is absent")
        set_check(a,"uninstall","NOT_TESTED","independent strict report is absent")

    # Supplemental reports must name individual scenarios with source evidence.
    extras=proven_file(root,app,"supplemental","scenarios.json")
    if extras.is_file():
        d=load(extras)
        if d.get("schema")!="devnet-master-qa-scenarios-v0.1.7" or d.get("app")!=app:
            raise ValueError(app+": invalid supplemental identity")
        for key,v in d.get("checks",{}).items():
            if key not in CHECKS:raise ValueError(app+": unknown scenario "+key)
            if key in ("archive_integrity","native_cachyos_package_tests","installed_grub_btrfs","clean_install","uninstall"):
                raise ValueError(app+": supplemental data may not override primary evidence")
            if v.get("status") not in STATES:raise ValueError(app+": invalid scenario status")
            if v["status"]=="PASS" and (
                not re.fullmatch(r"https://github\.com/devnet82/[a-zA-Z0-9_.-]+/actions/runs/\d+",v.get("source_run","")) or
                not v.get("evidence_sha256") or not re.fullmatch("[0-9a-f]{64}",v["evidence_sha256"])
            ):
                raise ValueError(app+": supplemental PASS without exact attributable run and digest")
            set_check(a,key,v["status"],v.get("source_run","supplemental report: no PASS"))
    return a

def check_detail(report,key):
    return str(report.get("checks",{}).get(key,{}).get("detail",""))

def check(report,key):
    return report.get("checks",{}).get(key,{}).get("status","NOT_TESTED")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--manifest",required=True)
    parser.add_argument("--evidence-root",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--app",help="single candidate ID for repository-local evaluation")
    args=parser.parse_args()
    manifest=load(args.manifest)
    if manifest.get("schema")!="devnet-master-qa-candidates-v0.1.7" or manifest.get("gate_version")!=VERSION:
        raise SystemExit("Unsafe or outdated Master QA manifest")
    if manifest.get("required_checks")!=CHECKS:raise SystemExit("Mandatory QA checklist changed")
    items=manifest.get("applications",[])
    if len(items)!=8 or len({x.get("id") for x in items})!=8:
        raise SystemExit("Expected eight distinct Devnet candidates")
    if args.app and args.app not in [x["id"] for x in items]:raise SystemExit("Unknown application ID")
    report={"schema":"devnet-master-qa-report-v0.1.7","gate_version":VERSION,
        "required_checks":CHECKS,"applications":[],
        "master_qa_release_approval":"BLOCKED",
        "blocked_reasons":[],
        "note":"No application approval unless every required check has independently verified PASS evidence"}
    for c in items:
        if args.app and c["id"]!=args.app:continue
        try:
            a=evaluate(c,Path(args.evidence_root))
        except Exception as e:
            a={"id":c["id"],"application":c["name"],"version":c["version"],
               "checks":{},"master_qa_release_approval":"BLOCKED",
               "evidence_error":str(e)[:220]}
            for k in CHECKS:set_check(a,k,"NOT_TESTED","invalid evidence: fail closed")
            set_check(a,"archive_integrity","FAIL","evidence inconsistent or unsafe")
        missing=[k for k in CHECKS if check(a,k)!="PASS"]
        a["blocked_checks"]=missing
        a["master_qa_release_approval"]="BLOCKED" if missing else "APPROVED"
        report["applications"].append(a)
        if missing:report["blocked_reasons"].append({"app":c["id"],"checks":missing})
    report["master_qa_release_approval"]="BLOCKED" if report["blocked_reasons"] else "APPROVED"
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("DEVNET_MASTER_QA_v0.1.7_"+report["master_qa_release_approval"])
    for a in report["applications"]:
        print(a["id"],a["master_qa_release_approval"],"PASS",
              sum(x["status"]=="PASS" for x in a["checks"].values()),
              "FAIL",sum(x["status"]=="FAIL" for x in a["checks"].values()),
              "NOT_TESTED",sum(x["status"]=="NOT_TESTED" for x in a["checks"].values()),
              a.get("installation_classification",""))
    return 0 if report["master_qa_release_approval"]=="APPROVED" else 2

if __name__=="__main__":sys.exit(main())
