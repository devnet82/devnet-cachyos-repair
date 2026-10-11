#!/usr/bin/env bash
# Devnet QA Release Staging v0.1.1. Never overwrites existing releases.
# No app installers, service changes, reboots, or public publishing.
set -Eeuo pipefail
umask 077

if (( EUID == 0 )); then
  echo "ERROR: Run as ordinary user, never with sudo." >&2
  exit 2
fi
source_dir="$HOME/Downloads"
if (( $# >= 1 )); then source_dir="$1"; fi
mode=""
if (( $# >= 2 )); then mode="$2"; fi
if [[ "$mode" != "" && "$mode" != "--upload-drafts" ]] || (( $# > 2 )); then
  echo "Usage: bash stage-devnet-packages.sh [directory] [--upload-drafts]" >&2
  exit 2
fi
if [[ ! -d "$source_dir" ]]; then
  echo "ERROR: Directory missing: $source_dir" >&2
  exit 2
fi
for cmd in gh sha256sum mktemp python3 base64 stat; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: Missing $cmd" >&2
    exit 2
  fi
done

manifest="$(cat <<'APPS'
devnet82/devnet-rgb-control|qa-package-v8.9|Devnet RGB Control v8.9 QA candidate|devnet-rgb-control-v8.9(1).zip
devnet82/devnet-wayvr-watch-manager|qa-package-v0.1.33|Devnet WayVR Watch Manager v0.1.33 QA candidate|devnet-wayvr-watch-manager-v0.1.33.zip
devnet82/vr-stack-control|qa-package-v0.6.131|Devnet VR Stack Control v0.6.131 QA candidate|vr-stack-control-v0.6.131.zip
devnet82/devnet-proton-rtsp|qa-package-v1.74|Devnet Proton RTSP v1.74 capture QA candidate|devnet-proton-rtsp-v1.74-fresh-capture.tar(1).gz
devnet82/devnet-sonicpad-auto-printer|qa-package-v0.1.29|Devnet Sonic Pad Auto Printer v0.1.29 QA candidate|devnet-sonicpad-auto-printer-v0.1.29.zip
APPS
)"

echo "Devnet GitHub release draft uploader — v0.1.1"
echo "Candidate packages are NOT verified or approved."
echo "Source folder: $source_dir"
# This is a partial-staging tool. Missing files are skipped, NOT fabricated.
# The 517 MB Proton fresh-capture file is NEVER uploaded to the public
# devnet-proton-rtsp repository, even as a draft.
eligible=0
resolve_file() {
  local f="$source_dir/$1"
  if [[ "$1" == "devnet-rgb-control-v8.9(1).zip" && ! -f "$f" ]]; then
    f="$source_dir/devnet-rgb-control-v8.9.zip"
  fi
  [[ -f "$f" && ! -L "$f" && -s "$f" ]] || return 1
  printf '%s\n' "$f"
}
while IFS='|' read -r repo tag title filename; do
  if [[ "$repo" == "devnet82/devnet-proton-rtsp" ]]; then
    echo "SKIPPED: Proton fresh capture requires separate privacy review/private staging."
    continue
  fi
  if ! file="$(resolve_file "$filename")"; then
    printf 'SKIPPED missing: %s (repo %s)\n' "$filename" "$repo"
    continue
  fi
  eligible=$((eligible+1))
  printf 'READY %s  SHA256:%s  %s bytes\n' "$(basename "$file")" "$(sha256sum -- "$file" | cut -d' ' -f1)" "$(stat -c %s -- "$file")"
done <<< "$manifest"
if (( eligible == 0 )); then
  echo "STOP: No matching safe package files found. Nothing was uploaded." >&2
  exit 3
fi
echo "READY: $eligible packages; others will be skipped."

if [[ "$mode" != "--upload-drafts" ]]; then
  echo
  echo "DRY RUN ONLY — no uploads or repo changes."
  echo "To upload DRAFT release assets:"
  echo "  bash stage-devnet-packages.sh \"$source_dir\" --upload-drafts"
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "STOP: GitHub CLI not authenticated. Run: gh auth login" >&2
  exit 4
fi
echo
echo "Releases remain DRAFT. No existing releases are overwritten."
echo "The Sonic Pad repo will be created PRIVATE if not present."
read -r -p "Type STAGE DEVNET to proceed: " approval </dev/tty
if [[ "$approval" != "STAGE DEVNET" ]]; then
  echo "Cancelled."
  exit 0
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf -- "$tmpdir"' EXIT

ensure_bootstrap() {
  local target="$1"
  if ! gh api "repos/$target/contents/README.md" >/dev/null 2>&1; then
    printf '# %s\n\nThis repository initially holds DRAFT QA package archives only. No release is approved until original assets and QA tests are verified.\n' "$target" | base64 -w 0 > "$tmpdir/content.b64"
    gh api -X PUT "repos/$target/contents/README.md" \
      -f message='chore: initialize QA staging' \
      -f content="$(cat "$tmpdir/content.b64")" >/dev/null
  fi
}

while IFS='|' read -r repo tag title filename; do
  if [[ "$repo" == "devnet82/devnet-proton-rtsp" ]]; then
    echo "SKIPPED Proton fresh capture: no public-repo upload without privacy review."
    continue
  fi
  if ! file="$(resolve_file "$filename")"; then
    echo "SKIPPED missing archive: $filename"
    continue
  fi
  echo
  echo "Staging $(basename "$file") in $repo"
  if [[ "$repo" == "devnet82/devnet-sonicpad-auto-printer" ]] &&
     ! gh repo view "$repo" >/dev/null 2>&1; then
    echo "Creating dedicated PRIVATE Sonic Pad GitHub repository..."
    gh repo create "$repo" --private \
      --description "Devnet Sonic Pad Auto Printer — QA candidate staging" >/dev/null
  fi
  if ! gh repo view "$repo" >/dev/null 2>&1; then
    echo "STOP: GitHub repository not accessible: $repo" >&2
    exit 5
  fi
  if [[ "$repo" == "devnet82/devnet-proton-rtsp" ||
        "$repo" == "devnet82/devnet-sonicpad-auto-printer" ]]; then
    ensure_bootstrap "$repo"
  fi
  if gh release view "$tag" --repo "$repo" >/dev/null 2>&1; then
    echo "SKIPPED existing tag/release: $repo $tag (never overwrite)"
    continue
  fi
  actual_name="$(basename "$file")"
  (
    cd "$source_dir"
    sha256sum -- "$actual_name" > "$tmpdir/$actual_name.sha256"
  )
  cat > "$tmpdir/notes.txt" <<NOTES
DRAFT / UNVERIFIED ORIGINAL PACKAGE ARCHIVE

Original filename: $(basename "$file")
Exact SHA-256: $(sha256sum -- "$file" | cut -d' ' -f1)
Archive bytes: $(stat -c %s -- "$file")

This DRAFT is for isolated VM and QA tests. It is NOT a public approved
release and does not mean that GitHub's default-branch source matches this
archive. Do not deploy it to production hardware before Master QA sign-off.

No existing GitHub release, tag or application source is overwritten.
NOTES
  gh release create "$tag" --repo "$repo" \
    --draft --title "$title" --notes-file "$tmpdir/notes.txt" \
    "$file" "$tmpdir/$actual_name.sha256"
  echo "STAGED DRAFT: $repo/releases/tag/$tag"
done <<< "$manifest"
echo
echo "Draft staging completed. Application Master QA is still BLOCKED."
echo "Use authenticated same-repo GitHub Actions to retrieve these draft assets."
