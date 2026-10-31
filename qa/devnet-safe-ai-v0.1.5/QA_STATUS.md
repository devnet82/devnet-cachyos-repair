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
