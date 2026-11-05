#!/usr/bin/env python3
"""Deploy only the preview integration; do not manage the Neovim configuration."""
import argparse
import ast
import importlib.util
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
def managed_link(destination, source):
    if destination.is_symlink():
        return destination.resolve() == source.resolve()
    if destination.is_dir() and source.is_dir():
        return all(managed_link(destination / entry.name, entry)
                   for entry in source.iterdir() if entry.name != '__pycache__')
    return False


def preview(target):
    if sys.platform != 'linux':
        raise ValueError('Use ./setup apply for macOS deployment')
    common = REPO / 'dotfiles/common'
    paths = ['tools/remote-tex-preview', '.local/bin/remote-tex-preview',
             '.local/share/nvim/site/plugin/remote-tex-preview.lua',
             '.config/remote-tex-preview/config.json',
             '.config/remote-tex-preview/config.example.json']
    for rel in paths:
        destination, source = target / rel, common / rel
        if not source.exists(): raise ValueError('Missing source: ' + str(source))
        if managed_link(destination, source): continue
        if destination.exists() or destination.is_symlink():
            raise ValueError('Conflict (unchanged): ' + str(destination))
        parent = destination.parent
        while parent != target:
            if parent.is_symlink(): raise ValueError('Parent is a symlink (unchanged): ' + str(parent))
            parent = parent.parent
    for rel in paths:
        destination = target / rel
        if managed_link(destination, common / rel): continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(os.path.relpath(common / rel, destination.parent))
        print('Linked:', destination)


def check(target):
    sys.dont_write_bytecode = True
    if sys.version_info < (3, 10): raise ValueError('Python 3.10+ required')
    common = REPO / 'dotfiles/common'
    for path in (common / 'tools/remote-tex-preview').rglob('*.py'):
        ast.parse(path.read_text(), filename=str(path))
    ast.parse(Path(__file__).read_text(), filename=__file__)
    spec = importlib.util.spec_from_file_location('rtp_check', common / 'tools/remote-tex-preview/rtp.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.config(common / '.config/remote-tex-preview/config.json')
    print('OK: Python syntax and shared preview config')
    local = target / '.config/remote-tex-preview/config.json'
    if local.exists(): module.config(local); print('OK: deployed preview config')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['check', 'preview'])
    parser.add_argument('--target', type=Path, default=Path.home())
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    if args.action == 'preview': preview(target)
    else: check(target)

if __name__ == '__main__':
    try: main()
    except (OSError, ValueError) as exc:
        print('setup:', exc, file=sys.stderr); sys.exit(1)
