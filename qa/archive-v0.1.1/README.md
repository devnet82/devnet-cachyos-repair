# Devnet exact-build package audit v0.1.1

Run this **read-only** verifier against the original files, not the older GitHub repository releases.

This is a partial archive/syntax audit, NOT a Master QA approval. It will not run install.sh, change services, access hardware or reboot. Archive members are streamed and examined; no package is extracted.

Supported formats: .zip, .tar.gz and .tgz. The original Proton RTSP tar.gz may be large, so allow a few minutes. Python 3 and bash are required. The script uses only the Python standard library.

On CachyOS / fish, save the auditor locally (download the raw GitHub source, not a shell command from an unknown site), then use:

    python3 audit_archives.py \
      ~/Downloads/devnet-sonicpad-auto-printer-v0.1.29.zip \
      ~/Downloads/devnet-wayvr-watch-manager-v0.1.33.zip \
      ~/Downloads/devnet-rgb-control-v8.9\(1\).zip \
      ~/Downloads/vr-stack-control-v0.6.131.zip \
      ~/Downloads/devnet-proton-rtsp-v1.74-fresh-capture.tar\(1\).gz \
      --report-dir ~/Downloads/devnet-master-qa-reports

Adjust only the filenames to match the local files. Each archive receives a JSON report with SHA-256, checksum/integrity results, safe archive path/link checks, Python/Bash/JSON/XML syntax check counts, available tests listing and explicit NOT_TESTED for installation/hardware/GUI.

For full QA, run isolated install/upgrade/rollback/Doctor/reconnect/KDE/WayVR/Sonic Pad tests separately. Do not run a package installer as root just to exercise QA.

The GitHub workflow tests the auditor against synthetic ZIP/tar files. It **does not test the user's actual uploaded ZIPs**, as the GitHub runner cannot access those chat-uploaded bytes. No claim of success on those five packages until their exact bytes are accessible to an actual testing runtime.

Existing cross-app GitHub QA work remains on branch qa/devnet-portfolio-master-v0.1.0.
