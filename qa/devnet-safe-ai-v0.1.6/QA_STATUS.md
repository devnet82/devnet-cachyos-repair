# Devnet Safe AI v0.1.6 — QA BLOCKED

**Purpose:** fix exact v0.1.5 host acceptance failure: an explicit `Delegate to the real devnet-heavy specialist` prompt was answered by 9B alone, yet `DEVNET RESULT AUDIT: PASS (completed delegations: 0)` returned exit code 0.

## Exact candidate and unchanged baseline
- Immutable original v0.1.5 archive SHA256: `fc572e7a1e1659f409a9d3a98f4f1926535515204cd43031b9bee15198109512`
- Exact v0.1.6 candidate SHA256: `5dda7c3355d754efe07f2d44a89ff65d9843d32fffc71e0bfdb80923bec69a25`
- Deterministic rebuild from original v0.1.5 with compressed source/test delta; original ZIP and installed launcher never modified.

## Narrow change
- When user explicitly starts a run prompt with an imperative requesting `devnet-heavy` delegation (Delegate/Invoke/Call/Use/Ask), result audit **requires at least one successful substantive subagent call**, failing closed otherwise.
- `run --require-heavy "prompt"` also forces the requirement regardless of wording; arguments `agent`, `description`, `prompt` are explicitly reminded to the 9B coordinator.
- Ordinary 9B-only tasks are unchanged. Negated and merely descriptive phrases do not automatically force 30B.
- Zero-subagent runs no longer earn a misleading PASS for explicitly mandatory specialist requests. This is only a structural task requirement, not semantic verification. No shell/web/GitHub/tool access additions, no installed OpenCode/Ollama changes.

## Evidence
- Local **55/55** full regression tests PASS on exact candidate (46 previous rerun + 9 new dedicated-to-required-delegation and fail-closed checks).
- GitHub-hosted genuine CachyOS VM full fresh 55-test/security suite, independent evidence gate: [run 41230865437](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41230865437) **PENDING** at creation.
- Real user-host candidate v0.1.6 doctor, live 9B Write, 30B handoff and model unloading, gaming/VR pause, installation/rollback and full Master QA: **NOT TESTED**. Historical v0.1.5 PASS does not count for v0.1.6.
- **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.** No production installation.

## Verified GitHub-first v0.1.6 VM result — 31 October 2026

- [workflow run 41230865437](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41230865437): **ALL 3 JOBS SUCCESS**, including deterministic v0.1.6 exact-archive SHA256 preflight, genuine booted native CachyOS QEMU/KVM guest **55/55 full fresh regression tests PASS** (46 previous plus 9 new required-delegation checks), real unprivileged Bubblewrap security scope, independent evidence/scope gate and signed attestations. Exact candidate SHA256 verified: `5dda7c3355d754efe07f2d44a89ff65d9843d32fffc71e0bfdb80923bec69a25`.
- No user host v0.1.6 live test yet. Mandatory specialist requirement is checked in mocked unit tests; real 9B→30B model run and GPU unloading still need direct host validation for this exact revision.
- **GITHUB_FIRST_SCOPE=PASS_LIMITED; MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Genuine user-host mandatory 30B delegation — 31 October 2026

User ran the exact pinned v0.1.6 archive on real CachyOS (preflight `ZIP VERIFIED`, full SHA256 `5dda7c3355d754efe07f2d44a89ff65d9843d32fffc71e0bfdb80923bec69a25`) without replacing installed launcher:
- `doctor` **PASS**: OpenCode sandbox, offline network, private workspace, model and subagent configuration.
- `run --require-heavy "Delegate to the real devnet-heavy specialist..."`: real UI showed `✓ Review counter increment race Devnet-Heavy Agent`; 9B coordinator received and summarised specialist findings. `DEVNET RESULT AUDIT: PASS (new tool failures: 0; completed delegations: 1 ; required: True )`, `TEST EXIT: 0`. **Specific v0.1.5 missed-delegation regression now PASS on live host.**
- Correct explanation: two +1 increments from 5 = 7 when synchronized, lost update yields 6; mutex protective critical section; no benchmark results claimed.
- **Not established by this run**: actual 30B model load/unload telemetry (no `ollama ps` during or after), real game/VR interruption, full install/upgrade/rollback, recovery, Master QA full evidence. Structural subagent audit does not independently validate program correctness in other tasks.
- Keep initial GitHub 55/55 tests + evidence gate PASS_LIMITED. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.

## Live user-host v0.1.6 gaming-start guard — 31 October 2026

