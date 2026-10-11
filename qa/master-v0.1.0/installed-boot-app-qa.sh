#!/usr/bin/env bash
# Original v0.1.19 installed CachyOS GRUB/BTRFS VM boot test,
# with isolated per-app lifecycle test before BTRFS snapshot rollback.
set -Eeuo pipefail
CONTROL=/mnt/devnet-control
mkdir -p "$CONTROL"
mount -o rw /dev/vda "$CONTROL" || exit 60
exec >>"$CONTROL/installed-boot.log" 2>&1
trap 'rc=$?; echo INSTALLED_BOOT_SCRIPT_EXIT=$rc; sync' EXIT
echo "QA_BOOT_START=$(date -u +%FT%TZ)"
uname -r
cat /etc/os-release
findmnt -no SOURCE,FSTYPE,OPTIONS /
cat /proc/cmdline
[ "$(lsblk -dn -o SERIAL /dev/vda | tr -d '[:space:]')" = DEVNETCONTROL ] || exit 60
[ "$(lsblk -dn -o SERIAL /dev/vdb | tr -d '[:space:]')" = DEVNETQAONLY ] || exit 61
grep -q '^ID=cachyos' /etc/os-release || exit 62
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 63
uuid=$(cat "$CONTROL/target-btrfs-uuid.txt")
[ "$(blkid -s UUID -o value /dev/vdb2)" = "$uuid" ] || exit 64
if [ -f "$CONTROL/installed-first-pass.txt" ]; then
  grep -q 'rootflags=subvol=@restored' /proc/cmdline || exit 65
  [ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 66
  [ ! -e /etc/devnet-qa-app-marker ] || exit 67
  [ ! -e /var/tmp/devnet-lifecycle-package ] || exit 68
  printf '%s\n' APP_BTRFS_SNAPSHOT_ROLLBACK_PASS >"$CONTROL/app-snapshot-rollback.txt"
  printf '%s\n' INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS >"$CONTROL/installed-restored-pass.txt"
  sync
  echo INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS
  exit 0
fi
grep -q 'rootflags=subvol=@ ' /proc/cmdline || exit 69
[ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 70
printf '%s\n' INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS >"$CONTROL/installed-first-pass.txt"
test -s "$CONTROL/candidate.zip"
test -s "$CONTROL/guest_lifecycle.py"
# Life cycle process can fail; evidence must still be preserved and the
# guest snapshot rollback must still be exercised.
python3 "$CONTROL/guest_lifecycle.py" "$CONTROL/candidate.zip" \
  SHA_PLACEHOLDER APP_PLACEHOLDER \
  "$CONTROL/app-lifecycle-result.json" "$CONTROL/app-lifecycle.log" \
  || echo APP_LIFECYCLE_FAILED_OR_INCOMPLETE
test -s "$CONTROL/app-lifecycle-result.json"
printf 'app-tested-rollback-must-remove\n' > /etc/devnet-qa-app-marker
mkdir -p /mnt/devnet-btrfs-top
mount -o subvolid=5 /dev/vdb2 /mnt/devnet-btrfs-top
[ -d /mnt/devnet-btrfs-top/@known-good ] || exit 71
printf '%s\n' simulated-broken > /etc/devnet-qa-marker
btrfs subvolume snapshot /mnt/devnet-btrfs-top/@known-good /mnt/devnet-btrfs-top/@restored
[ "$(cat /mnt/devnet-btrfs-top/@restored/etc/devnet-qa-marker)" = known-good ] || exit 72
grep -F 'linux /@/boot/' /boot/grub/grub.cfg
sed -i 's|/@/boot/|/@restored/boot/|g; s|rootflags=subvol=@ |rootflags=subvol=@restored |' /boot/grub/grub.cfg
grep -q 'rootflags=subvol=@restored' /boot/grub/grub.cfg || exit 73
printf '%s\n' BTRFS_RESTORED_ENTRY_WRITTEN >"$CONTROL/restore-grub-prepared.txt"
sync
systemctl reboot
