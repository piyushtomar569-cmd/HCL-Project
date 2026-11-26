#!/usr/bin/env python3
"""
File Integrity Verification
Create SHA-256 baselines for files in a selected directory and verify them later.

Examples:
  python integrity_check.py baseline ./sample_files
  python integrity_check.py verify ./sample_files
  python integrity_check.py baseline ./sample_files --manifest ./baseline.json
  python integrity_check.py verify ./sample_files --manifest ./baseline.json

The manifest is written outside the scanned directory by default, so it is not
included in its own baseline. Use only on files you own or are authorized to assess.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MANIFEST = Path("integrity-baseline.json")
CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(target: Path, manifest: Path) -> list[Path]:
    if target.is_file():
        return [target] if target.resolve() != manifest.resolve() else []
    if not target.is_dir():
        raise FileNotFoundError(f"Target does not exist: {target}")

    files = []
    for path in target.rglob("*"):
        if path.is_file() and path.resolve() != manifest.resolve():
            files.append(path)
    return sorted(files, key=lambda p: str(p).lower())


def make_baseline(target: Path, manifest: Path) -> int:
    files = collect_files(target, manifest)
    entries = {}
    for path in files:
        relative = str(path.relative_to(target)) if target.is_dir() else path.name
        try:
            entries[relative] = {
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        except OSError as exc:
            print(f"SKIPPED: {relative} ({exc})")

    payload = {
        "format": "file-integrity-baseline-v1",
        "algorithm": "SHA-256",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "target": str(target.resolve()),
        "files": entries,
    }
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Baseline saved: {manifest.resolve()}")
    print(f"Files recorded: {len(entries)}")
    return 0


def verify(target: Path, manifest: Path) -> int:
    if not manifest.is_file():
        print(f"ERROR: Baseline not found: {manifest}", file=sys.stderr)
        return 2

    try:
        baseline = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: Could not read baseline: {exc}", file=sys.stderr)
        return 2

    if baseline.get("format") != "file-integrity-baseline-v1":
        print("ERROR: Unsupported or invalid baseline format.", file=sys.stderr)
        return 2

    expected = baseline.get("files", {})
    current_paths = collect_files(target, manifest)
    current = {}
    for path in current_paths:
        relative = str(path.relative_to(target)) if target.is_dir() else path.name
        try:
            current[relative] = sha256_file(path)
        except OSError as exc:
            print(f"UNREADABLE: {relative} ({exc})")

    changed = []
    missing = sorted(set(expected) - set(current))
    added = sorted(set(current) - set(expected))

    for relative in sorted(set(expected) & set(current)):
        if expected[relative].get("sha256") != current[relative]:
            changed.append(relative)

    print(f"Baseline: {manifest.resolve()}")
    print(f"Files in baseline: {len(expected)} | Files now: {len(current)}")
    if not changed and not missing and not added:
        print("PASS: No file changes detected.")
        return 0

    for item in changed:
        print(f"CHANGED: {item}")
    for item in missing:
        print(f"MISSING: {item}")
    for item in added:
        print(f"ADDED:   {item}")

    print("REVIEW: Differences found. Confirm whether each change was expected.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and verify SHA-256 file-integrity baselines.")
    parser.add_argument("action", choices=("baseline", "verify"), help="Create a baseline or compare against it.")
    parser.add_argument("target", type=Path, help="File or directory to check.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST,
                        help=f"Baseline JSON path (default: {DEFAULT_MANIFEST})")
    args = parser.parse_args()

    try:
        if args.action == "baseline":
            return make_baseline(args.target, args.manifest)
        return verify(args.target, args.manifest)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
