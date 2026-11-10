#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["tomlkit==0.13.3"]
# ///
"""Merge repository preferences into a writable Codex config."""

from __future__ import annotations

import argparse
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import tomlkit
from tomlkit.exceptions import ParseError
from tomlkit.items import InlineTable, Table
from tomlkit.toml_document import TOMLDocument


def merge(target: TOMLDocument | Table | InlineTable, source: TOMLDocument | Table | InlineTable) -> None:
    """Override supplied keys recursively; replace arrays instead of appending."""
    for key, value in source.items():
        if isinstance(value, (Table, InlineTable)):
            child = target.get(key)
            if not isinstance(child, (Table, InlineTable)):
                child = tomlkit.table()
                target[key] = child
            merge(child, value)
        else:
            target[key] = value


def apply(source: Path, target: Path, *, check: bool = False) -> bool:
    """Preserve unmentioned settings, backing up changes before atomic replace."""
    preferences = tomlkit.parse(source.read_text())
    if target.is_symlink():
        raise ValueError(f"{target} is a symlink; move it aside before merging")
    before = target.read_bytes() if target.exists() else None
    document = tomlkit.parse(before.decode() if before is not None else "")
    merge(document, preferences)
    after = tomlkit.dumps(document).encode()
    if before == after:
        print(f"Unchanged: {target}")
        return False
    if check:
        print(f"Would update: {target}")
        return True

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(after)
            stream.flush()
            os.fsync(stream.fileno())
        # Do not overwrite edits made while parsing and preparing the merge.
        current = target.read_bytes() if target.exists() else None
        if target.is_symlink() or current != before:
            raise RuntimeError(f"{target} changed during merge; retry when idle")
        if before is not None:
            backup_dir = target.parent / "backups"
            backup_dir.mkdir(mode=0o700, exist_ok=True)
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = backup_dir / f"config.toml.{stamp}"
            with backup.open("xb") as stream:
                os.chmod(backup, 0o600)
                stream.write(before)
            print(f"Backup: {backup}")
        temporary.replace(target)
        print(f"Updated: {target}")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--target",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml",
    )
    parser.add_argument("--check", action="store_true", help="Preview without writing")
    args = parser.parse_args()
    try:
        apply(args.source, args.target, check=args.check)
    except ParseError:
        # Parser errors may quote private config values; do not print their text.
        parser.exit(1, f"Invalid TOML in {args.source} or {args.target}; no config replaced.\n")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Codex settings merge failed: {error}\n")


if __name__ == "__main__":
    main()
