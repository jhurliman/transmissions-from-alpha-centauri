# SPDX-License-Identifier: GPL-3.0-or-later
"""Check historical text sources without importing or executing them."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def verify():
    manifest = json.loads((ROOT / "manifest.json").read_text())
    expected = set()
    for record in manifest["files"]:
        name = record["path"]
        path = ROOT / name
        if path.is_symlink() or not path.resolve().is_relative_to((ROOT / "source").resolve()):
            raise SystemExit("Unsafe source path: " + name)
        data = path.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise SystemExit("Source checksum mismatch: " + name)
        if path.suffix == ".py":
            ast.parse(data.decode(), filename=name)
        elif path.suffix == ".json":
            json.loads(data)
        expected.add(name)
    actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / "source").rglob("*") if p.is_file()}
    if actual != expected:
        raise SystemExit("Source inventory mismatch: " + repr(sorted(actual ^ expected)))
    catalog = json.loads((ROOT / "studies.json").read_text())
    assert [s["study"] for s in catalog["studies"]] == list(range(1, 259))
    assert all(set(s["files"]) <= expected for s in catalog["studies"])
    print(f"Verified {len(expected)} historical text files and 258 catalog entries; replay remains unverified.")

if __name__ == "__main__":
    verify()
