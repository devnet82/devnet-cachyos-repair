#!/usr/bin/env python3
"""Regression tests for the Master QA evidence gate. No application code runs."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE=Path(__file__).with_name("gate.py")
spec=importlib.util.spec_from_file_location("devnet_master_gate",SOURCE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MANIFEST=Path(__file__).with_name("candidates.json")
CANDIDATES=json.loads(MANIFEST.read_text())["applications"]
APP=next(x for x in CANDIDATES if x["id"]=="vr_stack")

def evidence(base,section,name,obj):
    p=Path(base)/APP["id"]/section/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj)+"\n")
    return p

def build_valid_native(base):
    native={"format":"devnet-native-cachyos-vm-qa-v0.1.2",
      "expected_version":APP["version"],"release_decision":"BLOCKED",
      "checks":{name:{"status":"PASS","detail":APP["sha256"] if name=="exact_sha256" else "confirmed"}
        for name in gate.NATIVE_CHECKS},
      "tests":[{"test":"tests/test-package.py","status":"PASS","detail":"exit=0"},
               {"test":"tests/test-package.sh","status":"PASS","detail":"exit=0"}]}
    evidence(base,"native","qa-result.json",native)
    inv={"format":"devnet-master-qa-inventory-v0.1.0",
        "app":APP["guest_app"],"archive_name":APP["archive"],
        "sha256_expected":APP["sha256"],"sha256_observed":APP["sha256"],
        "checks":{k:"PASS" for k in ("exact_archive","zip_safety_crc","inventory")}}
    evidence(base,"inventory","installation-inventory.json",inv)
    installed={"format":"devnet-installed-lifecycle-v0.1.0",
      "app":APP["guest_app"],
      "checks":{k:{"status":"PASS"} for k in gate.INSTALL_CHECKS}}
    installed["checks"].update({
      "clean_install":{"status":"FAIL","detail":"exit=1"},
      "uninstall":{"status":"NOT_TESTED","detail":"install unsuccessful"}})
    evidence(base,"installed","app-lifecycle-result.json",installed)
    p=Path(base)/APP["id"]/"installed"
    (p/"app-snapshot-rollback.txt").write_text("APP_BTRFS_SNAPSHOT_ROLLBACK_PASS\n")
    (p/"installed-restored-pass.txt").write_text("INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS\n")
    strict={"gate":"devnet-master-qa-strict-installed-v0.1.1",
      "app":APP["guest_app"],"master_qa_release_approval":"BLOCKED",
      "app_clean_install":"FAIL","app_uninstall":"NOT_TESTED",
      "candidate_lifecycle_gate":"BLOCKED","installation_classification":"PACKAGE_OR_INSTALLER_FAILURE"}
    evidence(base,"strict","strict-gate-result.json",strict)
    return installed

class GateTests(unittest.TestCase):
    def test_full_manifest_exactly_eight_and_all_required_checks(self):
        d=json.loads(MANIFEST.read_text())
        self.assertEqual(d["gate_version"],gate.VERSION)
        self.assertEqual(len(d["applications"]),8)
        self.assertEqual(d["required_checks"],gate.CHECKS)
        for a in d["applications"]:
            self.assertTrue(a["version"])
            if "sha256" in a:self.assertRegex(a["sha256"],r"^[0-9a-f]{64}$")

    def test_missing_evidence_never_green(self):
        with tempfile.TemporaryDirectory() as temp:
            for a in CANDIDATES:
                result=gate.evaluate(a,Path(temp))
                self.assertEqual(len(result["checks"]),18)
                self.assertNotEqual(sum(x["status"]=="PASS" for x in result["checks"].values()),18)

    def test_green_vm_and_snapshot_cannot_mask_broken_installer(self):
        with tempfile.TemporaryDirectory() as temp:
            build_valid_native(temp)
            r=gate.evaluate(APP,Path(temp))
            self.assertEqual(gate.check(r,"native_cachyos_package_tests"),"PASS")
            self.assertEqual(gate.check(r,"archive_integrity"),"PASS")
            self.assertEqual(gate.check(r,"installed_grub_btrfs"),"PASS")
            self.assertEqual(gate.check(r,"clean_install"),"FAIL")
            self.assertEqual(gate.check(r,"uninstall"),"NOT_TESTED")
            self.assertEqual(gate.check(r,"application_rollback"),"NOT_TESTED")
            self.assertEqual(r["strict_evidence_gate_v0_1_1"],"VERIFIED")

    def test_changed_original_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            build_valid_native(temp)
            p=Path(temp)/APP["id"]/"inventory"/"installation-inventory.json"
            bad=json.loads(p.read_text());bad["sha256_observed"]="0"*64
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,"digest mismatch"):
                gate.evaluate(APP,Path(temp))

    def test_mismatched_strict_gate_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            build_valid_native(temp)
            p=Path(temp)/APP["id"]/"strict"/"strict-gate-result.json"
            bad=json.loads(p.read_text());bad["app_clean_install"]="PASS"
            p.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,"inconsistent strict"):
                gate.evaluate(APP,Path(temp))

    def test_no_unverified_supplemental_overrides(self):
        with tempfile.TemporaryDirectory() as temp:
            build_valid_native(temp)
            evidence(temp,"supplemental","scenarios.json",{
                "schema":"devnet-master-qa-scenarios-v0.1.7","app":APP["id"],
                "checks":{"clean_install":{"status":"PASS"}}})
            with self.assertRaisesRegex(ValueError,"may not override"):
                gate.evaluate(APP,Path(temp))

    def test_missing_evidence_full_command_exits_blocked_and_saves_json(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/"out.json"
            p=subprocess.run([sys.executable,str(SOURCE),"--manifest",str(MANIFEST),
                "--evidence-root",temp,"--output",str(output)],
                text=True,capture_output=True)
            self.assertEqual(p.returncode,2,p.stderr)
            report=json.loads(output.read_text())
            self.assertEqual(report["master_qa_release_approval"],"BLOCKED")
            self.assertEqual(len(report["applications"]),8)
            self.assertTrue(all(x["master_qa_release_approval"]=="BLOCKED" for x in report["applications"]))

if __name__=="__main__":unittest.main(verbosity=2)
