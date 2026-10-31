# Devnet Safe AI v0.1.3 — QA BLOCKED

Original exact v0.1.2 SHA256: `fd227dfc54e26e10198ebc0623088aea7884fa62840b7999b32d8a2d0618a8ae`

Candidate exact v0.1.3 ZIP SHA256: `8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b`

Changes staged outside this repository, without installation:

- For 9B Ollama `/v1/chat/completions`, normalize trusted HTTP request to top-level `reasoning_effort: none`, preserving tools/messages/stream.
- Make OpenCode V2 edit permissions compatible with location-relative paths; retain external-directory denial, Bubblewrap workspace mount, state/system/secret denials.
- Keep 30B model and native Ollama inference payloads unchanged.

Local/offline extracted-archive unit regressions: **35/35 PASS**. Real OpenCode and Ollama runtime **NOT TESTED**. GitHub-hosted Ubuntu exact-archive 35-test run **PASS_LIMITED** (run 41211385269, uploaded SHA256 candidate confirmed), including deterministic independent scope gate. GitHub-hosted native CachyOS VM exact-archive 35/35 unit scope **PASS_LIMITED** (run 41211497089), with checksum preflight, real guest execution, evidence artifact and deterministic independent gate all successful. This is not live OpenCode/Ollama testing. Native CachyOS VM, host installation, model handoff, file creation, sandbox escape, gaming pause, rollback, independent Master QA gate **NOT TESTED**. Prior observed file-write acceptance: **FAIL**.

**RELEASE_APPROVED=false; MASTER_QA=BLOCKED.** No current launcher, OpenCode config, or Ollama config was modified. Do not promote/merge until genuine GitHub-first and host QA tests are executed on the exact candidate with independent evidence.

## 2026-10-31 — Genuine GitHub live-scope tests (newer than initial status above)

**Candidate ZIP unchanged:** SHA256 `8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b`. Existing CachyOS host launcher and configurations untouched.

- [Native CachyOS QEMU/KVM guest run 41224010435](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41224010435): **PASS, limited scope, independently attested**. Exact ZIP, all 35 unit tests freshly rerun, actual unprivileged Bubblewrap filesystem and offline-network boundary checks, negative symlink escape check, genuine guest evidence and independent signed scope gate.
- [Real OpenCode 2.1.4 + real Ollama Qwen3.5 9B run 41223936617](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41223936617): **PASS, limited scope, independent evidence gate**. Downloaded real model; OpenCode executed candidate-derived configuration without Bubblewrap; requested an exact file through the tool and checked that the physical output file existed with exact expected line. **This job intentionally does not claim sandbox isolation.**
- [Original combined Ubuntu live-sandbox run 41223441027](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41223441027): **FAILED (GitHub Ubuntu runner's unprivileged Bubblewrap loopback RTM_NEWADDR = Operation not permitted)**; prior [run 41223374963](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41223374963) failed harness version grep. The combined workflow has been **archived, removed from active Actions** and replaced with the two separately passing scope workflows above. Historical failed runs retained unaltered as QA evidence.
- Earlier test-harness-only failures of the split workflows: native guest result omitted `native_bwrap_isolation` receipt, and direct runner initially omitted workspace creation. Both harness defects corrected without modifying candidate ZIP. Final green runs and independent gates confirm corrected scopes.

**Not yet verified for this v0.1.3 candidate:** real OpenCode + Ollama executing together *inside* the native CachyOS Bubblewrap sandbox; 30B delegation and unload/model switching; complete native host upgrade/rollback; live host gaming pause; security attacks on real OpenCode including traversal and secret-file symlinks; autonomous Master QA and user acceptance.

**MASTER_QA=BLOCKED; RELEASE_APPROVED=false. Do not install over existing setup.**
