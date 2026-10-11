# Devnet Master Application QA — 2026-10-11 (execution checkpoint)

**Release decision: BLOCKED for every listed candidate.** This is evidence accounting, not a declaration of application fitness.

## Source preservation
- Five original release ZIPs remain unpublished draft assets, unchanged.
- SHA-256 names/expected digests are the original values from 2026-10-11 handover.
- All application changes require an application version bump; only QA branches/harness files were changed at this checkpoint.
- Earlier public releases must not be altered.
- The installed native VM is a disposable GRUB/BTRFS disk, **not** the user's host PC. A prior workflow's virtual disk was not persisted, so a new isolated disk is allocated per workflow using its proven installation scripts.
- Latest successful original-package native CachyOS live ISO tests: 5/5 jobs and 7/7 discovered test entry points; see links below.
- A successful native ISO suite does **not** satisfy clean-install, upgrade, app rollback, uninstall, GUI, services or physical hardware acceptance.

## Per-application independent status

| Candidate | Native live ISO packaged tests | 2026-10-11 ZIP installation inventory | Installed GRUB/BTRFS lifecycle | App upgrade | App rollback | GUI/tray | Hardware | Master QA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RGB Control v8.11 | PASS (1/1) | PASS, install/uninstall found; 3 service files; requires command review | BLOCKED_ENVIRONMENT: OpenRGB missing; VM snapshot rollback PASS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| VR Stack Control v0.6.132 | PASS (2/2) | PASS, install/uninstall found | ATTEMPTED: clean install FAIL (missing vr-control-gui); guest snapshot rollback PASS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| WayVR Watch Manager v0.1.34 | PASS (2/2) | PASS, install/uninstall found | ATTEMPTED: clean install FAIL (missing doctor.py); guest snapshot rollback PASS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| ChatBox GTK v0.1.3.133 | PASS (1/1) | PASS, install/uninstall found; .desktop found; requires command review | BLOCKED_ENVIRONMENT: GTK/media deps absent and no privileged sudo; VM snapshot rollback PASS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| VRChat yt-dlp/Deno Wrapper v0.1.4 | PASS (1/1) | PASS, install/uninstall found; requires command review | BLOCKED_ENVIRONMENT: Steam/VRChat Proton prefix missing; VM snapshot rollback PASS | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Proton RTSP v1.77 | exact ZIP SHA/CRC PASS; packaged regression PASS in isolated container (not CachyOS VM) | Targeted secret/private URL scan PASS, no matches; kept unuploaded | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Sonic Pad Auto Printer v0.1.29 | NOT_TESTED under this programme | NOT_TESTED | NOT_APPLICABLE to desktop VM / device-specific test required | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| CachyOS Repair v0.1.20 | v0.1.20 reported installed on user's real PC; don't generalise | NOT_TESTED in this portfolio stage | GRUB/BTRFS installed-system recovery PASS in prior 38083265759 run; broader lifecycle NOT_TESTED | NOT_TESTED | BTRFS snapshot recovery PASS for existing VM harness | NOT_TESTED | NOT_TESTED | BLOCKED |

## GitHub evidence — completed successes
- RGB Control live ISO: https://github.com/devnet82/devnet-rgb-control/actions/runs/38135791535 ; original ZIP inventory https://github.com/devnet82/devnet-rgb-control/actions/runs/38139396850
- VR Stack live ISO: https://github.com/devnet82/vr-stack-control/actions/runs/38135445190 ; original ZIP inventory https://github.com/devnet82/vr-stack-control/actions/runs/38139399618
- WayVR Watch live ISO: https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38135450307 ; original ZIP inventory https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38139402496
- ChatBox GTK live ISO: https://github.com/devnet82/devnet-chatbox/actions/runs/38135938713 ; original ZIP inventory https://github.com/devnet82/devnet-chatbox/actions/runs/38139406998
- Private VRChat Wrapper live ISO: https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38135462908 ; original ZIP inventory https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38139409878
- Installed GRUB/BTRFS original recovery success: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759

