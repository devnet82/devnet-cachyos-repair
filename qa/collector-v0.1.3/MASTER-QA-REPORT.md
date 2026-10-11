# Devnet Installed Apps Collector v0.1.3 — Master QA (11 October 2026)

**Master release approval: BLOCKED (real user installation acceptance NOT_TESTED).**

**Completed:** exact ZIP and source SHA-256, 38 local regression tests, 11 nonroot lifecycle tests, 11 VM guest acceptance checks, fresh ZIP extraction, installed CachyOS GRUB/BTRFS snapshot recovery and reboot.

- Candidate ZIP SHA-256: `83bbdc81e46bf80f398abe10278bffd32da2435b5638d9896b605a7392cc7647`
- Collector source SHA-256: `f9c7916fe551733c4d931238428baf87dbaba4719115fecbde9b4bd69237d452`
- [Genuine installed-CachyOS KVM run](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/38161650569) — completed SUCCESS, raw guest evidence artifact preserved.
- [Source and tests](https://github.com/devnet82/devnet-cachyos-repair/tree/qa/devnet-installed-apps-collector-v0.1.3/qa/collector-v0.1.3)

## Mandatory Master QA checks

| Area | Status | Evidence / limitation |
|---|---|---|
| Candidate integrity | PASS | exact script SHA-256 verified locally, from fresh ZIP and inside installed CachyOS KVM |
| Native cachyos os | PASS | installed CachyOS x86_64, GRUB, BTRFS, disk serial and UUID guards |
| Clean install | PASS | user-only install.sh from fresh ZIP and offline CachyOS VM |
| Uninstall | PASS | user-only uninstall.sh, repeat uninstall, unrelated user application files preserved |
| Upgrade from known good | NOT_TESTED | synthetic managed v0.1.1 upgrade/backups PASS; no prior real v0.1.1 installed app existed (standalone script) |
| Rollback recovery | PASS | interrupt/failing atomic rename, safe app binary preservation, partial ZIP cleanup, BTRFS snapshot restore and reboot |
| Configuration migration | NOT_APPLICABLE | collector has no stored configuration; export excludes mutable application settings |
| Gui tray single instance | NOT_APPLICABLE | CLI-only utility; 12 concurrent independent exports with collision-free private outputs PASS |
| Doctor checks | PASS | completeness, symlink, hardlink, privacy, genuine missing-file Doctor checks |
| Services processes | NOT_APPLICABLE | no installed service/daemon, no process controls, no GUI/tray |
| Failure paths | PASS | missing app/asset, privacy flag, corrupt/unsafe path, hardlink, changed source, low disk, output permission, bad target |
| Network offline reconnect | NOT_APPLICABLE | no network access, no dependency/reconnect; VM application test ran offline |
| Permissions low disk | PASS | nonroot and 0600 zip, symlink/traversal safeguards, ENOSPC injection cleans partial file |
| Regression coverage | PASS | 38 local source tests, 11 nonroot lifecycle tests, installed VM suites and 33 exact-preview source files |
| Hardware portability | NOT_TESTED | Debian isolated filesystem + installed CachyOS KVM passed; real user PC and alternate installed paths untested |
| Security destructive guards | PASS | refuses sudo/root, no device/network/process access, safe path FDs, privacy fail closed, no source modification |
| Physical user source acceptance | NOT_TESTED | read-only collector has not run against user’s actual installed applications |
| Long run resources | NOT_TESTED | 20 repeat and 12 simultaneous exports plus 25 MB scale test passed; prolonged multi-hour monitoring not performed |

## Final QA decision

Functional and safety tests **PASS within the defined offline/fixture scope**. The remaining mandatory real-user-CachyOS source completeness/portability check and multi-hour physical acceptance were not executed, so strict release approval is **BLOCKED**. Users can use `--doctor` as a read-only on-host acceptance check before any export, but should not treat the ZIP as an approved general release until their environment is reviewed.

No sudo, network, SteamVR/Quest calls, or alteration of installed VR Stack/WayVR files were performed by the test candidate.

**Privacy:** Source code may still contain embedded secrets. Default privacy indicators prevent archive creation; any override requires local review before sharing.
