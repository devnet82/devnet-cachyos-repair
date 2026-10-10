# Devnet Master QA portfolio — first executed audit (v0.1.0)

**GitHub Actions run**: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38094749419

Execution: 7 isolated Ubuntu 24.04 CI matrix jobs, each completed successfully as an audit runner. The final **Master QA 100% gate deliberately returned BLOCKED** because not all exact builds, integration scenarios and physical device tests are evidenced. This is not 7 fully approved apps.

## Per-repository audit results

| Connected repository | Tested source / release | Source/package test gate | Evidence and gaps |
|---|---|---|---|
| devnet-rgb-control | GitHub main `ed2e2589ea84`, published v8.8 SHA-256 `92ad889e178291ea07241095ea683524d5b7d677375bf02b03467df464209b00` | **PASS** | Python/Bash syntax, source archive CRC, published ZIP hash/CRC; actual `tests/test-package.sh` fake-HOME install, upgrade, backup, rollback, uninstall. **Not v8.9**, no new physical RGB/OpenLinkHub test. |
| vr-stack-control | GitHub main `b0ab652b31dc`, published v0.6.85 SHA-256 `db9af6ff47f3abcf07cf452ddd91e91cbd75a10296c0c6050bb5c612980d9cf3` | **INCOMPLETE** | Python/Bash syntax, archive and release integrity PASS. No selected regression suite, no Quest/SteamVR/WayVR hardware test. Library has later v0.6.129. |
| devnet-wayvr-watch-manager | GitHub main `54f96bc0008d` (README v0.1.14) | **INCOMPLETE** | Syntax, JSON, XML/SVG and source archive PASS. `tests/test_all.py` missing from repo; historical CI run [35040653409](https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/35040653409) failed at functional test. Later v0.1.33 Quest build is NOT TESTED by this run. |
| devnet-cachyos-repair | GitHub main `1f850c391e07`, published v0.1.19 SHA-256 `435bc2a88a99eef4cd5e85d71d50ca36e3d3f40361efe53db85e57e2d20fea0c` | **INCOMPLETE** | Release integrity PASS, default branch only README. Separate actual guest evidence v0.1.20 and installed GRUB+BTRFS recovery PASS in [run 38083265759](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759); UEFI/systemd-boot still NOT TESTED. |
| devnet-chatbox | GitHub main empty; Library ZIP v0.1.3.131 GTK | **INCOMPLETE** | No GitHub source/release, exact Library ZIP unavailable to runner. |
| devnet-proton-rtsp | GitHub main empty; Library ZIP v1.76 test | **INCOMPLETE** | No GitHub source/release, exact Library ZIP unavailable to runner. |
| wivrn-stack-control | GitHub main empty | **INCOMPLETE** | No GitHub source/release. Distinct from populated `vr-stack-control` repo. |

## Additional Devnet apps outside this seven-repository CI inventory

- **Sonic Pad Auto Printer**: Library contains `devnet-sonicpad-auto-printer-v0.1.26.zip`; newer versions reportedly used. Actual Sonic Pad USB/serial mapping, Klipper/Moonraker service and physical rebind/reconnect NOT TESTED.
- **Devnet Native Adaptive Cubic (OrcaSlicer)**: v0.1.16 project, complete editable Orca source/release is not in these seven GitHub source trees. Geometry and slice-based six-surface/connected-centre regressions NOT TESTED.
- **DevnetToolStore (Windows)**: Windows app requires native Windows install/GUI, stock inventory and Excel export tests. NOT TESTED.
- **AMD GPU RA24 prototype**: archived prototype in Library, not audited here.
- **Later ChatBox, Proton RTSP, RGB, VR Stack and WayVR packages**: do not inherit older source/release PASS results.

## How to continue

1. Make the exact ZIP for each latest application available in CI (private GitHub Releases if necessary); compare SHA-256 before extracting.
2. Run app-specific Master QA on exact bytes: clean install, upgrade from frozen known-good, rollback, uninstall, Doctor, GUI, version consistency, failure paths, concurrency, config migration and packaging.
3. On the **real CachyOS KVM VM** run KDE/Wayland/X11 and systemd installation scenarios for compatible Linux apps; never use generic Ubuntu CI PASS as a CachyOS VM result.
4. Run separate tests on Quest 3, WayVR/WiVRn, Sonic Pad hardware, RGB/OpenLinkHub and Windows as applicable.
5. Keep all destructive tests inside disposable VM disks and retain v0.1.19 CachyOS Repair / other known-good releases unchanged.
6. Aggregate evidence; a missing or blocked check is NOT_TESTED, not PASS.

The portfolio ZIP audit/report remains attached to run 38094749419 as `devnet-portfolio-v0.1.0-summary`.
