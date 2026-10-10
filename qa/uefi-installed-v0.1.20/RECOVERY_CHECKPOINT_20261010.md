# CachyOS installed-VM QA recovery checkpoint — 2026-10-10

This file is a verified state handoff, not a claim of Master QA completion.

## Tested application

- Devnet CachyOS Repair application version: **0.1.20 test candidate**, SHA-256 `0474dcb99d1b9967b4c2b168727e5d2421105c150ac8b54eb5d4237b7b897c17`.
- Original known-good **0.1.19** GitHub release is unchanged: `cachyos-repair-qa-assets-v0.1.19`.
- v0.1.20 is reproducibly built by the QA builder and was tested in disposable CachyOS VM runs, but is **not** permanently published or Master QA 100% approved.
- Earlier app-in-CachyOS VM evidence: 19/19 packaged QA stages, 176 Python tests, 33/33 native KDE Wayland PySide6 acceptance checks, staged install/upgrade/rollback/uninstall, BTRFS snapshot, CLI JSON fix.

## Real installed BIOS/GRUB BTRFS guest: PASS

Branch: `qa/cachyos-installed-btrfs-grub-v0.1.19`
Run: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759
GitHub conclusion: **success**.

All real installed-guest workflow stages passed:
1. Official ISO checksum and exact app build SHA256.
2. Disposable target disk identity verification and BTRFS/GRUB installation.
3. Boot from installed BTRFS+GRUB disk.
4. Snapshot restoration / GRUB configuration.
5. Reboot into restored root and verification.
6. Strict installed-system test gate (4/4 PASS).

The passing run emits `INSTALLED_BTRFS_GRUB_PREPARED`, `INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS`, and `INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS`.

## Real installed UEFI/systemd-boot BTRFS guest: BLOCKED

Branch: `qa/cachyos-installed-uefi-systemdboot-v0.1.20`
Run: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083838792
GitHub conclusion: **failure**.

The ISO and exact app checksum passed. The 12-GiB disposable QEMU disk and OVMF firmware were prepared. The VM then **booted into the OVMF UEFI Interactive Shell, not the CachyOS ISO**. The serial evidence says:
- `BdsDxe: failed to load Boot0001 "UEFI Misc Device"... Not Found`
- `BdsDxe: starting Boot0002 "EFI Internal Shell"`
- At `Shell>`, scripted `root`, `mount /dev/vda /mnt`, and `bash /mnt/install-guest.sh` were not recognized.
- No `install.log`, `install-ready.txt`, or target UUID was produced.
- The systemd-boot installed disk, first boot, recovery, and reboot tests are **NOT_TESTED**, not failed application tests.

Likely fix target: QEMU OVMF boot configuration / ISO UEFI boot device mapping. First verify the ISO's EFI bootability and QEMU boot device options, then **test that CachyOS actually reaches Linux before injecting shell commands**. Never format an unverified device or bypass disk-identity guards.

## Remaining separate acceptance

- UEFI/systemd-boot installed BTRFS and reboot recovery.
- KDE X11 session tests, where supported.
- Real installed-system app install/uninstall and end-to-end Guided Repair.
- Physical system hardware acceptance (cannot pass from QEMU alone).
- Full Master QA approval remains BLOCKED. Preserve all known-good branches/releases and do not claim 100%.

## Stream interruption mitigation

Avoid giant continuous chat/tool sequences. Break QA into versioned GitHub branches and one run at a time, write short evidence checkpoints to GitHub, and report results after each run. An OpenAI/ChatGPT `Error in input stream` does **not**, by itself, mean the GitHub job stopped.
