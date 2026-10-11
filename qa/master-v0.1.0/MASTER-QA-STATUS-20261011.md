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
| RGB Control v8.11 | PASS (1/1) | PASS, install/uninstall found; 3 service files; requires command review | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| VR Stack Control v0.6.132 | PASS (2/2) | PASS, install/uninstall found | IN_PROGRESS: run 38139657456 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| WayVR Watch Manager v0.1.34 | PASS (2/2) | PASS, install/uninstall found | IN_PROGRESS: run 38139671344 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| ChatBox GTK v0.1.3.133 | PASS (1/1) | PASS, install/uninstall found; .desktop found; requires command review | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| VRChat yt-dlp/Deno Wrapper v0.1.4 | PASS (1/1) | PASS, install/uninstall found; requires command review | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Proton RTSP v1.77 | exact ZIP SHA/CRC verified locally in handover; native VM NOT_TESTED | Sensitive information inspection NOT_TESTED; deliberately not uploaded | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| Sonic Pad Auto Printer v0.1.29 | NOT_TESTED under this programme | NOT_TESTED | NOT_APPLICABLE to desktop VM / device-specific test required | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | BLOCKED |
| CachyOS Repair v0.1.20 | v0.1.20 reported installed on user's real PC; don't generalise | NOT_TESTED in this portfolio stage | GRUB/BTRFS installed-system recovery PASS in prior 38083265759 run; broader lifecycle NOT_TESTED | NOT_TESTED | BTRFS snapshot recovery PASS for existing VM harness | NOT_TESTED | NOT_TESTED | BLOCKED |

## GitHub evidence — completed successes
- RGB Control live ISO: https://github.com/devnet82/devnet-rgb-control/actions/runs/38135791535 ; original ZIP inventory https://github.com/devnet82/devnet-rgb-control/actions/runs/38139396850
- VR Stack live ISO: https://github.com/devnet82/vr-stack-control/actions/runs/38135445190 ; original ZIP inventory https://github.com/devnet82/vr-stack-control/actions/runs/38139399618
- WayVR Watch live ISO: https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38135450307 ; original ZIP inventory https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38139402496
- ChatBox GTK live ISO: https://github.com/devnet82/devnet-chatbox/actions/runs/38135938713 ; original ZIP inventory https://github.com/devnet82/devnet-chatbox/actions/runs/38139406998
- Private VRChat Wrapper live ISO: https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38135462908 ; original ZIP inventory https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38139409878
- Installed GRUB/BTRFS original recovery success: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759

## Running installed-system workflows (do not count as successes until completed)
- VR Stack: https://github.com/devnet82/vr-stack-control/actions/runs/38139657456
- WayVR Watch: https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38139671344

### Limitations / safeguards
- Installed-system base environment is headless and may lack GTK4, WayVR or other devices. Failed dependency preflight must not be labelled an application regression.
- Guest app installation is executed as `nobody` in a disposable guest, not as root. Root/system-wide installation behaviour is still NOT_TESTED.
- BTRFS snapshot revert of the disposable installed guest, if successful, does not prove application-specific upgrade/rollback paths.
- GUI/tray interaction, Quest hardware, GPU, Sonic Pad, RGB controllers, and physical host acceptance are all NOT_TESTED.
- The Proton RTSP ZIP must be scanned privately for credentials/private URLs before upload or executing any installation workflow.
