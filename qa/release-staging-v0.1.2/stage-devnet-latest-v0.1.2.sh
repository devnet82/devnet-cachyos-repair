#!/usr/bin/env bash
# Devnet latest six archives: SAFE / DRAFT-ONLY staging v0.1.2.
# Checks September 30 frozen SHA-256 digests; no overwriting working releases.
set -Eeuo pipefail
umask 077

if (( EUID == 0 )); then echo "Run as normal user, not root/sudo." >&2; exit 2; fi
src_dir="$HOME/Downloads"
if (( $# > 0 )); then src_dir="$1"; fi
mode="--dry-run"
if (( $# > 1 )); then mode="$2"; fi
if (( $# > 2 )) || [[ "$mode" != "--dry-run" && "$mode" != "--upload-drafts" ]]; then
  echo "Usage: bash stage-devnet-latest-v0.1.2.sh [directory] [--dry-run|--upload-drafts]" >&2
  exit 2
fi
if [[ ! -d "$src_dir" ]]; then echo "Missing directory: $src_dir" >&2; exit 2; fi
for c in sha256sum stat python3 gh mktemp base64; do
  if ! command -v "$c" >/dev/null 2>&1; then echo "Missing command: $c" >&2; exit 2; fi
done

manifest="$(cat <<'MANIFEST'
devnet82/devnet-rgb-control|qa-package-v8.11|devnet-rgb-control-v8.11.zip|aac1ecc08f1d905959e390396b754be1999345e5076aeebf0d9b5dc8fe4fbdb0|39549
devnet82/vr-stack-control|qa-package-v0.6.132|vr-stack-control-v0.6.132.zip|04118623d828de96526e1c185409c586bf9ed1b4b1318451e4301277ff69baf1|4675
devnet82/devnet-wayvr-watch-manager|qa-package-v0.1.34|devnet-wayvr-watch-manager-v0.1.34.zip|1a0d8740649165f4bd0098b025a864bf784ac8e6aea046b70d80f7f5a94cae58|7625
devnet82/devnet-chatbox|qa-package-v0.1.3.133-gtk|devnet-chatbox-v0.1.3.133-gtk.zip|6cd340be34e00b829a006bbc29d6d4e75f9949c42e6bf50fc0e9821a7058f978|84842
devnet82/devnet-proton-rtsp|qa-package-v1.77|devnet-proton-rtsp-v1.77.zip|7ccd4867c327e883bf9632165303cee701be8ed2b6c3bf37e1a447f888f5d89e|12758
devnet82/vrchat-ytdlp-deno-wrapper|qa-package-v0.1.4|vrchat-ytdlp-deno-wrapper-v0.1.4.zip|f01fcf51c1da17bc03f66a8b541d7426d4e3438b03cbaf6de701ef8d632636f6|9523
MANIFEST
)"

# ZIP audit: read-only; CRC/decompression, path traversal and symlink checks.
zip_check() {
  python3 - "$1" <<'PY'
import pathlib, stat, sys, zipfile
p=pathlib.Path(sys.argv[1])
with zipfile.ZipFile(p) as z:
    infos=z.infolist()
    assert infos, "empty archive"
    seen=set()
    for m in infos:
        name=m.filename
        parts=pathlib.PurePosixPath(name).parts
        assert not name.startswith(('/', '\\')), "absolute path"
        assert '\\' not in name and '..' not in parts and '\x00' not in name, "unsafe archive path"
        assert name not in seen, "duplicate archive member"
        assert not stat.S_ISLNK(m.external_attr >> 16), "symlink member"
        seen.add(name)
    bad=z.testzip()
    assert bad is None, "corrupt ZIP member: "+str(bad)
print("ZIP_INTEGRITY_OK", p.name, len(infos), "entries")
PY
}

echo "Devnet latest-archive checksum QA / GitHub DRAFT staging v0.1.2"
echo "Files directory: $src_dir"
ready=0
bad=0
while IFS='|' read -r repo tag filename expected bytes; do
  f="$src_dir/$filename"
  if [[ ! -f "$f" || -L "$f" ]]; then
    echo "MISSING (will skip): $filename"
    continue
  fi
  actual_bytes="$(stat -c %s -- "$f")"
  actual_hash="$(sha256sum -- "$f" | cut -d' ' -f1)"
  if [[ "$actual_bytes" != "$bytes" || "$actual_hash" != "$expected" ]]; then
    echo "BLOCKED / WRONG BUILD: $filename"
    echo "  Expected: $expected ($bytes bytes)"
    echo "  Found:    $actual_hash ($actual_bytes bytes)"
    bad=1
    continue
  fi
  if ! zip_check "$f"; then
    echo "BLOCKED / BAD ZIP: $filename"
    bad=1
    continue
  fi
  echo "VERIFIED EXACT: $filename -> $repo ($tag)"
  ready=$((ready+1))
done <<< "$manifest"

if (( bad )); then
  echo "STOP: At least one input was wrong or corrupt. No uploads made." >&2
  exit 5
fi
if (( ready == 0 )); then
  echo "STOP: None of the six original frozen ZIPs were found. No uploads made." >&2
  exit 3
fi
echo "Verified exact archives found: $ready/6"
if [[ "$mode" != "--upload-drafts" ]]; then
  echo "DRY RUN ONLY — no GitHub modifications."
  echo "After reviewing archives, use: bash stage-devnet-latest-v0.1.2.sh \"$src_dir\" --upload-drafts"
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "STOP: Sign into GitHub CLI first (gh auth login)." >&2; exit 4
fi
echo "IMPORTANT: GitHub releases will remain DRAFT/UNPUBLISHED."
echo "The absent wrapper repo will be created PRIVATE; no other repo visibility will change."
echo "Original source from older versions is not being substituted."
read -r -p "Type STAGE SIX to upload verified available ZIPs as DRAFT releases: " consent </dev/tty
if [[ "$consent" != "STAGE SIX" ]]; then echo "Cancelled"; exit 0; fi

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
while IFS='|' read -r repo tag filename expected bytes; do
  f="$src_dir/$filename"
  if [[ ! -f "$f" || -L "$f" ]]; then continue; fi
  echo
  echo "Target: $repo ; ZIP: $filename"
  if [[ "$repo" == "devnet82/devnet-proton-rtsp" ]]; then
    echo "Proton RTSP ZIP may contain credentials or private RTSP URLs."
    echo "It will be staged as a GitHub draft, but repository collaborators may see it."
    read -r -p "Type REVIEWED PROTON to confirm you checked its contents, or Enter to skip: " proton </dev/tty
    if [[ "$proton" != "REVIEWED PROTON" ]]; then echo "SKIPPED Proton pending content review"; continue; fi
  fi
  if [[ "$repo" == "devnet82/vrchat-ytdlp-deno-wrapper" ]] &&
     ! gh repo view "$repo" >/dev/null 2>&1; then
    echo "Creating dedicated PRIVATE repository for VRChat yt-dlp/Deno wrapper..."
    gh repo create "$repo" --private --description "VRChat yt-dlp and Deno wrapper QA staging" >/dev/null
  fi
  if ! gh repo view "$repo" >/dev/null 2>&1; then
    echo "STOP: GitHub repository inaccessible: $repo" >&2; exit 6
  fi
  # Only initialize the originally empty repos. Never rewrite source trees.
  if [[ "$repo" == "devnet82/devnet-chatbox" || "$repo" == "devnet82/devnet-proton-rtsp" ||
        "$repo" == "devnet82/vrchat-ytdlp-deno-wrapper" ]]; then
    if ! gh api "repos/$repo/contents/README.md" >/dev/null 2>&1; then
      printf '# %s\n\nDraft QA package staging repository. Builds here are not approved.\n' "$repo" | base64 -w0 > "$tmp/readme.b64"
      gh api -X PUT "repos/$repo/contents/README.md" -f message="chore: initialize draft QA repository" \
        -f content="$(cat "$tmp/readme.b64")" >/dev/null
    fi
  fi
  # Leave any pre-existing release or tag untouched, whether or not it has been published.
  if gh release view "$tag" --repo "$repo" >/dev/null 2>&1 ||
     gh api "repos/$repo/git/ref/tags/$tag" >/dev/null 2>&1; then
    echo "SKIPPED: tag or release already exists (no overwrite): $tag"
    continue
  fi
  printf '%s  %s\n' "$expected" "$filename" > "$tmp/$filename.sha256"
  cat > "$tmp/release-notes.md" <<NOTES
# QA candidate (unpublished draft) — $filename

Archived candidate from September 30, 2026 Devnet verification report.

- Original ZIP SHA-256: $expected
- Original ZIP size: $bytes bytes
- Local original hash, size, ZIP paths and CRC were rechecked before uploading.
- This is NOT an approved public release or proof that default-branch source matches the package.
- CachyOS VM acceptance, hardware, GUI, upgrade, recovery and failure paths are NOT TESTED by this uploader.
- Previous working releases and tags were preserved.

Do not publish until full Master QA sign-off.
NOTES
  gh release create "$tag" --repo "$repo" --draft \
    --title "$filename — unverified QA candidate" --notes-file "$tmp/release-notes.md" \
    "$f" "$tmp/$filename.sha256"
  echo "DRAFT CREATED: $repo / $tag"
done <<< "$manifest"
echo "Staging complete. Existing releases untouched. Master QA remains BLOCKED."
