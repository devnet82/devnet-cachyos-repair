#!/usr/bin/env bash
# Runs exclusively in disposable installed CachyOS /dev/vdb QEMU disk.
set -Eeuo pipefail
CONTROL=/mnt/devnet-control
mkdir -p "$CONTROL"
mount -o rw /dev/vda "$CONTROL" || exit 60
exec >> "$CONTROL/installed-boot.log" 2>&1
trap 'rc=$?; echo INSTALLED_BOOT_SCRIPT_EXIT=$rc; sync' EXIT
printf '%s\n' "QA_BOOT_START=$(date -u +%FT%TZ)" "KERNEL=$(uname -r)"
cat /etc/os-release
findmnt -no SOURCE,FSTYPE,OPTIONS /
cat /proc/cmdline
[ "$(lsblk -dn -o SERIAL /dev/vdb | tr -d '[:space:]')" = DEVNETQAONLY ] || exit 61
grep -q '^ID=cachyos' /etc/os-release || exit 62
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 63
uuid=$(cat "$CONTROL/target-btrfs-uuid.txt")
[ "$(blkid -s UUID -o value /dev/vdb2)" = "$uuid" ] || exit 64
if [ -f "$CONTROL/installed-first-pass.txt" ]; then
   grep -q 'subvol=@restored' /proc/cmdline || exit 65
   [ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 66
   printf '%s\n' INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS > "$CONTROL/installed-restored-pass.txt"
   sync
   echo INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS
   exit 0
fi
grep -q 'rootflags=subvol=@' /proc/cmdline || exit 67
[ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 68
printf '%s\n' INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS > "$CONTROL/installed-first-pass.txt"
# Validate the unchanged exact application candidate on a *booted installed system*.
# Read-only CLI test; no repair or destructive commands.
if command -v python3 >/dev/null && command -v unzip >/dev/null; then
  mkdir -p /var/tmp/devnet-installed-app
  unzip -q "$CONTROL/candidate.zip" -d /var/tmp/devnet-installed-app
  cd /var/tmp/devnet-installed-app/devnet-cachyos-repair-v0.1.20
  PYTHONPATH=. python3 -m devnet_cachyos_repair.cli --cli --json /var/tmp/devnet-installed-diagnostic.json || true
  if [ -s /var/tmp/devnet-installed-diagnostic.json ]; then
    [ "$(stat -c %a /var/tmp/devnet-installed-diagnostic.json)" = 600 ] || exit 72
    python3 -m json.tool /var/tmp/devnet-installed-diagnostic.json >/dev/null || exit 73
    echo INSTALLED_READ_ONLY_CLI_JSON_CREATED
    cp /var/tmp/devnet-installed-diagnostic.json "$CONTROL/installed-cli-diagnostic.json"
  fi
fi
# Actual BTRFS recovery: modify active root, create fresh RW restored snapshot,
# and change the GRUB entry to boot it on the next reboot.
mkdir -p /mnt/devnet-btrfs-top
mount -o subvolid=5 /dev/vdb2 /mnt/devnet-btrfs-top
[ -d /mnt/devnet-btrfs-top/@known-good ] || exit 69
printf '%s\n' simulated-broken > /etc/devnet-qa-marker
btrfs subvolume snapshot /mnt/devnet-btrfs-top/@known-good /mnt/devnet-btrfs-top/@restored
[ "$(cat /mnt/devnet-btrfs-top/@restored/etc/devnet-qa-marker)" = known-good ] || exit 70
grep -F 'linux /@/boot/' /boot/grub/grub.cfg
sed -i 's|/@/boot/|/@restored/boot/|g; s|rootflags=subvol=@ |rootflags=subvol=@restored |' /boot/grub/grub.cfg
grep -F 'linux /@restored/boot/' /boot/grub/grub.cfg
grep -q 'rootflags=subvol=@restored' /boot/grub/grub.cfg || exit 71
printf '%s\n' BTRFS_RESTORED_ENTRY_WRITTEN > "$CONTROL/restore-grub-prepared.txt"
sync
systemctl reboot