#!/usr/bin/env bash
# Devnet Collector Master QA v0.1.2 - disposable QEMU installed-CachyOS only.
set -Eeuo pipefail
CONTROL=/mnt/devnet-control
mkdir -p "$CONTROL"
mount -o rw /dev/vda "$CONTROL" || exit 60
exec >>"$CONTROL/installed-boot.log" 2>&1
trap 'rc=$?; echo "INSTALLED_COLLECTOR_BOOT_SCRIPT_EXIT=$rc"; sync' EXIT
[ "$(lsblk -dn -o SERIAL /dev/vda | tr -d '[:space:]')" = DEVNETCONTROL ] || exit 61
[ "$(lsblk -dn -o SERIAL /dev/vdb | tr -d '[:space:]')" = DEVNETQAONLY ] || exit 62
grep -q '^ID=cachyos' /etc/os-release || exit 63
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 64
[ "$(blkid -s UUID -o value /dev/vdb2)" = "$(cat "$CONTROL/target-btrfs-uuid.txt")" ] || exit 65
cat /proc/cmdline
if [ -f "$CONTROL/installed-first-pass.txt" ]; then
    grep -q 'rootflags=subvol=@restored' /proc/cmdline || exit 66
    [ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 67
    [ ! -e /etc/devnet-qa-collector-marker ] || exit 68
    [ ! -e /var/tmp/devnet-collector-qa-home ] || exit 69
    printf '%s\n' INSTALLED_GRUB_BTRFS_REBOOT_ROLLBACK_PASS > "$CONTROL/installed-restored-pass.txt"
    printf '%s\n' COLLECTOR_GUEST_BTRFS_ROLLBACK_PASS > "$CONTROL/app-snapshot-rollback.txt"
    sync
    exit 0
fi
grep -q 'rootflags=subvol=@ ' /proc/cmdline || exit 70
[ "$(cat /etc/devnet-qa-marker)" = known-good ] || exit 71
printf '%s\n' INSTALLED_GRUB_BTRFS_FIRST_BOOT_PASS > "$CONTROL/installed-first-pass.txt"
for n in devnet-export-installed-apps-v0.1.2.py test_collector.py guest_acceptance.py install.sh uninstall.sh VERSION; do
    test -s "$CONTROL/$n" || { echo "MISSING QA FILE: $n"; exit 72; }
done
printf '%s  %s\n' '406c752875dfd4498fcf691186e26a239db31000dbe5b147a7f6a48a1288cc6e' \
    "$CONTROL/devnet-export-installed-apps-v0.1.2.py" | sha256sum -c - || exit 73
mkdir -p /var/tmp/devnet-collector-qa-home
chown nobody:nobody /var/tmp/devnet-collector-qa-home
chmod 0700 /var/tmp/devnet-collector-qa-home
UNIT_STATUS=FAIL
if runuser -u nobody -- env HOME=/var/tmp/devnet-collector-qa-home \
    PYTHONNOUSERSITE=1 DEVNET_QA_VM=1 \
    python3 "$CONTROL/test_collector.py" -q > "$CONTROL/collector-unit-tests.log" 2>&1; then
    UNIT_STATUS=PASS
fi
cat "$CONTROL/collector-unit-tests.log"
echo "COLLECTOR_UNIT_TESTS_$UNIT_STATUS"
GUEST_STATUS=FAIL
if runuser -u nobody -- env HOME=/var/tmp/devnet-collector-qa-home \
    PYTHONNOUSERSITE=1 DEVNET_QA_VM=1 \
    python3 "$CONTROL/guest_acceptance.py" \
    "$CONTROL/devnet-export-installed-apps-v0.1.2.py" \
    406c752875dfd4498fcf691186e26a239db31000dbe5b147a7f6a48a1288cc6e \
    /var/tmp/devnet-collector-qa-home/collector-guest-result.json; then
    GUEST_STATUS=PASS
fi
test -s /var/tmp/devnet-collector-qa-home/collector-guest-result.json || exit 74
cp /var/tmp/devnet-collector-qa-home/collector-guest-result.json "$CONTROL/collector-guest-result.json"
echo "COLLECTOR_GUEST_ACCEPTANCE_$GUEST_STATUS"
printf 'UNIT=%s\nGUEST=%s\n' "$UNIT_STATUS" "$GUEST_STATUS" > "$CONTROL/collector-test-status.txt"
# Always exercise system recovery, even when app QA correctly fails closed.
printf '%s\n' simulated-collector-qa > /etc/devnet-qa-collector-marker
mkdir -p /mnt/devnet-btrfs-top
mount -o subvolid=5 /dev/vdb2 /mnt/devnet-btrfs-top
[ -d /mnt/devnet-btrfs-top/@known-good ] || exit 75
printf '%s\n' simulated-broken > /etc/devnet-qa-marker
btrfs subvolume snapshot /mnt/devnet-btrfs-top/@known-good /mnt/devnet-btrfs-top/@restored
[ "$(cat /mnt/devnet-btrfs-top/@restored/etc/devnet-qa-marker)" = known-good ] || exit 76
grep -F 'linux /@/boot/' /boot/grub/grub.cfg
sed -i 's|/@/boot/|/@restored/boot/|g; s|rootflags=subvol=@ |rootflags=subvol=@restored |' /boot/grub/grub.cfg
grep -q 'rootflags=subvol=@restored' /boot/grub/grub.cfg || exit 77
printf '%s\n' BTRFS_RESTORED_ENTRY_WRITTEN > "$CONTROL/restore-grub-prepared.txt"
sync
systemctl reboot
