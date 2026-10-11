#!/usr/bin/env bash
# QEMU only. Reuse validated GRUB/BTRFS installed-VM boot and snapshot rollback.
set -Eeuo pipefail
CONTROL=/mnt/devnet-control
mkdir -p "$CONTROL"
mount -o rw /dev/vda "$CONTROL" || exit 60
exec >>"$CONTROL/installed-boot.log" 2>&1
trap 'rc=$?; echo INSTALLED_BOOT_SCRIPT_EXIT=$rc; sync' EXIT
cat /etc/os-release
findmnt -no SOURCE,FSTYPE,OPTIONS /
cat /proc/cmdline
[ "$(lsblk -dn -o SERIAL /dev/vda | tr -d '[:space:]')" = DEVNETCONTROL ] || exit 61
[ "$(lsblk -dn -o SERIAL /dev/vdb | tr -d '[:space:]')" = DEVNETQAONLY ] || exit 62
grep -q '^ID=cachyos' /etc/os-release || exit 63
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 64
uuid=$(cat "$CONTROL/target-btrfs-uuid.txt")
[ "$(blkid -s UUID -o value /dev/vdb2)" = "$uuid" ] || exit 65
if [ -f "$CONTROL/installed-first-pass.txt" ]; then
  grep -q 'rootflags=subvol=@restored' /proc/cmdline || exit 66
  [ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 67
  [ ! -e /etc/devnet-qa-hotfix-marker ] || exit 68
  [ ! -e /var/tmp/devnet-hotfix-home ] || exit 69
  printf '%s\n' INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS > "$CONTROL/installed-restored-pass.txt"
  printf '%s\n' APP_FIXTURE_BTRFS_ROLLBACK_PASS > "$CONTROL/app-snapshot-rollback.txt"
  sync
  exit 0
fi
grep -q 'rootflags=subvol=@ ' /proc/cmdline || exit 70
[ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 71
printf '%s\n' INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS > "$CONTROL/installed-first-pass.txt"
test -s "$CONTROL/candidate.zip"
test -s "$CONTROL/guest_hotfix_qa.py"
mkdir -p /var/tmp/devnet-hotfix-home
chown nobody:nobody /var/tmp/devnet-hotfix-home
chmod 0700 /var/tmp/devnet-hotfix-home
# App candidate code runs solely as unprivileged nobody, never root.
if runuser -u nobody -- env HOME=/var/tmp/devnet-hotfix-home \
  XDG_CONFIG_HOME=/var/tmp/devnet-hotfix-home/.config \
  DEVNET_QA_VM=1 python3 "$CONTROL/guest_hotfix_qa.py" \
  APP_TOKEN "$CONTROL/candidate.zip" SHA_TOKEN \
  /var/tmp/devnet-hotfix-home /var/tmp/devnet-hotfix-home/hotfix-result.json; then
  echo HOTFIX_FIXTURE_GUEST_PASS
else
  echo HOTFIX_FIXTURE_GUEST_FAILED
fi
test -s /var/tmp/devnet-hotfix-home/hotfix-result.json
cp /var/tmp/devnet-hotfix-home/hotfix-result.json "$CONTROL/hotfix-result.json"
printf '%s\n' created-during-hotfix > /etc/devnet-qa-hotfix-marker
mkdir -p /mnt/devnet-btrfs-top
mount -o subvolid=5 /dev/vdb2 /mnt/devnet-btrfs-top
[ -d /mnt/devnet-btrfs-top/@known-good ] || exit 72
printf '%s\n' simulated-broken > /etc/devnet-qa-marker
btrfs subvolume snapshot /mnt/devnet-btrfs-top/@known-good /mnt/devnet-btrfs-top/@restored
[ "$(cat /mnt/devnet-btrfs-top/@restored/etc/devnet-qa-marker)" = known-good ] || exit 73
grep -F 'linux /@/boot/' /boot/grub/grub.cfg
sed -i 's|/@/boot/|/@restored/boot/|g; s|rootflags=subvol=@ |rootflags=subvol=@restored |' /boot/grub/grub.cfg
grep -q 'rootflags=subvol=@restored' /boot/grub/grub.cfg || exit 74
printf '%s\n' BTRFS_RESTORED_ENTRY_WRITTEN > "$CONTROL/restore-grub-prepared.txt"
sync
systemctl reboot
