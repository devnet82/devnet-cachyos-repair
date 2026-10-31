# Devnet Wine Idle Cleaner v0.1.0 — QA BLOCKED
**Release approval: false.** Do not install or enable the timer on the host.
Original SHA256 of exact candidate ZIP:
`0a0ee582186a18ffa3ee374f2e8565d3430cf268f2b0e3b52ae411c715494b47`

Purpose: automatically stop **only the Autodesk Fusion Wine prefix**, after non-core Wine clients disappear, six allowlisted Wine services remain stable, and at least 180 seconds elapse. Preserve the existing Devnet Safe AI gaming detector. Never use global pkill/killall or stop another prefix.

Candidate has 16/16 offline behaviour tests and 4/4 simulated non-root installer/uninstaller tests PASS, plus exact extracted ZIP re-run PASS. These results are **not** host or GitHub test evidence.

GitHub-first workflows staged:
- devnet-wine-idle-v010-exact.yml — exact archive Ubuntu unit + independent limited-scope evidence
- devnet-wine-idle-v010-native-cachyos.yml — exact archive genuine QEMU/KVM CachyOS guest tests and independently verified limited scope

Both require upload of candidate.zip to `qa/devnet-wine-idle-cleaner-v0.1.0/` in this branch before they can pass. Real Fusion active/closed lifecycles, Wine shutdown, Prefix isolation against live processes, user-level systemd timer and rollback, gaming detector interaction **NOT TESTED**.
**MASTER_QA=BLOCKED; RELEASE_APPROVED=false**.
