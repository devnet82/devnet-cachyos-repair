# Devnet Safe AI v0.1.5 — QA BLOCKED

Built from immutable v0.1.4 archive SHA256 `deed961ee9c2c7be57c0a1e114ecba9d4250dd57041059eb29939f7b5c062781`.

Exact v0.1.5 archive SHA256: `fc572e7a1e1659f409a9d3a98f4f1926535515204cd43031b9bee15198109512`.

## Scope
- Fix STOP/PAUSE safety: immediately terminate/reap OpenCode process group on gaming interruption or guard failure **before** calling model unload. Call `ollama stop` once, rather than twice, for each interruption. Handle Ctrl+C by reaping and unloading.
- Retain all v0.1.4 OpenCode 9B→30B delegation handling, message audit and offline workspace permissions without relaxing network boundaries.
- Real process test with a disposable 60-second child verifies process gone by the moment the mock model stop handler is invoked.
- Model self-reported benchmark results still cannot be accepted as independently verified QA evidence. Semantic correctness and independent application Master QA remain separate.

## Verified evidence
- Local exact candidate ZIP integrity verified; 46/46 full tests PASS (original 43 rerun plus three new: termination order, Ctrl+C, real child process).
- **GitHub-first genuine CachyOS QEMU/KVM:** [workflow run 41229794341](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41229794341). Exact archive preflight PASS; native guest tests pending at this writing.
- Native host doctor, 9B real sandbox file write, 30B specialist handoff, gaming signal, actual `ollama stop`, idle model memory policy, model recovery and install/rollback are NOT TESTED on exact v0.1.5.
- Previously user-proven v0.1.4 live delegation is only historical reference, **not inherited PASS** for v0.1.5.

**GITHUB_FIRST=PASS_LIMITED_OR_PENDING; MASTER_QA=BLOCKED; RELEASE_APPROVED=false.** Do not install into production.

## Final GitHub-first exact v0.1.5 QA verification — 31 October 2026

- [run 41230120191](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41230120191) **ALL THREE JOBS SUCCESS**: exact SHA256 verified reproducible archive rebuild from pinned v0.1.4; real booted CachyOS QEMU/KVM guest executed fresh **46/46 regression tests PASS**, including OS child termination prior to unload, KeyboardInterrupt unload, and frozen earlier security tests; unprivileged Bubblewrap workspace isolation PASS; independent signed evidence/scope gate PASS. Archive SHA256 remained `fc572e7a1e1659f409a9d3a98f4f1926535515204cd43031b9bee15198109512`.
- Earlier [run 41229794341](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41229794341) ended FAIL **after guest had produced a 46-test native result**, because workflow assertions still expected 43 (old suite count). CI harness-only correction updated both native and independent assertions; AI candidate bytes unchanged.
- **Scope:** GitHub FIRST unit/OS-child/Bwrap checks PASS_LIMITED. No real OpenCode 9B, Ollama 30B or gaming/VR with this exact candidate in native VM, nor live user-host doctor/write/delegation, real VR-game preemption, Ollama unload, installed migration/rollback or full Master QA. All still require evidence.
- **MASTER_QA=BLOCKED; RELEASE_APPROVED=false; GITHUB_FIRST=PASS_LIMITED.**
