# Latest full-app previews: VR Stack v0.6.135 and WayVR v0.1.38

Date: 2026-10-11. **Master QA release gate: BLOCKED.**

These are **new, separate, complete application QA previews**, not replacements for previous packages or original GitHub draft assets. The exact ZIPs were created in an isolated local container and **not uploaded to GitHub**, so no claim of exact new-ZIP execution inside installed CachyOS VM is made.

| Candidate | Exact original preview ZIP SHA-256 | Source full baseline | Further verified changes |
|---|---|---|---|
| VR Stack v0.6.135 | `888902798d190de59cc5b1271ffb19101267ec05e6bc1f819728e671f8b8c71e` | full v0.6.126 | v0.6.130 libmonado/Doctor, v0.6.132 label sync, dynamic systemd tray path, per-user lock, honest partial-rollback status |
| WayVR Watch v0.1.38 | `d03c0e8d6a95ce8903c1ddc431322d05ec5d3dd45150030d960e94e7dca4eff9` | full v0.1.28 | preserves SideQuest connection guidance, no custom HMD writes, v0.1.34 Doctor patch, OSError guard, per-user lock, honest partial-rollback status |

## Executed independent local package QA

- **7/7** shared full-installer regressions PASS, run unprivileged.
- **15/15** extended security/compatibility/rollback/portability/lock/migration/regression checks PASS, run unprivileged.
- Both final exact ZIPs extracted; Bash/Python syntax and ZIP CRC checks PASS; both user-scoped clean install, repeat install and rollback PASS in disposable HOME.
- Preserved WayVR v0.1.28 watch.xml and battery SVGs byte-identically; the archived v0.1.28 readme says it preserves the approved v0.1.18 watch layout.
- Original WayVR archived regression suite is **59 PASS / 2 FAIL** (intentional newer HMD-write suppression versus legacy HMD fallback test; omission of automatic metrics daemon enable/restart versus legacy installer test). These failures are not silently reclassified as PASS.
- Source feature gaps remain: full v0.6.127-v0.6.129 VR Stack and v0.1.29-v0.1.33 WayVR not available for direct parity tests.

## Pending acceptance — NOT_TESTED

Exact final ZIP installed in a genuine CachyOS GRUB/BTRFS KVM guest: NOT_TESTED. Current execution container is Debian 13 and has no /dev/kvm; exact new ZIP bytes were not transferred into GitHub runner. Earlier VM PASS applied to *previous original update-only ZIPs*, not these previews.

Live GTK3/GTK4 GUI/tray, WiVRn/OpenXR/SteamVR/Quest/WayVR/ADB hardware, service activation, historical real full-app upgrade and full Master QA: NOT_TESTED. Do not deploy or publish.

Candidate GitHub QA branches (metadata/report only, **no candidate ZIP attached**):
- https://github.com/devnet82/vr-stack-control/tree/qa/full-app-candidate-v0.6.135
- https://github.com/devnet82/devnet-wayvr-watch-manager/tree/qa/full-app-candidate-v0.1.38

Original working apps and GitHub drafts preserved byte-for-byte and unpublished. No commands executed on the user's CachyOS host.
