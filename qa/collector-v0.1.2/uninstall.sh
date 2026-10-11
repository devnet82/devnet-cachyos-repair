#!/usr/bin/env bash
# Devnet Installed Apps Collector v0.1.2 — user-only uninstall; preserves backups
set -Eeuo pipefail
if (( EUID == 0 )); then echo 'REFUSED: do not run with sudo/root' >&2; exit 2; fi
if [[ $# -gt 1 || ( $# == 1 && ${1-} != '--dry-run' ) ]]; then echo 'Usage: bash uninstall.sh [--dry-run]' >&2; exit 2; fi
[[ -d "$HOME" && ! -L "$HOME" && ! -L "$HOME/.local" && ! -L "$HOME/.local/bin" ]] || { echo 'Unsafe HOME/bin' >&2; exit 2; }
dest="$HOME/.local/bin/devnet-export-installed-apps"
if [[ ! -e "$dest" && ! -L "$dest" ]]; then echo 'Already uninstalled'; exit 0; fi
[[ -f "$dest" && ! -L "$dest" ]] || { echo 'Unsafe target' >&2; exit 2; }
head -n 3 "$dest" | grep -Fq 'DEVNET_COLLECTOR_MANAGED' || { echo 'Unmanaged target — refusing deletion' >&2; exit 2; }
if [[ ${1-} == '--dry-run' ]]; then echo "DRY_RUN: would uninstall $dest"; exit 0; fi
rm -- "$dest"
echo 'UNINSTALLED: collector CLI removed; backups and user files preserved'
