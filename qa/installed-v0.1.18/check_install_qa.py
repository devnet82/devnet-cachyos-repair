#!/usr/bin/env python3
"""Strict evidence gate for genuine installed-system GRUB/BTRFS QA."""
import json
from pathlib import Path
import re
import sys


def verdict(evidence):
    checks = {}
    install = (evidence/'install.log').read_text(errors='replace') if (evidence/'install.log').exists() else ''
    boot = (evidence/'installed-boot.log').read_text(errors='replace') if (evidence/'installed-boot.log').exists() else ''
    ready = (evidence/'install-ready.txt').read_text(errors='replace') if (evidence/'install-ready.txt').exists() else ''
    first = (evidence/'installed-first-pass.txt').read_text(errors='replace') if (evidence/'installed-first-pass.txt').exists() else ''
    restore = (evidence/'installed-restored-pass.txt').read_text(errors='replace') if (evidence/'installed-restored-pass.txt').exists() else ''
    grub = (evidence/'restore-grub-prepared.txt').read_text(errors='replace') if (evidence/'restore-grub-prepared.txt').exists() else ''
    checks['target_disk_identity_and_install'] = ('PASS' if 'INSTALLED_BTRFS_GRUB_PREPARED' in ready and 'INSTALL_SCRIPT_EXIT=0' in install else 'NOT_TESTED')
    checks['grub_btrfs_first_installed_boot'] = ('PASS' if 'INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS' in first and 'ID=cachyos' in boot and 'btrfs' in boot else 'NOT_TESTED')
    checks['restore_snapshot_and_grub_configuration'] = ('PASS' if 'BTRFS_RESTORED_ENTRY_WRITTEN' in grub else 'NOT_TESTED')
    checks['grub_btrfs_restored_reboot'] = ('PASS' if 'INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS' in restore and 'subvol=@restored' in boot else 'NOT_TESTED')
    return {'gate':'devnet-installed-cachyos-vm-v0.1.18', 'checks':checks, 'all_vm_checks_pass': all(v=='PASS' for v in checks.values()), 'physical_hardware':'NOT_TESTED', 'systemd_boot':'NOT_TESTED', 'kde_x11':'NOT_TESTED', 'note':'VM success never constitutes physical-system validation'}


def main():
    folder=Path(sys.argv[1]) if len(sys.argv)>1 else Path('evidence')
    r=verdict(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'installed-system-qa.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(json.dumps(r,indent=2))
    if not r['all_vm_checks_pass']:
        print('BLOCKED: installed VM checks remain unverified',file=sys.stderr)
        return 1
    return 0
if __name__=='__main__':
    raise SystemExit(main())