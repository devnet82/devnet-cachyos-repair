# Devnet Master Application QA Gate v0.1.8 — Real Software Installation
Status: PROPOSED — not merged. Supersedes v0.1.7 for candidate QA only after validation.

## Mandatory rule: install the real testing software

For every Devnet application or plugin, build an explicit dependency/host-software manifest before executing tests. In a **fresh, disposable VM using the real target OS**, automatically download/install all software and libraries required to exercise the application *as it is used by the end user*. For each required item, capture all of the following:

1. **Source and integrity:** trusted vendor/package-manager origin; version pinned or recorded; archive digest and signature/hash verification where available.
2. **Installation:** actual successful installation or staging in the guest OS, not merely host download; path, installer exit status and missing-dependency check.
3. **Runtime proof:** run the **real application** in the guest, capture executable/version/proc evidence, startup logs, errors and screenshots where a GUI applies. A mock, Python import, CLI `--help`, or package listing is insufficient to certify a GUI.
4. **Integration:** install the candidate plugin in the actual host application's plugin manager, enable/reload it, confirm appearance, test UI, permissions and functionality. For camera features, use a stream simulator for automated networking and a real printer/camera for final hardware validation.
5. **Lifecycle and resilience:** fresh install, repeat install, upgrade/rollback, uninstall, corrupt/missing dependency, offline/reconnect, permissions, long-run, concurrency and known regressions.
6. **Evidence:** record exact OS release/kernel, executable paths, versions, checksums, installer and runtime logs, screenshots and structured per-test PASS/FAIL/NOT_TESTED statuses.
7. **Fail closed:** if installing, launching, or integrating any required software fails or cannot be measured, mark FAIL or NOT_TESTED. **Never promote/release on mocked tests, package metadata, GUI startup proxies or partial VM runs.**
8. **Preserve known-good:** do not overwrite existing release artifacts, change the main branch, edit user profiles, or make persistent changes outside the disposable QA VM.

### For Anycubic camera plugin
- Target guest: genuine CachyOS KDE VM.
- Host software: **official OrcaSlicer v2.5.0-alpha** plugin-enabled Linux distribution, installed into a disposable guest location; prove the version and actual GUI launch.
- Runtime dependency: genuine `ffmpeg` binary installed using pacman in the CachyOS guest, proven by `ffmpeg -version`.
- Install/enable `Devnet Anycubic Camera` **inside the real OrcaSlicer plugin manager** and observe the Pages tab; verify localhost MJPEG + FLV decode, permissions, reconnect, shutdown.
- A QA result that does not include real plugin-manager integration and UI proof remains BLOCKED, even if genuine CachyOS boots and standalone plugin tests pass.
- Physical Kobra S1 Max camera and Windows 11 target compatibility are separate mandatory checks, not claimable from the VM.

QA gate revision from v0.1.7: adds **mandatory automatic installation and runtime evidence of all software needed for testing**.