## Completed installed-system workflows — application installers did NOT pass
All five GitHub jobs ended green **only because the v0.1.0 gate omitted an assertion on clean_install**. This is a QA harness false-positive documented in https://github.com/devnet82/devnet-cachyos-repair/issues/1. Every guest JSON reported clean_install FAIL. DO NOT use their green job conclusions for release approval.

| Application | Installed-guest test | Exit | Relevant guest evidence | Interpretation |
| --- | --- | --- | --- | --- |
| RGB Control v8.11 | https://github.com/devnet82/devnet-rgb-control/actions/runs/38139916648 | 1 | `ERROR: OpenRGB is not installed` | BLOCKED_ENVIRONMENT; OpenRGB hardware/software prerequisite not staged |
| VR Stack v0.6.132 | https://github.com/devnet82/vr-stack-control/actions/runs/38139657456 | 1 | expected `~/.local/bin/vr-control-gui` absent | PACKAGE_OR_INSTALLER_BLOCKER; https://github.com/devnet82/vr-stack-control/issues/1 |
| WayVR Watch v0.1.34 | https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38139671344 | 2 | expected `~/.local/share/devnet-wayvr-watch-manager/doctor.py` absent | PACKAGE_OR_INSTALLER_BLOCKER; https://github.com/devnet82/devnet-wayvr-watch-manager/issues/1 |
| ChatBox GTK v0.1.3.133 | https://github.com/devnet82/devnet-chatbox/actions/runs/38139919127 | 1 | GTK/media packages absent; unprivileged sudo impossible | BLOCKED_ENVIRONMENT; missing desktop prerequisite packages |
| VRChat yt-dlp/Deno Wrapper v0.1.4 | https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38139921433 | 1 | required VRChat Proton prefix/Tools directory absent | BLOCKED_ENVIRONMENT; requires fake isolated Steam-prefix fixture |

**All five** workflows independently verified ID=cachyos on installed BTRFS, the original SHA-256, ZIP extraction, their GRUB/BTRFS snapshot restore, and reboot into restored root (PASS). All five uninstall/upgrade/app-internal rollback paths remain NOT_TESTED. DO NOT confuse VM-system rollback PASS with application rollback PASS.

## Separate Proton RTSP v1.77 private-content review (11 October 2026)
Original ZIP found in personal Library (12,758 bytes) and inspected locally only. SHA-256 matched `7ccd4867c327e883bf9632165303cee701be8ed2b6c3bf37e1a447f888f5d89e`; ZIP CRC and path safety passed. Targeted static scan found no embedded private keys, PATs, assigned credentials or private-network URLs. The only URL host found is github.com, addressing a Devnet baseline release. Packaged `tests/test-package.sh` returned exit=0 in an isolated container fixture. This is NOT a genuine native CachyOS VM run and does NOT verify full runtime/physical playback. Original ZIP remains unuploaded/unpublished; release BLOCKED.

### Limitations / safeguards
- Installed-system base environment is headless and may lack GTK4, WayVR or other devices. Failed dependency preflight must not be labelled an application regression.
- Guest app installation is executed as `nobody` in a disposable guest, not as root. Root/system-wide installation behaviour is still NOT_TESTED.
- BTRFS snapshot revert of the disposable installed guest, if successful, does not prove application-specific upgrade/rollback paths.
- GUI/tray interaction, Quest hardware, GPU, Sonic Pad, RGB controllers, and physical host acceptance are all NOT_TESTED.
- The Proton RTSP ZIP must be scanned privately for credentials/private URLs before upload or executing any installation workflow.


## Strict QA gate v0.1.1: completed 2026-10-11

The false-green installed workflow was corrected by a separately versioned **artifact-only** strict gate, which re-read the exact saved guest JSON and logs; this did not rebuild the VM or application candidates. All five strict runs completed and **correctly failed the lifecycle approval gate**. These red statuses are expected, not new application failures.

