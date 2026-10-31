# Devnet Safe AI v0.1.7 — QA BLOCKED

## Reason for this exact revision
The verified existing production launcher remains **v0.1.2** with SHA256 `3cae3df60b657744740c69649469a4eb495f6a9659d4d5557a4cae4a94dcebce`. The user verified 5/5 backup, interrupted-staging, atomic scratch replacement, rollback and preservation checks against the unchanged v0.1.6 candidate. However the installed v0.1.6 code had no integrated upgrade/rollback CLI, so promoting it to production would have required an unaudited manual replacement.

## Change scope
The **v0.1.7** uninstalled QA candidate introduces explicit `upgrade` and `rollback` commands: only the exact verified regular, non-symlink v0.1.2 launcher is allowed as upgrade source, an SHA-checked original backup is created without overwrite in private local state, a staged copy of the new source is written and fsynced in the launcher's directory, single atomic `os.replace` + directory fsync applied, original mode retained; rollback restores exact SHA-verified backup, refusing unknown launcher, tampered backup, root, game-active and concurrent-operation cases. Existing `install` remains fail-closed. No changes to OpenCode configs, model routing, private user workspace, web/GitHub access or Ollama.

Original immutable v0.1.6 archive SHA256: `5dda7c3355d754efe07f2d44a89ff65d9843d32fffc71e0bfdb80923bec69a25`.

**New exact v0.1.7 ZIP SHA256: `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6`.** Deterministic rebuild from pinned v0.1.6 ZIP and separately staged compressed source and test delta.

## Tests and remaining gates
- Local Linux **70/70 fresh tests PASS** on exact reconstructed candidate, in a non-root user process (55 original tests rerun plus 15 upgrade/rollback tests exercising real scratch filesystem, backup corruption, interrupted replace, mode preservation, symlink, lock, root and gaming guard failures). Previous accidental execution of the whole suite as root was correctly blocked by the new updater's refuse-sudo behaviour and **not** counted as pass; rerun non-root passed.
- GitHub-first real native CachyOS QEMU VM all-applicable unit/security and updater regression plus independent evidence/scope gate: [workflow 41234072326](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41234072326), **PENDING** at time of staging.
- Exact v0.1.7 user-host test, integrated rollback CLI on a scratch HOME, 9B file write, 30B delegation and model unloaded, game interruption, actual installer/upgrade/rollback/recovery, final user acceptance: **NOT TESTED**. Prior v0.1.6 successes do not substitute for fresh v0.1.7 execution.
- Power-cut/kernel panic and uncooperative filesystems cannot be simulated by unit tests; label limitations.
- Automatic native Linux gaming detection outside Steam remains a known coverage gap, unchanged in this upgrade revision.

**MASTER_QA=BLOCKED. RELEASE_APPROVED=false.** User's installed v0.1.2 launcher is untouched.

## User download integrity confirmation — 31 October 2026
User reported running the exact SHA256 and ZIP integrity verifier for `~/Downloads/devnet-safe-ai-v0.1.7-QA-BLOCKED.zip` and observed `DEVNET v0.1.7 ZIP VERIFIED: PASS`. This establishes that the downloaded archive is byte-for-byte identical to pinned SHA256 `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6` and ZIP CRC check found no corruption. This is **download integrity PASS only**, not installation/runtime or release approval. GitHub-first native CachyOS run 41234166536 remains in progress as of this check, independent gate pending; installed production remains v0.1.2. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Latest corrected GitHub-first VM result — 31 October 2026
Run [41234166536](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41234166536): deterministic SHA-pinned exact archive job **success**; `real-cachyos-vm-70-regressions` **failure** in guest boot/test step (guest script started but workflow timed out without expected verifiable `native-result.json` after 10 minutes); `independent-evidence-and-scope-gate` **skipped**. The unit-test outcome inside the guest is unknown pending inspection of uploaded evidence, NOT 70/70 PASS. **Do not install or upgrade** the production launcher yet. This is *not* a claim of application failure specifically: could be boot/guest harness or test failure. User downloaded exact ZIP integrity PASS. **MASTER_QA=BLOCKED, RELEASE_APPROVED=false.**

## CI failure root-cause and test-harness-only repair, no candidate change — 31 October 2026

Downloaded and inspected *actual uploaded GitHub guest evidence* from failed runs:
- Run [41234072326](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41234072326) guest `unit-tests.log` proves `Ran 70 tests` with **7 errors** because all transactional upgrade tests were launched under root; v0.1.7 correctly refuses `os.geteuid()==0`. This is test-harness privilege mismatch, not evidence upgrade succeeds on correct user.
- Run [41234166536](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41234166536) guest `controller.log` reports real CachyOS kernel and exact ZIP PASS, then `cat: /mnt/unit-tests.log: No such file or directory`, exit 1. The corrected YAML accidentally contained literal `\\n` characters in the guest script before `useradd` and `sudo -u`, all on a shell comment line, so **neither command ran** and no test log was created. This explains missing test evidence.
- Fixed workflow *only* in commit `4a0eb51a18a52b5ca17bcd4b04a7f5edbaba3f8c`: replace escaped `\\n` tokens with real line breaks, run `useradd` then `sudo -u devnet-qaisolated python3 test_devnet_safe_ai_v0.1.7.py`. Verifies exactly one useradd and no escaped shell newline artifacts. Did **not** change v0.1.7 candidate ZIP SHA256 `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6`.
- New GitHub-first native CachyOS rerun [41235364596](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41235364596) **IN PROGRESS** at last check. Independent evidence gate pending, **do not approve/install** v0.1.7 based on failed prior runs.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**
