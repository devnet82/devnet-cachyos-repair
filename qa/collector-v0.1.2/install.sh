#!/usr/bin/env bash
# Devnet Installed Apps Collector v0.1.2 — user-only atomic installation
set -Eeuo pipefail
version=0.1.2
if (( EUID == 0 )); then echo 'REFUSED: do not run with sudo/root' >&2; exit 2; fi
if [[ $# -gt 1 || ( $# == 1 && ${1-} != '--dry-run' ) ]]; then echo 'Usage: bash install.sh [--dry-run]' >&2; exit 2; fi
src=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/devnet-export-installed-apps-v0.1.2.py
[[ -f "$src" && ! -L "$src" ]] || { echo 'Missing/unsafe source' >&2; exit 2; }
python3 - "$src" <<'PYAST'
import ast, pathlib, sys
ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
PYAST
[[ -d "$HOME" && ! -L "$HOME" ]] || { echo 'Unsafe HOME' >&2; exit 2; }
dest_dir="$HOME/.local/bin"
dest="$dest_dir/devnet-export-installed-apps"
for path in "$HOME/.local" "$dest_dir"; do
  [[ ! -L "$path" ]] || { echo 'Refusing symlinked installation directory' >&2; exit 2; }
done
if [[ -e "$dest" || -L "$dest" ]]; then
  [[ -f "$dest" && ! -L "$dest" ]] || { echo 'Unsafe existing target' >&2; exit 2; }
  head -n 3 "$dest" | grep -Fq 'DEVNET_COLLECTOR_MANAGED' || { echo 'Existing unmanaged target — refusing overwrite' >&2; exit 2; }
  if cmp -s "$src" "$dest"; then echo 'Collector already installed; no changes'; exit 0; fi
fi
if [[ ${1-} == '--dry-run' ]]; then echo "DRY_RUN: would install v$version at $dest; no changes"; exit 0; fi
mkdir -p -- "$dest_dir"

tmp=$(mktemp "$dest_dir/.devnet-export-installed-apps.XXXXXXXX")
backup=''
cleanup(){ if [[ -n "$tmp" ]]; then rm -f -- "$tmp"; fi; return 0; }
trap cleanup EXIT
install -m 0755 -- "$src" "$tmp"
if [[ -f "$dest" ]]; then
  for path in "$HOME/.local/share" "$HOME/.local/share/devnet-installed-apps-collector" "$HOME/.local/share/devnet-installed-apps-collector/backups"; do
    [[ ! -L "$path" ]] || { echo "Symlinked backup directory — refusing update" >&2; exit 2; }
  done
  mkdir -p "$HOME/.local/share/devnet-installed-apps-collector/backups"
  backup="$HOME/.local/share/devnet-installed-apps-collector/backups/collector-$(date +%Y%m%d-%H%M%S)-$$"
  cp -p -- "$dest" "$backup"
  chmod 0600 "$backup"
fi
mv -f -- "$tmp" "$dest"
tmp=''
echo "INSTALLED: $dest (v$version)"
[[ -z "$backup" ]] || echo "Backup preserved: $backup"