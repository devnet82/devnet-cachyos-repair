# Devnet Safe AI v0.1.4 — QA BLOCKED (31 October 2026)

Branch: `qa/devnet-safe-ai-v0.1.4-delegation-fix`. Original pinned v0.1.3 ZIP SHA256: `8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b`. Exact v0.1.4 reconstructed ZIP SHA256: `deed961ee9c2c7be57c0a1e114ecba9d4250dd57041059eb29939f7b5c062781`.

## Root-cause evidence
User's real v0.1.3 OpenCode 2.1.4 host session shows 21 qwen3-coder:30b messages, 13,682 output tokens (recent-window aggregate), 20 heavy-agent text blocks, and five coordinator subagent calls. Of those, three were marked completed with nonempty recorded return bodies and two were errors: `Tool execution interrupted: subagent` and `Invalid arguments for tool "subagent": description: Missing key`. The 9B coordinator tried the skill loader as a fallback and reported fabricated/unverified analysis, finishing `AI EXIT: 0`. Delegation end-to-end **FAILED**.

## Change scope
- Add explicit required OpenCode V2 subagent tool fields `agent`, `description`, `prompt`; prohibit model override and invalid skill fallback.
- Add specialist system instructions to finish with substantive plain-text analysis rather than tool-only replies; 12-step budget.
- Add a **read-only, per-run OpenCode SQLite tool-state audit** for CLI `run`. Refuse success if a new tool call has status error, a subagent does not complete or the returned child result is empty; do not print private prompts. This does not validate semantic correctness, and interactive `chat` still lacks post-run audit.
- Preserve private workspace, current launcher (NOT replaced), Ollama gateway, shell/web/GitHub denials, game pause and exact original baseline.

## Evidence
- Fresh **43/43 offline regressions PASS** in independent local container (35 previous tests rerun plus 8 new contract/audit tests), no live OpenCode/Ollama.
- Exact candidate reconstructed by `rebuild.py` from SHA-verified v0.1.3 baseline and staged compressed source/test delta; both independent local builds match `deed961ee...`.
- GitHub-hosted real CachyOS QEMU/KVM test and independent evidence gate: workflow [41227839930](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41227839930), result **PENDING** at staging of this status.
- Live GitHub hosted OpenCode + Ollama 9B→30B and secure output return: **NOT TESTED** for v0.1.4.
- User host exact v0.1.4 `doctor`, real subagent return, installer/rollback, safety and gaming interruption: **NOT TESTED**.
- Persistent memory, real app GUI/QA workflow, user final acceptance: **NOT TESTED**.

**MASTER_QA=BLOCKED. RELEASE_APPROVED=false. GitHub VM first; no production install.**

## GitHub-hosted exact v0.1.4 VM verification — PASS LIMITED

- Final workflow [41228164643](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41228164643) **all three jobs SUCCESS**: SHA256 verified deterministic archive rebuild, genuine booted CachyOS QEMU/KVM guest running **43/43 fresh unit/security regression checks**, unprivileged Bubblewrap isolation probes, independent evidence/scope gate, signature attestations. The guest result explicitly keeps MASTER_QA BLOCKED and RELEASE_APPROVED=false.
- The first v0.1.4 VM attempts failed in the **CI harness**, not application tests: a stale pinned QEMU-helper raw URL (404) and a mistaken QEMU machine name `q43` instead of `q35`. Repaired harness by copying SHA-matched pinned commit blob `2c30d3ae5ee9626162d6caeca7cbe44143887a51` into the QA branch, checking it out in the VM job, and restoring `q35`. The v0.1.4 candidate checksum **did not change** across corrections.
- **Scope limitation**: no actual 30B inference/handoff in the hosted VM; new host-CachyOS runtime doctor/write/delegation, active game interruption, memory unload, install and rollback remain NOT TESTED for v0.1.4. A completed unit/security test gate does not approve production release.

**GITHUB_FIRST_TESTS=PASS_LIMITED; MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**
