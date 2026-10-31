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

## Corrected GitHub-FIRST native CachyOS 70/70 + independent evidence PASS — 31 October 2026

The user's GitHub screenshot shows SUCCESS for all 3 jobs. Independently checked exact run [41235364596](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41235364596) using GitHub job state and the actual GitHub Actions logs:
1. `verify-exact-private-safe-package`: **success**. Deterministic reconstructed candidate hash `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6`.
2. `real-cachyos-vm-70-regressions`: **success**. Actual CachyOS ISO checksum verified, QEMU guest booted, non-root `devnet-qaisolated` test runner actually executed. Job log contains `GUEST_INSTALL_SCRIPT_STARTED` and `GITHUB_CACHYOS_70_OF_70_TESTS_PASS_LIMITED_FULL_MASTER_QA_BLOCKED`; native bwrap filesystem/network sandbox security also passes.
3. `independent-evidence-and-scope-gate`: **success**. GitHub attestations [62179385](https://github.com/devnet82/devnet-cachyos-repair/attestations/62179385) and [62179389](https://github.com/devnet82/devnet-cachyos-repair/attestations/62179389) published to Sigstore transparency log; evidence and scope receipt artifacts captured.
This passes the required **GitHub-first CI gate only**. The independent scope explicitly states actual OpenCode/Ollama inside bwrap, 30B live switching, host installation, VM/host Master QA remain NOT TESTED; release BLOCKED. Next gate is live user's own CachyOS KVM QA VM, then host exact v0.1.7 integrated workflow, including fresh 9B/30B/gaming interruption/recovery, with no inheritance from v0.1.6 test results. Existing production v0.1.2 remains unchanged.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## User's own actual CachyOS QA VM — exact v0.1.7 70/70 regression PASS, 31 October 2026

After successful GitHub-first native CachyOS QEMU 70/70 and signed independent evidence gate, user executed a fish-compatible one-line Python host-to-VM transfer/regression command:
- Host verified downloaded candidate ZIP SHA256 `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6`.
- SSH to existing `devnet@192.168.122.71`, `BatchMode=yes`, transferred the exact archived bytes over stdin to isolated ephemeral test directory, re-verified SHA256 and CRC, explicitly required non-root VM SSH user, and ran `test_devnet_safe_ai_v0.1.7.py` locally on the VM without installation.
- User provided raw output with actual transactional upgrade/rollback tests, tamper/symlink/refusal scenarios `... ok`, followed by `Ran 70 tests in 1.787s`, `OK`, `LOCAL CACHYOS VM 70/70: PASS` and successful command return.
- A `ResourceWarning` appeared in the test output; it did not cause test failure. Preserve as non-fatal issue, investigate if potentially meaningful.
- This is **VM regression-scope PASS only** from user-provided execution evidence. GitHub-first test ordering observed. No claim of OpenCode live model, full GUI/tray, live gaming, VM installed upgrade, release acceptance or fresh v0.1.7 Ollama 9B→30B host test. Existing host v0.1.2 installation untouched.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## User-host exact v0.1.7 uninstalled doctor PASS — 31 October 2026

User executed SHA256-checked exact v0.1.7 ZIP `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6` as extracted standalone uninstalled source with `doctor` on host CachyOS. Raw output:
```
PASS: OpenCode sandbox, offline network, private workspace, models and subagent config
V0.1.7 HOST DOCTOR: PASS
```
Check returned exit 0; the installed production v0.1.2 was not upgraded or modified. **Host doctor PASS only**, not actual live 9B/30B delegation, real gaming interruption, full security or host Master QA approval. Next: exact v0.1.7 fresh live required 30B delegation and model loading/unloading; do not inherit v0.1.6 PASS.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Exact v0.1.7 real host 9B→30B→9B delegation + idle unload — PASS, with report-grounding issue — 31 October 2026

User ran hash-verified v0.1.7 candidate (SHA256 `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6`) extracted temporarily, uninstalled, through live OpenCode. Required `devnet-heavy` called with instructions: "review a C++ counter race condition, explain the safe mutex fix, and report its findings. Do not edit files." Output:
- `✓ Review C++ counter race condition Devnet-Heavy Agent`; substantive coordinator summary returned.
- `DEVNET RESULT AUDIT: PASS (new tool failures: 0; completed delegations: 1 ; required: True )`
- `RUN EXIT: 0`
- 1-second polling of real `ollama ps`: `MODELS OBSERVED: ['qwen3-coder:30b', 'qwen3.5:9b']`, `30B LOAD OBSERVED: True`.
- After an additional 40s idle, `MODELS AFTER IDLE:` header only, no models; `V0.1.7 LIVE MODEL QA: PASS`.
**Actual model delegation and idle resource recovery: PASS on exact v0.1.7.** This does not establish absence of transient overlap or all GPU memory usage.

**Important content-grounding concern (not to count as PASS):** Despite a conceptual prompt with **no provided input C/C++ files**, the assistant's generated report claims `Files Analyzed: counter_problematic.c, counter_fixed.c`, mentions line numbers and a specific expected 200,000 increments. Those are **unsubstantiated claims** (unless actual files and reads are independently proved). No file-read trace is contained in supplied output. The deterministic audit confirms *real subagent invocation*, not factual grounding or real file review. Record this as **UNVERIFIED/possible hallucination**, investigate separately; no claim that a real source review passed. The user demands no simulated evidence or false PASS.
- Remaining release gates include fresh v0.1.7 real file writing, mid-task actual gaming interruption vs manual sentinel, fully-integrated upgrade/rollback, resolution or explicit fail-closed handling of native non-Steam gaming detection.
- Production installed v0.1.2 unchanged.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Host exact v0.1.7 real 9B sandboxed file-write QA PASS — 31 October 2026

User executed exact v0.1.7 SHA-verified ZIP uninstalled in a temporary directory, requested a one-line text file in the established private workspace using real OpenCode.
Output from live run:
```
> build · qwen3.5:9b
← Write DEVNET_V017_FILE_QA.txt
Created file successfully: DEVNET_V017_FILE_QA.txt
DEVNET RESULT AUDIT: PASS (new tool failures: 0; completed delegations: 0 ; required: False )
RUN EXIT: 0
REAL WORKSPACE FILE WRITE: PASS
```
Command independently checked regular non-symlink file `/mnt/devnet-ai/projects/devnet-ai-safe-workspace/DEVNET_V017_FILE_QA.txt` exists and contains exactly `DEVNET_V017_REAL_WRITE_PASS` (newline-insensitive). Earlier precondition checked target did not already exist; no overwrite. This is **real sandbox write PASS on exact v0.1.7**. The message "No other files were modified" was **model assertion only**, not independently checked; do not count that as verified. Normal 9B run properly required no 30B delegation, unlike earlier separate required-delegation PASS.
Remaining: fresh v0.1.7 mid-inference gaming guard stop/unload from actual in-use model and auto-game launch, integrated upgrade/rollback of real installed v0.1.2 with private-state integrity, full release Master QA and native non-Steam game detection gap.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Exact v0.1.7 real No Man's Sky gaming start block — PASS, 31 October 2026

User launched a real Steam/Proton No Man's Sky game and ran the SHA256-pinned exact v0.1.7 source extracted from the downloaded ZIP with a live `run "Reply with TEST"` command. Harness independently required both `gaming-on` and `stop-all` manual flags **absent**; expected exit code 2 and specific guard output. Raw user output:
```
BLOCKED: Gaming/stop-all is active

V0.1.7 REAL GAME START BLOCK: PASS
```
Thus **real game detection and fail-closed refusal to start AI on exact v0.1.7 PASS**; no flag-based simulation and no installed launch change. This establishes startup gaming block but **not** mid-inference automatic game activation, process termination and 9B/30B model unload for v0.1.7, native non-Steam game coverage, or production integrated upgrade/rollback acceptance. No release permission. `MASTER_QA=BLOCKED; RELEASE_APPROVED=false.`

## User host v0.1.7 mid-task guard precondition blocked — 31 October 2026
User's attempt to run exact candidate mid-inference gaming-flag stop/unload test terminated safely before OpenCode launch at `assert not m.gaming_now(), "CLOSE GAMES FIRST"`. This means trusted host game guard returned True before the run. The test did **NOT** create its temporary gaming-on flag, did **NOT** launch an AI job, and collected **NO** inference/stop/unload results. It is **BLOCKED precondition**, not PASS or FAIL for the intended mid-task test. Next: read-only inspect manual flags plus matched /proc process names without printing full arguments or altering any processes. No installed launch change. MASTER_QA=BLOCKED; RELEASE_APPROVED=false.

## Exact v0.1.7 user-host genuine mid-inference stop and Ollama model unload — PASS (manual sentinel), 31 October 2026

User retried SHA256-verified exact downloaded v0.1.7 candidate uninstalled, after real game activity cleared, with running OpenCode 9B, and temporary `~/.config/devnet-qa-automation/gaming-on` sentinel created **only after** an active `qwen3.5:9b` was actually seen in real `ollama ps`; sentinel then removed by test's cleanup.
User-provided raw runtime output:
```
MODEL ACTIVE BEFORE STOP: True
STOP EXIT: 2
MODEL UNLOADED: True
GUARD MESSAGE:
> build · qwen3.5:9b
BLOCKED: Gaming detected; sandbox stopped and models unloaded
V0.1.7 MID-TASK INTERRUPTION: PASS
```
**PASS** for real active 9B inference stopped by flag and no resident Ollama models ~3 seconds after stop. Exit code 2 confirms fail-closed behaviour. This does **not** establish automatic game-process detection *during* active inference (real No Man's Sky active launch before start was independently PASS), actual VR start, or a 30B interruption mid-delegation. Installed host v0.1.2 unchanged; required integrated upgrade/rollback and release evidence still pending. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## User-host real v0.1.7 integrated upgrade and rollback commands — scratch HOME PASS, 31 October 2026

User ran SHA256 verified exact `v0.1.7` ZIP `46134abe84b13ef4847e24183f6710092448e6c8409dd4b1a5991e6b7b343ff6` uninstalled in a temporary HOME, with a regular file byte-for-byte copy of the real installed v0.1.2 launcher (SHA256 `3cae3df60b657744740c69649469a4eb495f6a9659d4d5557a4cae4a94dcebce`) and the trusted gaming-guard agent copy.
- Real v0.1.7 `upgrade` command exit 0, printed `UPGRADE PASS: /tmp/.../.local/bin/devnet-safe-ai`. Scratch target bytes independently compared against exact v0.1.7 source, **PASS**.
- Integrated backup location `/tmp/.../.local/share/devnet-safe-ai/launcher-backups/devnet-safe-ai-v0.1.2-original.py`, independently compared original bytes, **PASS**.
- Real upgraded launcher `rollback` command exit 0, printed `ROLLBACK PASS: verified v0.1.2 original restored`. Scratch target independently verified original bytes and executable permission mode, **PASS**.
- Independently verified host's existing `~/.local/bin/devnet-safe-ai` bytes unchanged: `INSTALLED V0.1.2 UNCHANGED: PASS`.
- User-reported harness output: `UPGRADE EXIT: 0`, `INTEGRATED UPGRADE AND BACKUP: PASS`, `ROLLBACK EXIT: 0`, `INTEGRATED ROLLBACK: PASS`, `INSTALLED V0.1.2 UNCHANGED: PASS`.
**Scope:** This is actual CLI-driven upgrade/rollback on a scratch HOME with real filesystem and isolated state; **not** a production installation test, desktop shortcut integration, a machine crash/power-loss durability demonstration, or full independent Master QA acceptance. Full v0.1.7 release approval still requires automatic *real game launch mid-inference* interruption, investigation of invented unverified file-analysis claims and any other applicable integration checks. Do not claim 100% verified PASS. Original production v0.1.2 still installed. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**
