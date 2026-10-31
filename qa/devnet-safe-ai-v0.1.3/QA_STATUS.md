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

## Updated verified status — 31 October 2026 (post earlier summary)

- **Real Qwen 9B with genuine OpenCode 2.1.4, running directly (outside Bubblewrap): PASS_LIMITED**. GitHub [run 41223936617](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41223936617) completed actual Ollama model download/inference and created `REAL_LIVE_QA.txt` through OpenCode's real Write tool; independent 9B-scope evidence gate PASS. This proves the underlying 9B model and file-writing tool work; it does **not** prove the current v0.1.3 sandboxed launcher creates files.
- **Genuine unprivileged Bubblewrap in an actual GitHub-hosted CachyOS QEMU guest: PASS_LIMITED**. GitHub [run 41224010435](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41224010435) passed fresh 35/35 exact-archive tests, workspace-write and secret/filesystem/network isolation probes, and independent evidence gate. No live OpenCode/Ollama inside that exact sandbox was exercised.
- **Exact v0.1.3 launcher with real OpenCode + Ollama on Ubuntu GitHub runner: BLOCKED**. GitHub [run 41223441027](https://github.com/devnet82/devnet-cachyos-repair/actions/runs/41223441027) installed real OpenCode and Ollama but `doctor` failed immediately at `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, before any live file write. Treat as GitHub-runner namespace restriction or candidate compatibility issue until tested on real CachyOS; no security bypass is acceptable.
- Other scheduled native CachyOS jobs at 17:30 UTC are duplicate/reverification jobs, not new scope; assess results independently before citing.
- **Next minimum acceptance test**: run *uninstalled* pinned candidate v0.1.3 `doctor` on the user's CachyOS computer with verified hash; do not alter currently installed v0.1.2 launcher. Only if successful, test genuine 9B file writing *inside this launcher*, 30B specialist delegation/model unloading, pause on gaming, strict workspace denies, rollback and all mandatory host Master QA checks.
- **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**; current installed safe AI remains unchanged.

## User-reported live CachyOS host acceptance — 31 October 2026
- User downloaded candidate `~/Downloads/devnet-safe-ai-v0.1.3-QA-BLOCKED.zip`; user-provided `sha256sum` is `8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b` (exact archived candidate), and unzip listing contains all five expected items.
- Exact candidate, extracted and **not installed**, `python3 devnet-safe-ai-v0.1.3.py doctor`: `PASS: OpenCode sandbox, offline network, private workspace, models and subagent config`; `DOCTOR EXIT: 0`.
- User then invoked **actual candidate `run`** with prompt to create `DEVNET_V013_LIVE_QA.txt`. Console displayed `> build · qwen3.5:9b`, `← Write DEVNET_V013_LIVE_QA.txt`, `Created file successfully`, `AI EXIT: 0`; independent filesystem read in same user's shell returned `DEVNET_V013_SANDBOX_WRITE_PASS` from `/mnt/devnet-ai/projects/devnet-ai-safe-workspace/DEVNET_V013_LIVE_QA.txt`.
- **Scope:** real host launcher doctor and a genuine 9B sandboxed Write tool acceptance, user-provided terminal output; not independently captured host recording/attestation. Host configuration was not installed/replaced. No 30B delegation, unload, active-game guard, rollback, complete security test or complete Master QA.
- **NEXT:** verify real 9B→30B subagent handoff, unload/pause policy, then remaining mandatory host QA. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.

## Live host 30B delegation acceptance: FAILED — 31 October 2026

- Uninstalled exact-hash v0.1.3 candidate was invoked by user via `python3 devnet-safe-ai-v0.1.3.py run` with a non-writing concurrency review delegated to `devnet-heavy`, requesting an actual subagent tool call without model override.
- The real 9B coordinator printed `✓ Review concurrency design and fix race condition Devnet-Heavy Agent`, but subsequently said child completed without returning analysis. It then attempted `Skill "devnet-heavy"`, which **failed** (`Unable to load skill devnet-heavy`), scanned the workspace, and printed a pseudo-XML `write` markup that did not constitute a real Write tool call.
- Response falsely asserted specialist analysis occurred and included factual/code defects (lost-update example incorrectly said expected final 5 for two increments; code without global variable handling). It reported `AI EXIT: 0` despite the failed specialist result and unverified generated report.
- Immediate `ollama ps` reported `qwen3.5:9b` loaded, and did **not** show `qwen3-coder:30b`. This observation **does not prove** 30B was never loaded because it may have unloaded before polling.
- **Acceptance FAIL**: no verifiable child model request, no returned specialist content, unsafe fabricated fallback, no proof of 30B→9B handoff/unload. Current candidate is unchanged and uninstalled.
- Similar upstream OpenCode issues: [#18423](https://github.com/anomalyco/opencode/issues/18423) (empty subagent text with Ollama) and [#24447](https://github.com/anomalyco/opencode/issues/24447) (missing result diagnostics), but root cause not established for this run. Avoid blaming Ollama or tweaking models until reading private-state session metadata or capture trusted gateway model-request evidence.
- **Next narrow read-only host diagnostic:** inspect counts of `qwen3-coder:30b` and `devnet-heavy` inside the Safe AI private OpenCode SQLite session database, without printing prompts/credentials. Then reproduce with proper model-usage evidence on GitHub first, fix fail-closed false-success behaviour, run every applicable QA check afresh.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false.**

## Host OpenCode private SQLite metadata diagnostic — 31 October 2026

User ran read-only aggregate diagnostics on `~/.local/share/devnet-safe-ai/opencode-home/.local/share/opencode/opencode.db`:
- `session_message` recent records: 72.
- 21 records identify nested model `{'id':'qwen3-coder:30b','providerID':'ollama','variant':'default'}`; 22 identify `qwen3.5:9b` and 29 have no model.
- Agent counts are 21 `devnet-heavy`, 29 `build`, 22 no agent.
- Flat top-level role query returned 0 because JSON record shapes differ; **not** evidence of zero assistant activity.
- This is genuine OpenCode session metadata strongly suggesting a 30B subagent session was started; **still not proof of generated tokens/completed inference**. Next diagnostic aggregates completion reasons, error counts and token metadata for `devnet-heavy` records without reading prompts/text.
- **30B result delivery FAIL, MASTER_QA BLOCKED, RELEASE_APPROVED false**; no installed launcher changes.

## Host private OpenCode token diagnostic — 31 October 2026

User's read-only local SQLite `session_message` aggregate, `devnet-heavy` scoped, reports **21 30B-associated messages**, `tokens` metadata in 20, **13,682 reported output tokens**, `finish=stop` 3, `finish=tool-calls` 17, `finish` missing 1, and **no `error` object** in these 21 records. Thus there is strong native runtime evidence of actual 30B token generation and agent tool usage, beyond just model configuration. Data covers recent 200 records (not proven confined to one run), so do **not** claim every token belongs to most recent attempt or that delegation was successful.
The caller still reported **no usable returned specialist analysis**, tried an invalid Skill fallback, then presented invented or unverified analysis with exit 0. **TASK RESULT DELIVERY remains FAIL**, need read-only analysis of `session_part` task tool statuses/lengths without printing private prompts or content. Do not install or approve v0.1.3. **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.

## Host subagent return-state diagnostic — 31 October 2026

User's read-only OpenCode 2.1.4 SQLite JSON `session_message.data.content` aggregate over latest 200 messages found **5 real coordinator `subagent` calls**: newest-to-oldest `completed` output length **159**, `completed` length **2072**, `error` length **0**, `error` length **0**, `completed` length **1524**. Coordinator tool mix: read 2, glob 1, skill 1, subagent 5, write 6; heavy model has 20 text blocks. Therefore **some subagent return payloads are nonempty**, disproving a blanket no-output claim, but the two errors and failed latest user-visible result remain. Need distinguish latest completed short result from actual specialist findings, and inspect error metadata only. This is aggregate across recent records, not automatically all from same single run. The current v0.1.3 exact archive is unchanged; **MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.
