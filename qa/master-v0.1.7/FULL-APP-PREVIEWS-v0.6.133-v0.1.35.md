# Devnet full-application rebuild previews — 11 October 2026

**STATUS: QA PREVIEW ONLY; NOT RELEASE APPROVED.**

User asked to replace incremental hotfix-only deliveries with complete installable application bundles.

## Built preview artifacts

| Application | Version | Original full baseline | Known improvements integrated | QA ZIP SHA-256 |
| --- | --- | --- | --- | --- |
| VR Stack Control | v0.6.133 | Exact original v0.6.126 archive | Original v0.6.130 libmonado/Doctor helper; v0.6.132 version sync incorporated | `c7308d0826705454b522ee9a13d648955c1dafbb8d445abf6475ec4b39ee2ddc` |
| WayVR Watch Manager | v0.1.35 | Exact original v0.1.27 archive | v0.1.31 headset-write suppression behaviour; original v0.1.34 Doctor Check constructor patch | `9b9e0d7b2ae20eab78cc45b28d2d9c905ba5d546c37bfe86ad1aa252bc31894b` |

Both have complete bin/app payloads and new cautious user-only install/rollback scripts. The new installer retains existing supported-version runtime components and configuration during an in-place upgrade rather than overwriting them with the historical full base. Full clean installation uses the older complete baseline with the known patches added. It requires explicit `--yes` after `--dry-run`, takes a rollback snapshot, refuses symlinked targets and unsupported existing versions, and does not auto-start system services.

### Local QA performed

- Candidate archive CRC/path safety PASS; shell Bash syntax and Python AST syntax PASS.
- Explicit isolated unprivileged regression suite: **7/7 PASS** covering fresh install, supported baseline upgrade, idempotency, backup rollback, configuration and runtime preservation, unsafe/mismatched version rejection, and WayVR protected watch/metrics behaviour.
- WayVR archived full-baseline regression suite: **59 PASS / 2 FAIL**. Legacy cases still expect the old pre-v0.1.31 HMD fallback writes and automatic metrics service restarting, unlike the documented new no-custom-HMD-write and no-auto-restart preview behaviour. These are recorded failures/requirements to reconcile rather than silently skipped tests.
- WayVR original full-baseline watch.xml and SVG asset bytes were preserved unchanged; parity against the user's latest locked watch image is NOT VERIFIED.
- Native installed CachyOS VM tests for the **new** preview ZIPs, real full previous-app upgrade, GTK GUI/tray, Quest hardware and multi-hardware tests all remain NOT_TESTED.

### Source gaps — MUST BE FIXED before approval

The recovered complete VR Stack code baseline is v0.6.126; complete intermediate sources v0.6.127–v0.6.129 were not accessible. The recovered complete WayVR baseline is v0.1.27; complete intermediate code v0.1.28–v0.1.33 was not accessible. **Therefore a fresh install of these QA previews cannot yet be certified equivalent to the newer working apps.**

Do not delete or overwrite a known-good installation; do not publish original draft assets, do not present either QA preview as a final safe upgrade. Existing app branches/status:
- https://github.com/devnet82/vr-stack-control/tree/qa/full-app-candidate-v0.6.133
- https://github.com/devnet82/devnet-wayvr-watch-manager/tree/qa/full-installer-preview-v0.1.35

Preview ZIPs were created as local conversation artifacts and were not uploaded as GitHub releases. Original working releases and prior draft ZIPs remain preserved. Master QA approval remains BLOCKED.
