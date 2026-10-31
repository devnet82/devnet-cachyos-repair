# Devnet Safe AI v0.1.3 — QA BLOCKED

Original exact v0.1.2 SHA256: `fd227dfc54e26e10198ebc0623088aea7884fa62840b7999b32d8a2d0618a8ae`

Candidate exact v0.1.3 ZIP SHA256: `8a55f4dbc9e939b04b798b7176ed8ab10b0439a88fc7609f134b528d1d3daf7b`

Changes staged outside this repository, without installation:

- For 9B Ollama `/v1/chat/completions`, normalize trusted HTTP request to top-level `reasoning_effort: none`, preserving tools/messages/stream.
- Make OpenCode V2 edit permissions compatible with location-relative paths; retain external-directory denial, Bubblewrap workspace mount, state/system/secret denials.
- Keep 30B model and native Ollama inference payloads unchanged.

Local/offline extracted-archive unit regressions: **35/35 PASS**. Real OpenCode and Ollama runtime **NOT TESTED**. GitHub-hosted Ubuntu exact-archive 35-test run **PASS_LIMITED** (run 41211385269, uploaded SHA256 candidate confirmed), including deterministic independent scope gate. GitHub-hosted native CachyOS VM unit scope is **IN_PROGRESS** (run 41211497089), not yet a PASS. Native CachyOS VM, host installation, model handoff, file creation, sandbox escape, gaming pause, rollback, independent Master QA gate **NOT TESTED**. Prior observed file-write acceptance: **FAIL**.

**RELEASE_APPROVED=false; MASTER_QA=BLOCKED.** No current launcher, OpenCode config, or Ollama config was modified. Do not promote/merge until genuine GitHub-first and host QA tests are executed on the exact candidate with independent evidence.
