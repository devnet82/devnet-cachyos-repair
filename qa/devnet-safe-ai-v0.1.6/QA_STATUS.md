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
