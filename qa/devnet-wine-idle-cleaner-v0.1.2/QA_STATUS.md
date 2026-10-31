# Wine Idle Cleaner v0.1.2 — strict Master QA status

**MASTER_QA=BLOCKED; RELEASE_APPROVED=false; DO NOT INSTALL/ENABLE.**

Exact candidate zip `devnet-wine-idle-cleaner-v0.1.2-QA-BLOCKED.zip` SHA256:
`5cf355189c7ab0a815260724a9881bb729d69c112c4ae603defe78b1ad678d5d`

GitHub builds an archive byte-for-byte equal to the user's downloadable ZIP using `build_exact.py` and immutable pinned v0.1.1 ZIP SHA256 `f11cd9bd6e5ea0f4738ddf472be9ff8c79dcfa5c2fea85a843ca1a2d8bf8889b`. The SHA gate fails closed if any byte differs.

## Verified local exact-source scope
- Fresh 32/32 Python behavioural and sandbox compatibility tests PASS.
- Fresh 4/4 real install/uninstall with fake systemctl in disposable unprivileged home PASS.
- ZIP integrity and all SHA256SUMS PASS.
- `bash -n` installer/uninstaller PASS.
- Candidate SHA256 reproducible from independently extracted original ZIP.

## Prior evidence
- v0.1.1 manual host Fusion lifecycle `APP_RUNNING -> WAITING -> STOP_REQUESTED -> NO_WINE` PASS and Devnet gaming detector CLEAR. This is **prior version** evidence, not inherited as v0.1.2 PASS.
- v0.1.1 real Ubuntu user-systemd service could not inspect `/proc/PID/environ` (PermissionError EACCES). A/B experiment on `NoNewPrivileges`, `ProtectHome`, `ProtectSystem` singly failed, while disabling mount namespace directives **including `ReadWritePaths=`** permitted the same user service to run.
- v0.1.2 removes those incompatible mount sandbox features, keeps `NoNewPrivileges=yes`, `UMask=0077`, rootless operation, exact prefix stopping, process identity checks, 180-second grace and double scans.
- This is a security tradeoff: user process runs with ordinary filesystem permissions rather than the previous mount namespace.

## GitHub-first fresh v0.1.2 workflows
- Genuine native CachyOS QEMU/KVM 36-test [run 41221113219](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41221113219): result **PENDING** until jobs and independent gate complete.
- Real disposable-user systemd timer, active-app protection, unrelated Wine prefix, 180-second grace, rollback and independent gate [run 41221215205](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41221215205): result **PENDING** until jobs complete.

## Remaining mandatory scopes (untested for v0.1.2)
Real CachyOS host lifecycle under native systemd user manager, active and closed Fusion, updater not busy, recovery after reboot/suspend, mixed Wine-prefix isolation, host install/rollback and independent full Master QA gate. No release approval before evidence and user's own acceptance.
