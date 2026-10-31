# Devnet Wine Idle Cleaner v0.1.1 — QA BLOCKED
Exact unmodified candidate ZIP SHA256: `f11cd9bd6e5ea0f4738ddf472be9ff8c79dcfa5c2fea85a843ca1a2d8bf8889b`.
Safety fix for live v0.1.0 Fusion residual processes: `explorer.exe /desktop`, `ADPClientService.exe`, `conhost.exe --headless`, and `MicrosoftEdgeUpdate.exe /c`. Recognition requires matching exact/anchored command lines for the specific Fusion WINEPREFIX. All unrecognised processes still block. To arm cleanup, the timer must have seen a genuine non-helper application in the same Wine-server PID/starttime session; a restarted server disarms. After verified residual processes are unchanged for 180 seconds, two real scans are required before issuing `WINEPREFIX=<exact Fusion prefix> wineserver -k`. This can interrupt background updaters and remains an unapproved candidate.

Local exact extracted ZIP: 29/29 freshly executed behaviour/process tests PASS, 4/4 freshly executed disposable non-root install/rollback tests PASS. Checksum and syntax PASS. Host Fusion active-app and closed-app baseline only tested on v0.1.0; no real host Wine shutdown on v0.1.1.
GitHub-first QA workflows staged: `.github/workflows/devnet-wine-idle-v011-exact.yml` and `.github/workflows/devnet-wine-idle-v011-native-cachyos.yml`. Need `qa/devnet-wine-idle-cleaner-v0.1.1/candidate.zip` uploaded with SHA256 before runs pass. GitHub hosted native CachyOS tests, host live Fusion lifecycle, update-in-progress guard, systemd timer, safe isolation, and host rollback remain NOT TESTED on v0.1.1.

**MASTER_QA=BLOCKED; RELEASE_APPROVED=false; NO HOST INSTALL/ENABLE.**

## Verified GitHub-first execution (2026-10-31)
- Exact candidate SHA256: `f11cd9bd6e5ea0f4738ddf472be9ff8c79dcfa5c2fea85a843ca1a2d8bf8889b`, uploaded under commit `3fbe9f0d774eef0fe213a2a22568d8d7de846951`.
- GitHub exact archive Ubuntu test run [41216720135](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41216720135): success; 29/29 behaviour and 4/4 simulated non-root install/rollback, independent evidence gate success.
- GitHub native CachyOS QEMU/KVM test run [41216909095](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41216909095): success; 33/33 fresh tests, independent evidence and attestation gate success.
- Prior native workflow [41216719939](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41216719939) failed before guest on an incorrect pinned VM controller helper URL; corrected workflow only, exact ZIP unchanged.
- Scope: native tests exercise mocked prefix behaviour and disposable user installer, **not** real Fusion Wine background shutdown or host systemd timer lifecycle. Host live Fusion closed-process status, updater protection, actual gated stop, restart preservation, timing under suspend/resume, upgrade/rollback on user host remain **NOT TESTED**.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**
