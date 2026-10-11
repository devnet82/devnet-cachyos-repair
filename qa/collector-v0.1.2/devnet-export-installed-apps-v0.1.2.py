#!/usr/bin/env python3
# DEVNET_COLLECTOR_MANAGED v0.1.2
"""Privacy-conscious, read-only installed Devnet application source collector.

This exports user-installed program files, not personal app config, Steam data,
Quest data, system services or live processes. The exported data may still contain
secrets manually embedded in source: review and explicitly permit flagged files.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import uuid
import zipfile

VERSION = "0.1.2"
VR_BIN = (
    "vr-control", "vr-control-gui", "vr-doctor", "vr-stackd", "vr-stack-tray",
    "vr-stack-run.sh", "vr-stack-steam-autofind", "vr-stack-steam-repair",
    "vr-stack-libmonado-fix", "vr-stack-libmonado-fix.sh", "vr-stack-control",
    "vr-stack-tray-gui", "vr-control-doctor", "vr-control-tray",
)
WAYVR_BIN = (
    "devnet-wayvr-watch-manager", "devnet-wayvr-watch-metrics",
    "devnet-wayvr-watch-toggle", "devnet-wayvr-watch-doctor",
    "devnet-wayvr-watch-adb-setup", "devnet-wayvr-watch-setup",
)
DESKTOP_FILES = (
    "vr-control-panel.desktop", "vr-stack-tray.desktop",
    "vr-stack-control.desktop", "devnet-wayvr-watch-manager.desktop",
)
SERVICE_FILES = (
    "vr-stack-control.service", "vr-stack-tray.service",
    "vr-stack-libmonado-fix.path", "vr-stack-libmonado-fix.service",
    "devnet-wayvr-watch-metrics.service",
)
REQUIRED = {
    "vr_stack": (
        ".local/bin/vr-control", ".local/bin/vr-control-gui",
        ".local/bin/vr-doctor", ".local/bin/vr-stackd",
    ),
    "wayvr": (
        ".local/share/devnet-wayvr-watch-manager/doctor.py",
        ".local/share/devnet-wayvr-watch-manager/manager.py",
        ".local/share/devnet-wayvr-watch-manager/metrics.py",
        ".local/share/devnet-wayvr-watch-manager/watchlib.py",
        ".local/share/devnet-wayvr-watch-manager/watch.xml",
    ),
}
APP_ASSET_SUFFIXES = {
    ".py", ".svg", ".xml", ".png", ".jpg", ".jpeg",
    ".webp", ".css", ".ui", ".qml", ".js", ".desktop", ".sh", ".txt",
}
APP_ASSET_NAMES = {"VERSION", "LICENSE", "README.md", "default-config.json"}
FORBIDDEN_PARTS = {
    "__pycache__", ".git", ".cache", "backups", "backup", "snapshots",
    "logs", "log", "session", "sessions", "state", "secrets", "keys",
    "credentials", "tokens", "profiles", "downloads", "runtime", ".ssh",
    ".gnupg", "config", "cache", ".local/state",
}
SAFE_NAME = re.compile(r"^[A-Za-z0-9_. -]{1,180}$")
# No values from matching lines are ever printed. Privacy warnings are fail-closed.
PRIVACY_FLAGS = re.compile(
    rb"(?i)(password\s*[:=]|api[_-]?key\s*[:=]|secret\s*[:=]|"
    rb"access[_-]?token\s*[:=]|private\s+key|BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|"
    rb"/home/[a-z_][a-z0-9_-]*/|/run/media/[a-z_][a-z0-9_-]*/|"
    rb"(?<![a-z0-9])(?:gh[pousr]_[A-Za-z0-9]{18,}|github_pat_[A-Za-z0-9_]{20,}))"
)
MAX_FILE = 8 * 1024 * 1024
MAX_TOTAL = 60 * 1024 * 1024
MAX_FILES = 400
MAX_DIRS = 400

class ExportBlocked(ValueError):
    """Expected fail-closed export refusal (never reveal private file values)."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _components_are_safe(base: Path, rel: Path, *, directory: bool = False) -> bool:
    if rel.is_absolute() or not rel.parts or ".." in rel.parts:
        return False
    cursor = base
    try:
        for segment in rel.parts:
            if segment in ("", ".", ".."):
                return False
            cursor = cursor / segment
            mode = cursor.lstat().st_mode
            if stat.S_ISLNK(mode):
                return False
        return stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)
    except (FileNotFoundError, OSError):
        return False