User executed the exact SHA-verified candidate with trusted local `~/.config/devnet-qa-automation/gaming-on` sentinel created only for the test and registered for removal at normal Python exit. Result: `EXIT: 2`, `MESSAGE: BLOCKED: Gaming/stop-all is active`, `GAMING START BLOCK: PASS`. This is **genuine host gaming-start guard PASS** (simulated sentinel; not a real launched game). Mid-task process-group termination / real Ollama unloading after interruption, actual gaming detector and VR remain **NOT TESTED**. **MASTER_QA=BLOCKED, RELEASE_APPROVED=false**.

## Live user-host v0.1.6 mid-task gaming sentinel interrupt — 31 October 2026

Exact previously SHA-verified v0.1.6 candidate ran on real CachyOS with 9B OpenCode active for an extended analysis request. User created the existing `~/.config/devnet-qa-automation/gaming-on` sentinel during the running process. Observed:
- `> build · qwen3.5:9b`
- `AI ACTIVE: triggering gaming mode`
- `BLOCKED: Gaming detected; sandbox stopped and models unloaded`
- `MID-TASK EXIT: 2`
- `MID-TASK GAMING STOP: PASS`
- `ollama ps` immediately afterwards: empty model list.

**PASS within tested scope:** genuine running launcher reacted to mid-task manual sentinel activation, exited 2, and Ollama reported no resident models afterward. This demonstrates interruption and unload on the user's actual host; the exact physical game/VR detection integration was NOT exercised. Other pending tests include actual automatic game-flag triggering, live 30B interruption/unload, install/upgrade/uninstall/rollback, broader Master QA/evidence and user final acceptance. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Host gaming detector integration code-path review — 31 October 2026

User read actual host `~/.local/lib/devnet-qa-automation/agent.py` lines 69–89: `gaming_now(proc_root=Path("/proc"))` returns True for MANUAL_PAUSE or STOP_FILE; fails closed when /proc absent or unreadable; iterates per-process `comm` and `cmdline` and calls `process_is_game(comm, cmd)` on each. The exact v0.1.6 ZIP code `gaming_now()` checks `~/.config/devnet-qa-automation/{stop-all,gaming-on}` and loads this trusted agent module on the host via `importlib.util.spec_from_file_location`, invoking its `gaming_now()` (fails closed on errors), at launch and every ~0.75 s during run. Thus static linkage/invocation path to existing automatic process scanner is confirmed; actual matcher definitions `process_is_game` and running Steam/Proton/VR game automatic detection still NOT REVIEWED/NOT TESTED. Manual sentinel mid-task PASS is not real Steam/VR proof. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Review of host `process_is_game()` rules, QA agent v0.4.4 — 31 October 2026

User supplied actual `agent.py` lines 1–70. `process_is_game(comm,cmdline)` returns true if the lowercased exact `comm` is in `GAME_NAMES` (`gamescope`, wine launchers/wineserver, `vrserver`/`vrcompositor`/`vrmonitor`, `steamvr`, `wivrn-server`, etc), if lowercased command line contains `/steamapps/common/` or `/steamapps/compatdata/`, or if name ends in `.exe` except `explorer.exe`, `services.exe`, `steam.exe`. Idle `steam`, `steamwebhelper`, Discord are not flagged by name alone.
**Static matching caveats / new acceptance tests needed**:
- Native games whose names/argv do not include any listed process name/Steam path, such as system-packaged `supertuxkart`, will **NOT be detected automatically**. This is a genuine coverage gap for the requirement "pause while gaming", not yet addressed by v0.1.6.
- Auxiliary `.exe` processes (except the three exclusions), `wineserver` and some VR services may be detected despite no active play (false pauses). Steam content paths in unrelated CLI arguments could also be detected, so process-name vs argument matching needs real checks and false-positive scenarios.
- Code review is **NOT** an actual Steam/Proton/VR game launch test or 30B model-unload proof. Do not mark automatic game recognition as PASS until real integration evidence.
- For process-matcher acceptance, print only synthetic test names and Boolean results; do not log real /proc command lines (privacy).
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## User-host synthetic automatic gaming matcher acceptance — 31 October 2026

User executed exact installed agent v0.4.4 `process_is_game` against five representative synthetic process names/cmdlines, plus `gaming_now()` on the real host:
- Idle Steam: NOT DETECTED (**expected negative PASS**, avoids pausing for launcher)
- Steam game under `/steamapps/common/`: DETECTED (**PASS**)
- Proton executable `.exe`: DETECTED (**PASS**)
- SteamVR `vrcompositor`: DETECTED (**PASS**)
- Native Linux non-Steam `supertuxkart` binary with `/usr/bin/supertuxkart`: NOT DETECTED (**coverage FAIL**)
- `CURRENT GAMING DETECTOR: False` while not playing (plausible, not independently verified game state).

