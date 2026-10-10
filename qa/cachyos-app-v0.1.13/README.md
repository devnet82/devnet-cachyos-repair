# Devnet CachyOS Repair — VM QA v0.1.13

Frozen production application: **v0.1.19**, SHA-256 `435bc2a88a99eef4cd5e85d71d50ca36e3d3f40361efe53db85e57e2d20fea0c`.

The v0.1.12 VM run verified 33/33 desktop acceptance checks **against the actual KWin Wayland compositor** in the disposable CachyOS guest. It also verified staged installation, v0.1.17 → v0.1.19 upgrade, rollback, repeat upgrade and uninstall.

The same run could only execute stages 1–7 of the full packaged 19-stage suite, then encountered missing `unzip` at stage 8.

This v0.1.13 QA harness supplies `zip` and `unzip` from the Ubuntu GitHub Actions worker over the isolated transfer disk. They are copied to the guest's temporary directory, ELF signatures and executability are verified there, and `qa.sh` receives the temporary tool path. The guest's pacman database and the application ZIP are not modified.

- Genuine CachyOS KVM guest on two chipsets: Q35 and PC
- Official live ISO checksum and exact candidate ZIP SHA-256 verification
- Packaged PySide6 33-check integration (offscreen and compositor when found)
- Five-stage actual installer test using safe disposable DESTDIR
- Full packaged 19-stage QA execution inside guest (as guest root, so its user-negative permission test is meaningful)
- Separate evidence for ZIP tools and guest logs

The release gate still refuses 100% approval without an installed and rebooted GRUB/BTRFS guest, all supported KDE session types, complete repair workflows and physical hardware acceptance.

Workflow: `.github/workflows/cachyos-app-vm-qa-v0.1.13.yml`. QA version changed; the application remains **v0.1.19**.
