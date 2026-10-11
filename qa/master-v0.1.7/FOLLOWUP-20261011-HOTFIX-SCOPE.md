# 11 October 2026 — Devnet Master QA follow-up: supported hotfix baseline handling

**Master QA release approval remains BLOCKED.** This page amends earlier issue diagnoses and preserves original evidence. It does not alter any original ZIP or release.

## Corrected root cause — VR Stack and WayVR

The original v0.6.132 VR Stack ZIP explicitly identifies itself as a **version-sync hotfix** for installed v0.6.130/v0.6.131; it contains no complete GUI application and expects the installed `vr-control-gui` and `vr-doctor`.

The original v0.1.34 WayVR Watch ZIP identifies itself as an update for installed v0.1.31/v0.1.32/v0.1.33; it expects pre-existing `doctor.py`, `watchlib.py`, `metrics.py` and `watch.xml` and intentionally leaves the latter two unchanged.

Therefore the earlier blank-home installed-VM "clean-install fails" were *invalid acceptance scenarios* for these update-only packages, **not proven defects**. The historical test results are preserved, but must not be interpreted as failed production hotfix upgrades. The two GitHub issue descriptions have been corrected.

## New executed native installed GRUB/BTRFS hotfix checks — PASS (fixture scope)

| Candidate | Native installed system test | Guest regression outcome | Evidence |
| --- | --- | --- | --- |
| VR Stack v0.6.132 | Supported-version v0.6.131 GUI/Doctor fixture | supported upgrade, version sync, idempotency, rollback, mid-update failure recovery, unsupported version rejection, BTRFS snapshot restore/reboot PASS | https://github.com/devnet82/vr-stack-control/actions/runs/38154711365 |
| WayVR Watch v0.1.34 | Supported-version v0.1.33 Doctor/watchlib/metrics/watch fixture | supported upgrade, idempotency, Doctor suppression vs controller failure regression, protected file checks, rollback, injected failure recovery, version rejection, BTRFS snapshot restore/reboot PASS | https://github.com/devnet82/devnet-wayvr-watch-manager/actions/runs/38154717720 |

Both workflows retrieved the original unpublished ZIP asset, verified its original SHA-256, installed a **genuine CachyOS GRUB/BTRFS** VM and executed candidate code **unprivileged** inside an offline guest. Guest JSON logs and snapshot/reboot markers are preserved as GitHub Actions artifacts.

**Crucial limit:** Supported-version baselines were *synthetic fixtures based on original packaged regression tests*. These passes are not evidence of upgrading a complete existing historical application installation or live Quest/SteamVR runtime acceptance. Genuine baseline upgrade, visual GUI/tray and real hardware remain NOT_TESTED. Full new versions are not indicated solely by these clean-home errors.

## Other original packages: isolated test mode (distinct from production)

- RGB Control v8.11 exact original ZIP: isolated clean install and uninstall PASS in explicit `DEVNET_TEST_MODE=1`, configuration preservation tested locally; real OpenRGB/Commander and user-systemd acceptance NOT_TESTED.
- ChatBox GTK v0.1.3.133 original ZIP: isolated clean install and uninstall PASS with `DEVNET_CHATBOX_TEST_MODE=1`, with no real GTK/media dependency validation; production desktop NOT_TESTED.
- VRChat yt-dlp/Deno Wrapper v0.1.4: packaged suite PASS with a fake Steam prefix and compiler, including repeated installation, uninstall/restore and missing dependency preflight; real SteamVR/VRChat playback NOT_TESTED.

Native installed-CachyOS test-mode workflows launched (do not mark PASS until completed):
- RGB: https://github.com/devnet82/devnet-rgb-control/actions/runs/38155099232
- ChatBox: https://github.com/devnet82/devnet-chatbox/actions/runs/38155105112
- Wrapper (private): https://github.com/devnet82/vrchat-ytdlp-deno-wrapper/actions/runs/38155111267

## Remaining acceptance requirements

- Authentic supported full-application baseline upgrades for VR Stack/WayVR, including service/GUI and protected user data.
- Native production-mode dependencies and live GUI/tray for RGB and ChatBox; real Windows wrapper binary, Steam Proton prefix and playback for VRChat.
- Fully independent hardware acceptance, portability, network/offline/reconnect, low disk, corrupt package, security protections, and any other remaining Master QA scenarios.
- Proton RTSP v1.77 kept separate/unpublished after local-only privacy scan. Sonic Pad v0.1.29 requires actual hardware. CachyOS Repair v0.1.20 remains a separate app acceptance target; only the prior GRUB/BTRFS VM platform recovery has been verified.

**No commands executed on the user's CachyOS PC. No original ZIP or GitHub draft release modified.**
