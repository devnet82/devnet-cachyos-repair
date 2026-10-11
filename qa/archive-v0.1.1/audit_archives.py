#!/usr/bin/env python3
"""Devnet v0.1.1: read-only exact-archive safety/syntax audit.

Never extracts packages, runs installers, invokes hardware or writes outside
the requested JSON report. No libraries except Python stdlib.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import tarfile
import zipfile
from xml.etree import ElementTree as ET

MAX_MEMBERS = 100000
MAX_TOTAL_UNPACKED = 8 * 1024**3
MAX_PARSE_SIZE = 2 * 1024**2
KNOWN = (".py", ".sh", ".json", ".xml", ".svg")

def sha256_file(file):
    h = hashlib.sha256()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def is_bad_path(name):
    if not name or chr(0) in name or name.startswith(("/", "\\")) or "\\" in name:
        return True
    p = PurePosixPath(name)
    return ".." in p.parts or (bool(p.parts) and ":" in p.parts[0])

def iter_archive(path):
    """Yield (name, size, type, readable stream) for archive entries."""
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                perms = info.external_attr >> 16
                if stat.S_ISLNK(perms):
                    yield info.filename, info.file_size, "link", None
                elif info.is_dir():
                    yield info.filename, 0, "dir", None
                else:
                    with z.open(info) as f:
                        yield info.filename, info.file_size, "file", f
        return
    if not path.name.endswith((".tar.gz", ".tgz")):
        raise ValueError("Unsupported archive (expected ZIP, tar.gz or tgz)")
    with tarfile.open(path, "r:gz") as t:
        for info in t:
            if info.issym() or info.islnk():
                yield info.name, info.size, "link", None
            elif info.isdir():
                yield info.name, 0, "dir", None
            elif info.isfile():
                stream = t.extractfile(info)
                if stream is None:
                    raise ValueError("Missing archive member stream")
                with stream:
                    yield info.name, info.size, "file", stream
            else:
                yield info.name, info.size, "special", None

def parse_file(name, data, errors, counts):
    lower = name.lower()
    first = data.split(b"\n", 1)[0]
    python_file = lower.endswith(".py") or first.startswith(b"#!/usr/bin/env python")
    shell_file = lower.endswith(".sh") or first.startswith((b"#!/bin/bash", b"#!/usr/bin/env bash"))
    if python_file:
        counts["python"] += 1
        try:
            ast.parse(data, filename=name)
        except (SyntaxError, ValueError, UnicodeDecodeError) as exc:
            errors.append("Python syntax: " + name + ": " + str(exc)[:140])
    if shell_file:
        counts["shell"] += 1
        if shutil.which("bash"):
            rc = subprocess.run(["bash", "-n"], input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=15, check=False)
            if rc.returncode:
                errors.append("Bash syntax: " + name + ": " +
                              rc.stderr.decode("utf-8", "replace")[:140])
        else:
            counts["shell_not_tested"] += 1
    if lower.endswith(".json"):
        counts["json"] += 1
        try:
            json.loads(data)
        except (ValueError, UnicodeDecodeError) as exc:
            errors.append("JSON: " + name + ": " + str(exc)[:140])
    if lower.endswith((".xml", ".svg")):
        counts["xml"] += 1
        try:
            ET.fromstring(data)
        except ET.ParseError as exc:
            errors.append("XML: " + name + ": " + str(exc)[:140])

def audit(path, expected=None):
    report = {"package": path.name, "sha256": None, "bytes": None,
              "checks": {}, "syntax_counts": {}, "member_count": 0,
              "version_files": [], "possible_test_files": [],
              "hardware": "NOT_TESTED", "install_upgrade_rollback": "NOT_TESTED",
              "gui_runtime": "NOT_TESTED", "master_qa": "BLOCKED"}
    checks = report["checks"]
    def record(label, status, detail):
        checks[label] = {"status": status, "detail": detail}
    if not path.is_file():
        record("archive_exists", "FAIL", "Exact archive does not exist")
        report["overall"] = "FAIL"
        return report
    report["bytes"] = path.stat().st_size
    report["sha256"] = sha256_file(path)
    record("archive_exists", "PASS", "Input file exists, SHA-256 calculated")
    if expected:
        ok = report["sha256"].lower() == expected.lower()
        record("expected_sha256", "PASS" if ok else "FAIL",
               "Exact package digest matches" if ok else "Mismatch against expected digest")
    else:
        record("expected_sha256", "NOT_TESTED", "No externally pinned digest supplied")
    seen = set()
    errors = []
    counts = {"python": 0, "shell": 0, "shell_not_tested": 0,
              "json": 0, "xml": 0, "skipped_large": 0}
    members, total, links = 0, 0, 0
    try:
        for name, size, kind, stream in iter_archive(path):
            members += 1
            total += size
            if members > MAX_MEMBERS or total > MAX_TOTAL_UNPACKED:
                raise ValueError("Archive exceeds bounded member-count/unpacked-size limit")
            if is_bad_path(name) or name in seen:
                errors.append("Unsafe/duplicate entry: " + repr(name[:150]))
            seen.add(name)
            if kind in ("link", "special"):
                links += 1
                errors.append("Link or special file: " + repr(name[:150]))
            if kind != "file":
                continue
            base = PurePosixPath(name).name
            if base in ("VERSION", "version.txt", "QA_MANIFEST.json") and len(report["version_files"]) < 15:
                report["version_files"].append(name)
            if ("test" in base.lower() or name.endswith("/qa.sh")) and len(report["possible_test_files"]) < 25:
                report["possible_test_files"].append(name)
            if size > MAX_PARSE_SIZE:
                counts["skipped_large"] += 1
                # Always read complete member to enforce ZIP CRC/decompression and stream validity.
                for _ in iter(lambda: stream.read(1024 * 1024), b""):
                    pass
            else:
                data = stream.read()
                if len(data) != size:
                    errors.append("Member length mismatch: " + name[:150])
                parse_file(name, data, errors, counts)
        report["member_count"] = members
        report["syntax_counts"] = counts
        report["total_unpacked_bytes"] = total
        record("archive_integrity", "FAIL" if errors else "PASS",
               f"Read {members} members / {total} unpacked bytes; {'; '.join(errors[:8]) if errors else 'no CRC/read errors'}")
        record("unsafe_members", "FAIL" if links or any("Unsafe/duplicate" in x for x in errors) else "PASS",
               f"{links} links/special files; safe-path and duplicate checks complete")
        syntax_bad = any(e.startswith(("Python syntax", "Bash syntax", "JSON:", "XML:")) for e in errors)
        parsed = sum(counts[k] for k in ("python", "shell", "json", "xml"))
        record("static_syntax", "FAIL" if syntax_bad else
               ("NOT_TESTED" if not parsed or counts["shell_not_tested"] else "PASS"),
               f"{counts}; syntax problems: {len([x for x in errors if x.startswith(('Python syntax', 'Bash syntax', 'JSON:', 'XML:'))])}")
        if not members:
            record("nonempty_package", "FAIL", "Archive is empty")
        else:
            record("nonempty_package", "PASS", f"{members} entries found")
    except (OSError, ValueError, EOFError, zipfile.BadZipFile,
            tarfile.TarError, RuntimeError) as exc:
        record("archive_integrity", "FAIL", type(exc).__name__ + ": " + str(exc)[:250])
        record("unsafe_members", "NOT_TESTED", "Cannot complete archive read")
        record("static_syntax", "NOT_TESTED", "Cannot complete archive read")
    bad = any(x["status"] == "FAIL" for x in checks.values())
    report["overall"] = "FAIL" if bad else "PARTIAL"  # never 100% from archive inspection
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("packages", nargs="+", type=Path)
    p.add_argument("--report-dir", type=Path, default=Path("qa-reports"))
    p.add_argument("--expected-sha256", default=None,
                   help="Pinned SHA256 for one archive")
    a = p.parse_args()
    if a.expected_sha256 and len(a.packages) != 1:
        p.error("--expected-sha256 requires exactly one archive")
    a.report_dir.mkdir(parents=True, exist_ok=True)
    failed = False
    for src in a.packages:
        d = audit(src, a.expected_sha256)
        out = a.report_dir / (src.name + ".qa.json")
        out.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n")
        print(d["package"], d["overall"], d["sha256"], "=>", out.name)
        for key, c in d["checks"].items():
            print(" ", key, c["status"], c["detail"][:110])
        failed |= d["overall"] == "FAIL"
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
