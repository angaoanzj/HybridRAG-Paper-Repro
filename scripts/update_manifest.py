#!/usr/bin/env python3
"""Regenerate the release manifest from the files selected for distribution."""

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    selected = subprocess.check_output(
        ["git", "ls-files", "--cached", "-z"],
        cwd=ROOT,
    ).decode("utf-8").split("\0")
    manifest = {}
    for relative in sorted(set(selected)):
        if not relative or relative == "MANIFEST.json":
            continue
        path = ROOT / relative
        if path.is_file():
            manifest[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Recorded {len(manifest)} release files.")


if __name__ == "__main__":
    main()
