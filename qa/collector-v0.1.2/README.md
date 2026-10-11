# Devnet Installed Apps Collector v0.1.2 — QA candidate

**Purpose:** safely collect source and resources from your *installed* VR Stack Control and WayVR Watch Manager, to help create complete versioned installers. This is a CLI application, not a KDE GUI/tray app. No network, sudo, service control, Steam/VRChat or ADB access is needed.

**Source confidentiality:** Exact installed source may include embedded private paths or passwords even when config directories are excluded. The collector **refuses to create an archive when privacy indicators are found**, unless you inspect the listed relative paths first and explicitly pass `--allow-privacy-flags`. Never upload an archive containing credentials; remove them locally or ask for help with a redacted export. Every completed ZIP is mode 0600.

## Safe usage on CachyOS (fish-compatible)

From the extracted ZIP folder:

```sh
bash install.sh --dry-run
bash install.sh
~/.local/bin/devnet-export-installed-apps --doctor
~/.local/bin/devnet-export-installed-apps
```

The normal export requires all *nine known required files* across the two apps. If you only have one app installed, use `--app vr_stack` or `--app wayvr`. Missing file/unsafe paths cause a fail-closed error, not a misleading success. If the Doctor shows missing files, stop; do not use an incomplete archive to rebuild a full app.

After locally checking each indicated source file for secrets, you may explicitly use `--allow-privacy-flags` to preserve *unaltered source bytes*. Review the private ZIP again before sharing. **Do not upload private keys, tokens, passwords or personal data.**

To remove the collector (does not change VR Stack/WayVR): `bash uninstall.sh --dry-run` then `bash uninstall.sh`. Only a script marked as managed by this app will be removed; backup files are preserved.

## Master QA semantics

- CLI collector: no GUI/tray or daemon, so GUI and service behaviour are **NOT_APPLICABLE**. Doctor and concurrency tests apply.
- Test fixture with current app source != direct test on actual Quest/SteamVR PC: real installed-source completeness is **NOT_TESTED** until export is collected and inspected.
- No user app data or live services are intentionally accessed; source privacy detection is heuristic, not a guarantee.
- All source archives must be reviewed before upload. Never substitute this export for a tested final app installer.