def _safe_directory(base: Path, rel: Path) -> bool:
    return _components_are_safe(base, rel, directory=True)


def _safe_read(home: Path, relative: Path) -> tuple[bytes, os.stat_result]:
    """Open every path segment without following symlinks; check concurrent writes."""
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ExportBlocked("Unsafe source path")
    parent_fd = os.open(home, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in relative.parts[:-1]:
            new_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = new_fd
        fd = os.open(relative.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent_fd)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_FILE or before.st_nlink != 1:
                raise ExportBlocked("Unsafe or oversized source file")
            chunks = []
            count = 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, MAX_FILE + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                if count > MAX_FILE:
                    raise ExportBlocked("Source grew beyond size limit")
                chunks.append(chunk)
            after = os.fstat(fd)
            if (before.st_ino, before.st_dev, before.st_size, before.st_mtime_ns) != (
                after.st_ino, after.st_dev, after.st_size, after.st_mtime_ns
            ) or count != before.st_size:
                raise ExportBlocked("Source changed during collection")
            return b"".join(chunks), after
        finally:
            os.close(fd)
    finally:
        os.close(parent_fd)


def _safe_name(name: str) -> bool:
    return name not in (".", "..") and bool(SAFE_NAME.fullmatch(name))


def gather(home: Path, apps: tuple[str, ...]) -> tuple[list[Path], list[str]]:
    selected: set[Path] = set()
    warnings: list[str] = []
    if "vr_stack" in apps:
        for name in VR_BIN:
            selected.add(Path(".local/bin") / name)
        for name in DESKTOP_FILES[:3]:
            selected.add(Path(".local/share/applications") / name)
        for name in SERVICE_FILES[:-1]:
            selected.add(Path(".config/systemd/user") / name)
    if "wayvr" in apps:
        for name in WAYVR_BIN:
            selected.add(Path(".local/bin") / name)
        selected.add(Path(".local/share/applications") / DESKTOP_FILES[-1])
        selected.add(Path(".config/systemd/user") / SERVICE_FILES[-1])
        root_rel = Path(".local/share/devnet-wayvr-watch-manager")
        if _safe_directory(home, root_rel):
            entries_seen = dirs_seen = 0
            for current, dirs, files in os.walk(home / root_rel, topdown=True, followlinks=False):
                here = Path(current)
                # Do not traverse private, symlinked, or unsupported paths.
                dirs[:] = sorted(d for d in dirs if
                    d.lower() not in FORBIDDEN_PARTS and _safe_name(d) and
                    _safe_directory(home, (here / d).relative_to(home)))
                dirs_seen += len(dirs)
                if dirs_seen > MAX_DIRS:
                    raise ExportBlocked("WayVR directory scan limit reached; export not complete")
                for name in sorted(files):
                    entries_seen += 1
                    if entries_seen > MAX_FILES:
                        raise ExportBlocked("WayVR asset scan limit reached; export not complete")
                    if not _safe_name(name):
                        warnings.append("Ignored nonstandard asset name")
                        continue
                    full = here / name
                    relative = full.relative_to(home)
                    if any(part.lower() in FORBIDDEN_PARTS for part in relative.parts):
                        continue
                    if full.suffix.lower() in APP_ASSET_SUFFIXES or name in APP_ASSET_NAMES:
                        selected.add(relative)
        elif (home / root_rel).exists() or (home / root_rel).is_symlink():
            raise ExportBlocked("WayVR source directory has unsafe or symlinked path components")
    # Discover other known app executable prefix variants, but not arbitrary hidden files.
    if _safe_directory(home, Path(".local/bin")):
        for full in (home / ".local/bin").iterdir():
            name = full.name
            prefix = ("vr-stack-", "vr-control-") if apps == ("vr_stack",) else (
                "devnet-wayvr-watch-",) if apps == ("wayvr",) else (
                "vr-stack-", "vr-control-", "devnet-wayvr-watch-",)
            if _safe_name(name) and name.startswith(prefix):
                selected.add(full.relative_to(home))
    return sorted(selected, key=lambda p: p.as_posix()), warnings


def _check_output_dir(outdir: Path) -> Path:
    """Never traverse a symlinked output path or create a public ZIP."""
    outdir = outdir.absolute()
    current = Path(outdir.anchor)
    for part in outdir.parts[1:]:
        current = current / part
        if current.exists() or current.is_symlink():
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                raise ExportBlocked("Output path must not contain symlinks or non-directories")
        elif current == outdir:
            current.mkdir(mode=0o700)
        else:
            raise ExportBlocked("Output parent directory missing; create it manually")
    if not os.access(outdir, os.W_OK | os.X_OK):
        raise ExportBlocked("Output directory not writable")
    return outdir


def collect(home: Path, apps: tuple[str, ...]) -> tuple[list[tuple[dict, bytes]], dict]:
    if home.is_symlink() or not home.is_dir():
        raise ExportBlocked("Home directory absent or symlinked")
    home = home.resolve(strict=True)
    paths, warnings = gather(home, apps)
    records: list[tuple[dict, bytes]] = []
    total = 0
    privacy_names: list[str] = []
    for rel in paths:
        if not _components_are_safe(home, rel):
            continue
        try:
            data, st = _safe_read(home, rel)
        except (OSError, ValueError):
            warnings.append("An unreadable, changed, or unsafe source file was excluded")
            continue
        if len(records) >= MAX_FILES or total + len(data) > MAX_TOTAL:
            raise ExportBlocked("Application export size/count limit exceeded; export incomplete")
        flagged = bool(PRIVACY_FLAGS.search(data))
        if flagged:
            privacy_names.append(rel.as_posix())
        entry = {"path": rel.as_posix(), "size": len(data), "sha256": digest(data),
                 "executable": bool(st.st_mode & 0o111), "privacy_review_required": flagged}
        records.append((entry, data))
        total += len(data)
    got = {rec["path"] for rec, _ in records}
    per_app = {app: {
        "required_count": len(REQUIRED[app]),
        "required_found": sum(path in got for path in REQUIRED[app]),
        "missing_required": [path for path in REQUIRED[app] if path not in got],
    } for app in apps}
    if not records or any(info["missing_required"] for info in per_app.values()):
        counts = ", ".join(f"{app} {info['required_found']}/{info['required_count']}" for app, info in per_app.items())
        raise ExportBlocked(f"Incomplete installed application sources ({counts}); no ZIP created. Use --doctor to inspect missing paths.")
    manifest = {
        "schema": "devnet-installed-app-source-export-v2", "tool_version": VERSION,
        "mode": "read-only collection of user application program sources",
        "selected_apps": list(apps), "not_an_installable_package": True,
        "configuration_directories_excluded": True,
        "privacy_review_before_sharing": True,
        "files_collected": len(records), "bytes_collected": total,
        "privacy_indicator_file_count": len(privacy_names),
        "privacy_flagged_paths": privacy_names,
        "applications": per_app, "warnings": warnings,
        "files": [rec for rec, _ in records],
        "excluded": ["XDG configuration", "Steam and VRChat user data", "Quest/ADB",
                     "SSH and passwords", "live process state", "backups and logs"],
    }
    return records, manifest


def _write_atomic(outdir: Path, records: list[tuple[dict, bytes]], report: dict) -> Path:
    date = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    body = ("DEVNET INSTALLED APPLICATION SOURCE EXPORT — PRIVATE\n"
            "This is not an installer. Review the files and source before sharing.\n"
            "No running apps, settings or services were modified.\n")
    # Part file stays private and is never presented as a successful archive.
    tmp = outdir / (".devnet-collector-" + uuid.uuid4().hex + ".partial")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, "wb") as raw:
            with zipfile.ZipFile(raw, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as z:
                z.writestr("README-PRIVATE.txt", body)
                z.writestr("manifest.json", json.dumps(report, indent=2, sort_keys=True) + "\n")
                for entry, data in records:
                    member = (PurePosixPath("payload") / PurePosixPath(entry["path"]))
                    info = zipfile.ZipInfo(str(member))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = (0o100755 if entry["executable"] else 0o100644) << 16
                    z.writestr(info, data)
            raw.flush()
            os.fsync(raw.fileno())
        with zipfile.ZipFile(tmp) as z:
            if z.testzip() is not None:
                raise ExportBlocked("Export ZIP CRC verification failed")
            expected = set(["README-PRIVATE.txt", "manifest.json"] + ["payload/" + r["path"] for r, _ in records])
            if set(z.namelist()) != expected:
                raise ExportBlocked("ZIP member list differs from manifest")
            for entry, _ in records:
                if digest(z.read("payload/" + entry["path"])) != entry["sha256"]:
                    raise ExportBlocked("ZIP file digest verification failed")
        for suffix in range(1000):
            filename = f"devnet-installed-apps-source-export-{date}{'-'+str(suffix) if suffix else ''}.zip"
            final = outdir / filename
            try:
                # Atomic hardlink refuses an existing target, even if another
                # collector created the same timestamp or it is a symlink.
                os.link(tmp, final, follow_symlinks=False)
            except FileExistsError:
                continue
            os.unlink(tmp)
            return final
        raise ExportBlocked("Too many output collisions; no ZIP overwritten")
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def export(home: Path, outdir: Path, apps: tuple[str, ...], allow_privacy_flags: bool = False) -> tuple[Path, dict]:
    records, report = collect(home, apps)
    if report["privacy_indicator_file_count"] and not allow_privacy_flags:
        names = ", ".join(report["privacy_flagged_paths"][:12])
        raise ExportBlocked("Source privacy indicators in " + names + ". No ZIP created. Review those files locally, then rerun with --allow-privacy-flags if safe to share.")
    outdir = _check_output_dir(outdir)
    return _write_atomic(outdir, records, report), report


def doctor(home: Path, apps: tuple[str, ...]) -> int:
    if home.is_symlink() or not home.is_dir():
        print("DOCTOR: invalid or symlinked home directory")
        return 2
    paths, warnings = gather(home.resolve(strict=True), apps)
    available = {p.as_posix() for p in paths if _components_are_safe(home, p)}
    print("Devnet Installed Apps Collector Doctor", VERSION)
    for app in apps:
        missing = [p for p in REQUIRED[app] if p not in available]
        print(f"{app}: {len(REQUIRED[app])-len(missing)}/{len(REQUIRED[app])} required source files found")
        for p in missing:
            print("  MISSING:", p)
        if missing:
            warnings.append("Incomplete sources for " + app)
    for w in warnings:
        print("WARNING:", w)
    return 2 if warnings else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Devnet installed app source collector")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Source HOME (normally leave unchanged)")
    parser.add_argument("--output-dir", type=Path, default=Path.home()/"Downloads")
    parser.add_argument("--app", choices=["both", "vr_stack", "wayvr"], default="both")
    parser.add_argument("--doctor", action="store_true", help="Report application prerequisites, no export")
    parser.add_argument("--allow-privacy-flags", action="store_true", help="Only after reviewing flagged source files locally")
    args = parser.parse_args(argv)
    apps = tuple(REQUIRED) if args.app == "both" else (args.app,)
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print("REFUSED: do not run this collector as root or with sudo", file=sys.stderr)
        return 2
    try:
        if args.doctor:
            return doctor(args.home, apps)
        path, report = export(args.home, args.output_dir, apps, args.allow_privacy_flags)
    except (OSError, ValueError) as exc:
        print("EXPORT BLOCKED:", str(exc), file=sys.stderr)
        return 2
    print("DEVNET SOURCE EXPORT VERIFIED")
    print("ZIP:", path)
    print("SHA256:", digest(path.read_bytes()))
    print("FILES:", report["files_collected"])
    print("PRIVACY-FLAGGED FILES:", report["privacy_indicator_file_count"])
    print("The ZIP is private (0600). Inspect source before sharing. Your installed applications were not modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