**Scope**: tests exercise matcher function with representative synthetic inputs; not actual games being launched. Confirmed native Linux outside-Steam miss. Do not relax false-positive protections by treating arbitrary non-Steam GUI, GPU or full-screen processes as games; preserve idle Steam false. Candidate v0.1.6 imports this installed agent guard, so fixing native coverage requires a **separately reviewed & fully tested candidate change** to trusted host detector or narrow Safe AI extension. No existing files modified by this diagnostic. MASTER_QA BLOCKED; no approval.

## User-host real game-detector observation — 31 October 2026

After assistant instructed the user to launch an actual Steam game, user executed the unchanged native QA agent v0.4.4 `gaming_now()` on their CachyOS host and observed **`REAL GAME DETECTED: True`**. This is positive **in-situ gaming guard activation**, versus earlier `False` when no game was running. However `gaming_now` also returns True for `gaming-on` and `stop-all` manual sentinels and for non-game heuristic matches, so **automatic match specifically attributable to a running game's /proc entry is not yet independently established**. Next check: inspect active sentinels and matched /proc process *names only*, without printing command lines or private arguments. Original native non-Steam coverage hole remains; no installed launcher changes. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## User-host automatic gaming detection confirmed with real Steam/Proton process — 31 October 2026

User kept a real game (No Man's Sky, `NMS.exe`) running and executed a read-only verification against the currently installed v0.4.4 QA agent's `process_is_game` and `gaming_now`.
- `MANUAL FLAGS ACTIVE: False` (both `gaming-on` and `stop-all` absent).
- `MATCHED GAME PROCESSES:` `NMS.exe`, `lsass.exe`, `plugplay.exe`, `pv-adverb`, `python3`, `reaper`, `rpcss.exe`, `srt-bwrap`, `steam.exe`, `svchost.exe`, `tabtip.exe`, `winedevice.exe`, `wineserver`, `xalia.exe`.
- `AUTOMATIC DETECTION: True`; `CURRENT GAMING DETECTOR: True`.
This **confirms a genuine game process is matched automatically with manual override absent**, including the actual game's executable `NMS.exe`. Auxiliary `python3`, `reaper`, `srt-bwrap`, `steam.exe` and Proton service processes are also matched in this real gaming session, likely via Steam executable path/arguments; **false-positive game-stopped/idle detection remains UNVERIFIED**. The test establishes detector activation during real gaming, but not yet whether game launch automatically interrupts a concurrently-running AI (the latter was earlier tested only by manual sentinel). Native non-Steam game coverage still FAIL/NOT IMPLEMENTED. No candidate/installation changes. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Real Steam/Proton game-exit detector recovery — 31 October 2026

After fully closing No Man's Sky on the user's live CachyOS system, user ran the unchanged agent v0.4.4 read-only detector plus independent process matcher sweep:
- `DETECTOR AFTER GAME EXIT: False`
- `REMAINING MATCHES: []`
- Previously, while No Man's Sky was running, `gaming_now=True`, `NMS.exe` and Proton processes positively matched with manual override flags absent. Together these observations confirm **automatic gaming detector activity during the game and cessation after exit** for this particular real game: **PASS**.
- This does **not** demonstrate the exact launcher reacting to an *actual* game launch mid-run, 30B resident-model unload after delegation, gaming coverage for native non-Steam games, or installation/upgrade/rollback. Keep the same candidate unmodified and **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.

## Genuine user-host 9B / 30B resident model and idle unload observation — 31 October 2026

User ran SHA-verified exact v0.1.6 candidate on CachyOS in a subprocess with `run --require-heavy`; a separate foreground monitor polled real `ollama ps` every second for up to 240 seconds while the run was active, then waited 40 seconds after successful exit.
- Real OpenCode showed `✓ Explain mutex vs atomic counter Devnet-Heavy Agent`, then returned coordinator summary.
- `DEVNET RESULT AUDIT: PASS (new tool failures: 0; completed delegations: 1 ; required: True )`.
- `RUN EXIT: 0`.
- `MODELS OBSERVED: ['qwen3-coder:30b', 'qwen3.5:9b']`.
- `30B LOAD OBSERVED: True`.
- `MODELS AFTER IDLE:` empty `ollama ps` table (no resident models), after 40 seconds.
**PASS, genuine user-host runtime:** both models individually observed loaded, required 30B delegated and returned, and both absent after 40-second idle. Polling every second does not establish *absence of transient simultaneous residency*, exact RAM/VRAM peak, or which model ran on CPU/GPU. Do not claim strict zero overlap or zero total GPU use. Remaining open scope: actual game launch while inference active, real VR activity, non-Steam native-game detection gap, installation/upgrade/rollback and complete independent Master QA. Candidate and installed launcher unchanged; RELEASE_APPROVED=false, MASTER_QA=BLOCKED.