| App | Strict gate run | App install classification | Original app ZIP changed? |
| --- | --- | --- | --- |
| RGB Control | https://github.com/devnet82/devnet-rgb-control/actions/runs/38140508091 | BLOCKED_ENVIRONMENT_OPENRGB | No |
| VR Stack Control | https://github.com/devnet82/vr-stack-control/actions/runs/38140510594 | PACKAGE_OR_INSTALLER_FAILURE | No |
| WayVR Watch Manager | https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38140513036 | PACKAGE_OR_INSTALLER_FAILURE | No |
| ChatBox GTK | https://github.com/devnet82/devnet-chatbox/actions/runs/38140516303 | BLOCKED_ENVIRONMENT_PRIVILEGES_DEPENDENCIES | No |
| VRChat Wrapper (private) | https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38140518433 | BLOCKED_ENVIRONMENT_STEAM_PREFIX | No |

Each strict run saved `master-qa-strict-installed-gate-v0.1.1` as a workflow artifact and exited nonzero when application installation was not verified. The original older workflow conclusions remain preserved, but cannot be used as release acceptance evidence. All draft releases stay unpublished.


## Consolidated Devnet Master QA v0.1.7 — final checked-in execution (11 October 2026)

**IMPLEMENTED AND EXECUTED. Eight of eight applications remain BLOCKED.**
The canonical versioned implementation is [qa/master-v0.1.7/README.md](../master-v0.1.7/README.md), with [candidate manifest](../master-v0.1.7/candidates.json), [shared evidence evaluator](../master-v0.1.7/gate.py) and [self-tests](../master-v0.1.7/test_gate.py). The gate consolidates v0.1.6's genuine CachyOS/KVM requirement and v0.1.1's strict no-false-green installed-app acceptance.

**Latest final five exact-candidate QA runs, common immutable evaluator SHA-pinned to 9de8c6bb36ae47e8ea7d1681223dd4bd9ba53967:**
- RGB Control v8.11: https://github.com/devnet82/devnet-rgb-control/actions/runs/38151856428 — 3 PASS / 1 FAIL / 14 NOT_TESTED; clean-install environment OpenRGB missing; release BLOCKED.
- VR Stack v0.6.132: https://github.com/devnet82/vr-stack-control/actions/runs/38151859668 — 3 PASS / 1 FAIL / 14 NOT_TESTED; installed GUI binary missing; release BLOCKED.
- WayVR Watch v0.1.34: https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38151866496 — 3 PASS / 1 FAIL / 14 NOT_TESTED; doctor.py missing; release BLOCKED.
- ChatBox GTK v0.1.3.133: https://github.com/devnet82/devnet-chatbox/actions/runs/38151868862 — 3 PASS / 1 FAIL / 14 NOT_TESTED; GTK/media/privilege prerequisites missing; release BLOCKED.
- VRChat Wrapper v0.1.4 (private): https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38151871270 — 3 PASS / 1 FAIL / 14 NOT_TESTED; isolated Steam Proton prefix missing; release BLOCKED.

Each app-local run independently downloaded its original *unpublished* draft ZIP and its four pinned historical evidence artifacts, re-verified exact SHA-256 and checked guest/native/install/strict reports with the same versioned gate. All five strict release jobs intentionally exited nonzero and uploaded an app-specific report artifact. A red release gate is **correct** while any required check is not PASS.

The other three candidates are registered with independent BLOCKED decisions:
- Proton RTSP v1.77: local archive/secret scan and packaged regression previously passed, but native CachyOS lifecycle and hardware NOT_TESTED. Original candidate unuploaded.
- Sonic Pad Auto Printer v0.1.29: original physical Sonic Pad device and USB/Klipper workflows NOT_TESTED by this programme.
- CachyOS Repair v0.1.20: original installed CachyOS GRUB/BTRFS system rollback evidence from run 38083265759 was re-read and verified for **platform** recovery; full candidate lifecycle and hardware NOT_TESTED.

**Central eight-app gate:** https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38151828817 (passing self-tests, intentional release-blocking failure, eight-app JSON report saved). This central report does not automatically read the private repository's raw GitHub artifact; its missing locally imported app evidence is explicitly NOT_TESTED, while the five app-local gate reports are the detailed verified sources.

**Safeguards:** All five GitHub draft releases remain unpublished and byte-exact SHA-256 digests were independently rechecked. No original archive or published version changed; only QA branches and workflow/test files changed. No command was executed on the user's real CachyOS installation. Actual user's bootloader: GRUB with BTRFS.
