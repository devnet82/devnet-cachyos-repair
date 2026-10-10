#!/usr/bin/env bash
# Run only in a disposable QEMU CachyOS live VM.
set -Eeuo pipefail
CONTROL=/mnt/devnet-control
mkdir -p "$CONTROL"
mount -o rw /dev/vda "$CONTROL"
exec >"$CONTROL/install.log" 2>&1
onexit() { rc=$?; echo "INSTALL_SCRIPT_EXIT=$rc"; sync; }
trap onexit EXIT
printf 'PHASE=DISPOSABLE_INSTALLED_CACHYOS_SETUP\n'
cat /etc/os-release
uname -r
printf 'DISK_IDENTITIES\n'
lsblk -o NAME,SIZE,MODEL,SERIAL,FSTYPE,MOUNTPOINT
# Refuse accidental writes to a device not explicitly created by this QEMU run.
actual=$(tr -d '[:space:]' </sys/block/vdb/device/serial)
[ "$actual" = 'DEVNETQAONLY' ] || { echo "FAIL: disk guard expected DEVNETQAONLY, got $actual"; exit 41; }
[ "$(blockdev --getsize64 /dev/vdb)" = 12884901888 ] || { echo 'FAIL: 12GiB disk size guard'; exit 42; }
[ ! -e /dev/vdb3 ] || { echo 'FAIL: target unexpectedly has extra partition'; exit 43; }
if command -v sgdisk >/dev/null; then
  sgdisk --zap-all /dev/vdb
  sgdisk -n 1:2048:+2M -t 1:ef02 -c 1:DEVNET_BIOS_BOOT /dev/vdb
  sgdisk -n 2:0:0 -t 2:8300 -c 2:DEVNET_BTRFS /dev/vdb
elif command -v parted >/dev/null; then
  parted -s /dev/vdb mklabel gpt
  parted -s /dev/vdb mkpart primary 1MiB 3MiB
  parted -s /dev/vdb set 1 bios_grub on
  parted -s /dev/vdb mkpart primary btrfs 3MiB 100%
else
  echo 'BLOCKED: Neither sgdisk nor parted available in ISO'
  exit 44
fi
partprobe /dev/vdb || true
udevadm settle
for n in $(seq 1 20); do test -b /dev/vdb2 && break; sleep 1; done
test -b /dev/vdb2
mkfs.btrfs -f -L DEVNET_INSTALLED_QA /dev/vdb2
mkdir -p /mnt/devnet-root /mnt/devnet-top
mount /dev/vdb2 /mnt/devnet-top
btrfs subvolume create /mnt/devnet-top/@
mount -o subvol=@,compress=zstd /dev/vdb2 /mnt/devnet-root
ROOT=/mnt/devnet-root
mkdir -p "$ROOT/boot" "$ROOT/etc"
ls /etc/pacman.d | head
# Native package installation from the authentic CachyOS live environment.
# Never do a partial system upgrade against the host/user PC.
if command -v nmcli >/dev/null; then nmcli -t dev status || true; fi
ping -c 1 -W 3 1.1.1.1 || true
if ! timeout 780 pacstrap -K "$ROOT" base linux-cachyos-lts grub btrfs-progs networkmanager sudo python unzip cachyos-hooks; then
   echo 'BLOCKED: Native CachyOS pacstrap failed (inspect network/package logs)'
   exit 45
fi
KERNEL=$(find "$ROOT/boot" -maxdepth 1 -type f -name 'vmlinuz-*' -printf '%f\n' | head -n1)
INITRD=$(find "$ROOT/boot" -maxdepth 1 -type f \( -iname '*initramfs*.img' -o -iname '*initrd*.img' \) -printf '%f\n' | head -n1)
if [ -z "$KERNEL" ] || [ -z "$INITRD" ]; then
   echo 'BLOCKED: Installed kernel/initramfs absent. Listing /boot:'
   ls -la "$ROOT/boot"
   exit 46
fi
# Keep the installed instance recognisably CachyOS, not a rebranded Arch root.
if ! grep -Eq '^ID=cachyos$' "$ROOT/etc/os-release"; then
   echo 'BLOCKED: native pacstrap root did not identify as CachyOS'
   cat "$ROOT/etc/os-release"
   exit 47
fi
UUID=$(blkid -s UUID -o value /dev/vdb2)
cat > "$ROOT/etc/fstab" <<EOF
UUID=$UUID / btrfs subvol=@,compress=zstd,rw 0 0
EOF
printf '%s\n' known-good >"$ROOT/etc/devnet-qa-marker"
mkdir -p "$ROOT/usr/local/sbin" "$ROOT/etc/systemd/system/multi-user.target.wants"
cp "$CONTROL/installed-boot-qa.sh" "$ROOT/usr/local/sbin/devnet-installed-boot-qa.sh"
chmod 0755 "$ROOT/usr/local/sbin/devnet-installed-boot-qa.sh"
cat > "$ROOT/etc/systemd/system/devnet-installed-qa.service" <<EOF
[Unit]
Description=Devnet disposable CachyOS installed-system QA
After=local-fs.target
[Service]
Type=oneshot
ExecStart=/usr/local/sbin/devnet-installed-boot-qa.sh
TimeoutStartSec=180
[Install]
WantedBy=multi-user.target
EOF
ln -s ../devnet-installed-qa.service "$ROOT/etc/systemd/system/multi-user.target.wants/devnet-installed-qa.service"
# GRUB is installed to the QEMU-only 12GiB disk, never the host disk.
arch-chroot "$ROOT" grub-install --target=i386-pc --recheck /dev/vdb
mkdir -p "$ROOT/boot/grub"
cat > "$ROOT/boot/grub/grub.cfg" <<EOF
set timeout=1
set default=0
menuentry 'Devnet disposable CachyOS BTRFS' {
  insmod part_gpt
  insmod btrfs
  search --no-floppy --fs-uuid --set=root $UUID
  linux /@/boot/$KERNEL root=UUID=$UUID rootflags=subvol=@ rw console=ttyS0,115200 systemd.unit=multi-user.target
  initrd /@/boot/$INITRD
}
EOF
cat "$ROOT/boot/grub/grub.cfg"
# Make read-only known-good snapshot only after configuration has completed.
btrfs subvolume snapshot -r /mnt/devnet-top/@ /mnt/devnet-top/@known-good
printf '%s\n' "$UUID" >"$CONTROL/target-btrfs-uuid.txt"
printf '%s\n' INSTALLED_BTRFS_GRUB_PREPARED >"$CONTROL/install-ready.txt"
sync
printf 'INSTALLED_BTRFS_GRUB_PREPARED\n'