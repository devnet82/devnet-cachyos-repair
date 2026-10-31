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
