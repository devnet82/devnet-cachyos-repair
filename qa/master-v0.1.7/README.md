# Devnet Master QA v0.1.7 — Consolidated fail-closed gate

**Implemented and executed on 11 October 2026. All eight release approvals BLOCKED.**

## What was consolidated

- v0.1.6 authentic CachyOS/KVM and BTRFS recovery acceptance requirements, originally for CachyOS Repair.
- v0.1.1 strict installation evidence gate: a successful GitHub job or BTRFS snapshot restore is not proof an application's installer succeeded.
- Original draft ZIP hashes, native live-ISO packaged regressions, installed GRUB/BTRFS lifecycle logs, and inventory reports.
- Eight application candidates, 18 mandatory release checks each, release approval requiring 100% verified PASS.

**Canonical source:** [candidate inventory](candidates.json), [shared evaluator](gate.py), [regression tests](test_gate.py), [central workflow](../../.github/workflows/devnet-master-consolidated-v0.1.7.yml). All on branch **qa/devnet-master-consolidated-v0.1.7** in **devnet82/devnet-cachyos-repair**.

Each of the five original draft repositories also has a separate **qa/master-consolidated-v0.1.7** workflow using the same pinned evaluator. This downloads that repository's own original draft ZIP and its exact historical GitHub Actions artifacts. This design respects private-repository boundaries, including the private VRChat Wrapper. No original ZIP is repacked, replaced or republished, and no command runs on the user's physical CachyOS machine.

## Evidence-backed results

Each original five-app workflow validated **three PASS checks** (exact ZIP integrity, original packaged native CachyOS tests, booted GRUB/BTRFS guest and system snapshot restore), **one clean-install FAIL**, and **14 NOT_TESTED** release requirements. The new gate correctly exits nonzero, preserves its report and rejects release approval. Two installer failures may be actual package defects; the other three lacked required guest prerequisites.

| App | Clean-install evidence classification | v0.1.7 QA run | Master approval |
| --- | --- | --- | --- |
| RGB Control v8.11 | BLOCKED_ENVIRONMENT_OPENRGB | [38151431493](https://github.com/devnet82/devnet-rgb-control/actions/runs/38151431493) | BLOCKED |
| VR Stack Control v0.6.132 | PACKAGE_OR_INSTALLER_FAILURE (missing installed vr-control-gui) | [38151434599](https://github.com/devnet82/vr-stack-control/actions/runs/38151434599) | BLOCKED |
| WayVR Watch Manager v0.1.34 | PACKAGE_OR_INSTALLER_FAILURE (missing installed doctor.py) | [38151437621](https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38151437621) | BLOCKED |
| ChatBox GTK v0.1.3.133 | BLOCKED_ENVIRONMENT_PRIVILEGES_DEPENDENCIES | [38151440969](https://github.com/devnet82/devnet-chatbox/actions/runs/38151440969) | BLOCKED |
| VRChat yt-dlp/Deno Wrapper v0.1.4 | BLOCKED_ENVIRONMENT_STEAM_PREFIX | [38151443011](https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38151443011) | BLOCKED |
| Proton RTSP v1.77 | Original local-only SHA/CRC and targeted private-information scan PASS; native installed app NOT_TESTED; original kept unuploaded | No GitHub candidate gate | BLOCKED |
| Sonic Pad Auto Printer v0.1.29 | Physical Sonic Pad and USB/Klipper test rig NOT_TESTED in this programme | No device QA in this gate | BLOCKED |
| CachyOS Repair v0.1.20 | Existing installed GRUB/BTRFS platform recovery PASS from [38083265759](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759), not full v0.1.20 application lifecycle | Central check only | BLOCKED |

**Central consolidated eight-app result:** [GitHub Actions run 38151700200](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38151700200). The unit tests pass; the release job intentionally fails closed and preserves an eight-app JSON decision artifact. The central aggregator does not automatically possess private cross-repo raw evidence; missing local evidence is labelled NOT_TESTED. App-local gate artifacts are the independently verified package-level proof. Green jobs from older installed-system workflows remain historical and cannot override these release decisions.

## Safeguards and follow-on scope

Never count green workflow jobs without parsing guest results. Never substitute system BTRFS restore for application rollback. Original ZIP, version and installed guest identity must match. Supplemental PASS requires source run and matching SHA-256 proof bytes; physical hardware acceptance also needs explicit operator sign-off. Preserve all original draft assets unpublished. Every application code change requires a version bump and new candidate. Do not modify known-good releases.

Required future tests: fix actual installer/package blockers on new versions, stage missing isolated dependencies, verify clean install and uninstall, upgrade from known-good versions, application-specific rollback, migrations, GUI/tray, Doctor, services, failure injection, network reconnect, low disk/permissions, regressions, hardware portability, safety and physical acceptance. All unexecuted tests remain NOT_TESTED.
