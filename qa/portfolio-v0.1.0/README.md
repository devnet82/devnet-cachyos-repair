# Devnet Portfolio Master QA v0.1.0

This isolated GitHub Actions workflow audits all seven accessible public repositories. It does not modify, install, or publish any app on your real PC. Scripts run only inside disposable GitHub Ubuntu workers.

Each populated repo gets source commit pinning, Python/Bash syntax, XML/SVG and JSON parsing, git archive CRC/safe-member checks, and pinned GitHub Release ZIP SHA-256 verification when an asset exists. Dedicated test suites: RGB v8.8 fake-HOME install/upgrade/rollback/uninstall and WayVR v0.1.14 Python functional regression tests. A missing source or release is NOT_TESTED, not PASS.

**Newer ZIPs still not accessible to GitHub CI**: Devnet RGB v8.9, VR Stack v0.6.129, ChatBox v0.1.3.131 GTK, Proton RTSP v1.76 test, Sonic Pad Auto Printer v0.1.26, CachyOS Repair v0.1.20. GitHub main is older for some apps and empty for ChatBox, Proton RTSP and wivrn-stack-control.

Physical VR Quest 3, Sonic Pad USB, RGB hardware/fans, installed Linux boot/recovery, Wayland/X11 visual GUI checks and master-release acceptance remain distinct. Existing CachyOS Repair VM evidence includes installed BIOS+GRUB+BTRFS reboot/rollback PASS: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083265759. Installed UEFI/systemd-boot is still blocked: https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38083838792.

The workflow intentionally ends with a BLOCKED 100% gate until missing app-specific evidence exists.
