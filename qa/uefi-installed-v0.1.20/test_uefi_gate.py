import tempfile
import unittest
from pathlib import Path
from check_uefi_qa import verdict
class InstalledGateTests(unittest.TestCase):
    def test_no_files_blocks(self):
        with tempfile.TemporaryDirectory() as t:
            r=verdict(Path(t))
            self.assertFalse(r['all_vm_checks_pass'])
            self.assertTrue(all(v=='NOT_TESTED' for v in r['checks'].values()))
    def test_partial_evidence_not_approved(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            (p/'install-ready.txt').write_text('INSTALLED_UEFI_SYSTEMDBOOT_BTRFS_PREPARED')
            (p/'install.log').write_text('INSTALL_SCRIPT_EXIT=0')
            r=verdict(p)
            self.assertEqual(r['checks']['target_disk_identity_and_install'],'PASS')
            self.assertFalse(r['all_vm_checks_pass'])
    def test_complete_evidence_passes_vm_only(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            files={
                'install-ready.txt':'INSTALLED_UEFI_SYSTEMDBOOT_BTRFS_PREPARED',
                'install.log':'INSTALL_SCRIPT_EXIT=0',
                'installed-first-pass.txt':'INSTALLED_UEFI_SYSTEMDBOOT_BTRFS_FIRST_BOOT_PASS',
                'installed-boot.log':'ID=cachyos\nbtrfs\nrootflags=subvol=@restored\n',
                'restore-systemdboot-prepared.txt':'UEFI_SYSTEMDBOOT_RESTORED_ENTRY_WRITTEN',
                'installed-restored-pass.txt':'INSTALLED_UEFI_SYSTEMDBOOT_BTRFS_REBOOT_ROLLBACK_PASS'
            }
            for n,c in files.items():(p/n).write_text(c)
            r=verdict(p)
            self.assertTrue(r['all_vm_checks_pass'])
            self.assertEqual(r['physical_hardware'],'NOT_TESTED')
if __name__=='__main__':unittest.main()