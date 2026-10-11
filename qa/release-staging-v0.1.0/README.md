# Devnet package release staging v0.1.0

## Purpose and permissions

The GitHub connector can modify UTF-8 repository source/workflow files but **does not expose an authenticated binary GitHub Release asset upload action**. ChatGPT's isolated local code execution environment is unavailable in this conversation. User-uploaded archive bytes cannot be bridged directly to `gh release upload` with the available connected actions.

Therefore this repository contains a **tested, non-destructive upload helper** designed to run once on the user's own CachyOS computer with GitHub CLI authentication. It uploads original archives without repackaging or changing application source.

Self-test GitHub run: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38126411686 — workflow passed. This verifies the helper's Bash syntax, safe dry run and missing-file fail-close behaviour. It does **not** claim any of the five actual archives have been tested or transferred to GitHub.

## Exact uploaded application map

| GitHub destination | Existing repository? | QA tag to create | Exact original file | Uploaded file size |
| --- | --- | --- | --- | ---: |
| devnet82/devnet-rgb-control | Yes; protect published v8.8 | qa-package-v8.9 | devnet-rgb-control-v8.9(1).zip | 38,924 |
| devnet82/devnet-wayvr-watch-manager | Yes | qa-package-v0.1.33 | devnet-wayvr-watch-manager-v0.1.33.zip | 6,256 |
| devnet82/vr-stack-control | Yes; protect published v0.6.85 | qa-package-v0.6.131 | vr-stack-control-v0.6.131.zip | 2,427 |
| devnet82/devnet-proton-rtsp | Yes; empty public repo | qa-package-v1.74 | devnet-proton-rtsp-v1.74-fresh-capture.tar(1).gz | 517,425,558 |
| devnet82/devnet-sonicpad-auto-printer | Not yet; create PRIVATE | qa-package-v0.1.29 | devnet-sonicpad-auto-printer-v0.1.29.zip | 2,732,085 |

The Proton fresh capture may include private data and **must remain draft until inspected**; the helper requires separate capture-specific approval.

The `qa-package-` tag namespace keeps these pre-QA drafts distinct from normal final releases. Existing release/tag assets will not be overwritten.

## Step-by-step on user's CachyOS PC (fish)

Install GitHub CLI if it is not present:

```fish
sudo pacman -S --needed github-cli
```

Check login:

```fish
gh auth status
```

If needed: `gh auth login` and choose GitHub.com, HTTPS, and browser login.

Fetch the helper at the pinned Git commit and verify Bash syntax:

```fish
curl -fL https://raw.githubusercontent.com/devnet82/devnet-cachyos-repair/76e9b6c4a6cbbc6582879f8d8d7653b0e93b4f5e/qa/release-staging-v0.1.0/stage-devnet-packages.sh -o ~/Downloads/stage-devnet-packages.sh
bash -n ~/Downloads/stage-devnet-packages.sh
bash ~/Downloads/stage-devnet-packages.sh ~/Downloads
```

That performs **DRY RUN ONLY**, prints SHA-256 of the five original files and refuses to run if one is missing. The exact five original archives must be saved in `~/Downloads` or pass a different directory.

After reviewing SHA-256 values and access/privacy, run:

```fish
bash ~/Downloads/stage-devnet-packages.sh ~/Downloads --upload-drafts
```

There will be explicit consent prompts. Sonic Pad repository is created private only if absent. Proton capture requires separate `STAGE CAPTURE` consent; otherwise it is skipped.

## Next stage

Once the draft assets exist, use authenticated CI in the respective repositories to download the **exact ZIP/TAR**, calculate/check its SHA-256, and run isolated CachyOS VM archive QA; follow with app-specific install/upgrade/rollback/GUI/Doctor tests. Physical Quest 3, Sonic Pad and RGB acceptance remains NOT_TESTED until run on real devices.

None of this means the applications are fully approved; Master QA remains BLOCKED until actual exact-release evidence exists.
