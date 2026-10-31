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
