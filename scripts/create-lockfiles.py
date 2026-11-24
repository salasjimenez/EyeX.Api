#!/usr/bin/env python3
"""Resolve/reconcile npm v3 lockfiles for the six EyeX Node workspaces.

This script requires a working npm registry connection. It does not execute
third-party install scripts and does not modify package.json.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

WORKSPACES = (
    'implementations/typescript-node',
    'frontend/vue',
    'web',
    'sdk/react',
    'sdk/react-native',
    'sdk-ts',
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    npm_executable = shutil.which('npm')
    if npm_executable is None or shutil.which('node') is None:
        print('ERROR: Node.js and npm are required', file=sys.stderr)
        return 1
    for workspace in WORKSPACES:
        folder = root / workspace
        package_json = folder / 'package.json'
        lock_json = folder / 'package-lock.json'
        if not package_json.exists():
            print(f'ERROR: package.json missing: {workspace}', file=sys.stderr)
            return 1
        manifest_text = package_json.read_bytes()
        print(f'\n=== RESOLVE LOCKFILE {workspace} ===', flush=True)
        cmd = [
            npm_executable, 'install', '--package-lock-only', '--ignore-scripts',
            '--no-audit', '--no-fund',
        ]
        subprocess.run(cmd, cwd=folder, check=True)
        if package_json.read_bytes() != manifest_text:
            print(f'ERROR: npm modified {package_json}; restore it manually', file=sys.stderr)
            return 1
        if not lock_json.is_file():
            print(f'ERROR: lockfile missing: {lock_json}', file=sys.stderr)
            return 1
        manifest = json.loads(manifest_text)
        lockfile = json.loads(lock_json.read_text(encoding='utf-8'))
        if lockfile.get('lockfileVersion', 0) < 2:
            print(f'ERROR: outdated lockfile format: {workspace}', file=sys.stderr)
            return 1
        for field in ('name', 'version'):
            if lockfile.get(field) != manifest.get(field):
                print(f'ERROR: lockfile {field} mismatch in {workspace}', file=sys.stderr)
                return 1
        print(f'PASS {workspace}/package-lock.json')
    print('\nRESULTADO=LOCKFILES_PREPARED')
    print('NEXT: npm ci and builds must still be validated before commit.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
