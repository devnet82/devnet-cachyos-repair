# Devnet five-app exact-build native CachyOS VM QA — executed report

Date: 2026-10-11
QA harness: `devnet-native-cachyos-vm-qa-v0.1.2` (guest harness v0.1.0 except RGB corrected to v0.1.1 and ChatBox corrected to v0.1.2).
Target: authentic signed/checksummed CachyOS desktop ISO `cachyos-desktop-linux-260809.iso` with `ID=cachyos`, kernel observed `6.18.42-1-cachyos-lts`.
VM: isolated x86_64 QEMU/KVM `q35` guest, FAT control drive explicitly marked `DEVNETCONTROL`, no network, no device passthrough.
Tests ran against the original SHA-256-pinned draft ZIPs, not repository main-branch source.

## Results (verified GitHub Actions jobs)

| Application | SHA-256 pinned original | GitHub Actions run | Native CachyOS checks | Packaged tests |
| --- | --- | --- | --- | --- |
| Devnet RGB Control v8.11 | `aac1ecc08f1d905959e390396b754be1999345e5076aeebf0d9b5dc8fe4fbdb0` | [38135791535](https://github.com/devnet82/devnet-rgb-control/actions/runs/38135791535) | PASS | 1 PASS, 0 FAIL |
| VR Stack Control v0.6.132 | `04118623d828de96526e1c185409c586bf9ed1b4b1318451e4301277ff69baf1` | [38135445190](https://github.com/devnet82/vr-stack-control/actions/runs/38135445190) | PASS | 2 PASS, 0 FAIL |
| WayVR Watch Manager v0.1.34 | `1a0d8740649165f4bd0098b025a864bf784ac8e6aea046b70d80f7f5a94cae58` | [38135450307](https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38135450307) | PASS | 2 PASS, 0 FAIL |
| ChatBox GTK v0.1.3.133 | `6cd340be34e00b829a006bbc29d6d4e75f9949c42e6bf50fc0e9821a7058f978` | [38135938713](https://github.com/devnet82/devnet-chatbox/actions/runs/38135938713) | PASS | 1 PASS, 0 FAIL |
| VRChat yt-dlp/Deno Wrapper v0.1.4 | `f01fcf51c1da17bc03f66a8b541d7426d4e3438b03cbaf6de701ef8d632636f6` | [38135462908](https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38135462908) | PASS | 1 PASS, 0 FAIL |

**Native packaged regression total: 7/7 PASS; all five original packages checked SHA, ZIP integrity, version, Python/Bash syntax and genuine CachyOS OS identity.**

## Failure investigation and resolution

- v0.1.0 VM workflow failed to authenticate to draft releases (literal escaped GitHub expression). Corrected token in v0.1.1.
- v0.1.1 then referenced an incorrect versioned harness path. Corrected in v0.1.2.
- Native guest RGB/ChatBox v0.1.2 ran real CachyOS and correctly detected `exit=126` from package regression scripts due to `zipfile.extractall` not restoring Unix executable modes in the temporary unpacked sandbox. Never changed the original ZIP.
- RGB corrected in guest harness v0.1.1: executable `.sh` script bits restored in temporary VM copy; passed [v0.1.3 run](https://github.com/devnet82/devnet-rgb-control/actions/runs/38135791535).
- ChatBox extensionless `bin/devnet-chatbox` required shebang/archived-executable recognition; corrected in guest harness v0.1.2; passed [v0.1.4 run](https://github.com/devnet82/devnet-chatbox/actions/runs/38135938713).
- All superseded failed QA attempts are retained for audit. They must not be presented as application regressions without this diagnosis.

## Explicitly NOT TESTED / full Master QA remains BLOCKED

- Real installed CachyOS app clean install, uninstall, upgrade from known-good, interrupted upgrade and rollback on a provisioned root.
- Actual KDE/Wayland GUI and tray, single-instance behavior and Doctor repairs.
- BTRFS/GRUB installed-disk app rollback integrated with these five particular packages (a separate CachyOS installed-GRUB/BTRFS QEMU workflow did pass earlier; this is not an app-specific PASS).
- Quest 3 / WiVRn / WayVR / SteamVR / SlimeVR controller interactions; real VRChat and yt-dlp/Proton runtime behavior.
- Real RGB controller, fans and temperature protection; real Sonic Pad USB mapping/device tests.
- Full hardware portability, offline and corruption recovery, long-run load, configuration migration and permission edge cases.
- The excluded `devnet-proton-rtsp-v1.77.zip` was not uploaded as a draft pending privacy review. Sonic Pad Auto Printer v0.1.29 was not staged with these five apps.

All original GitHub draft releases and previously published working releases remain unmodified. No tests ran on the user's PC.
