# CachyOS App VM QA v0.1.15 — Devnet Repair v0.1.20

The v0.1.19 Boot Doctor CLI JSON export defect was proven in real Q35 and PC CachyOS guests.

- Frozen baseline release: `cachyos-repair-qa-assets-v0.1.19` (SHA-256 `435bc2a88a99eef4cd5e85d71d50ca36e3d3f40361efe53db85e57e2d20fea0c`).
- Reproducible v0.1.20 **test candidate**: SHA-256 `0474dcb99d1b9967b4c2b168727e5d2421105c150ac8b54eb5d4237b7b897c17`.
- The builder constructs the exact candidate from the unchanged GitHub Release ZIP, with a direct regression test for the CLI failure and version changes. Both input and output SHA-256 are enforced.
- A test candidate ZIP is preserved as a GitHub Actions artifact, not an approved release.
- Both Q35 and PC guests run the real 19-stage QA, 176 Python tests, native KDE Wayland widget and main GUI smoke, non-destructive diagnostic/CLI scans and the staged historical upgrade/rollback cycle.
- GRUB installed system reboot, native X11, actual privileged recovery and physical hardware remain NOT_TESTED and block full approval.

All production release files and original QA branches are preserved.
