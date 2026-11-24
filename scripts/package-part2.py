#!/usr/bin/env python3
"""Create a ZIP containing ONLY known EyeX part-2 modifications.

Do not include credentials, .env, node_modules, or unrelated untracked files.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

WORKSPACES = (
    'implementations/typescript-node', 'frontend/vue', 'web',
    'sdk/react', 'sdk/react-native', 'sdk-ts',
)
EXPECTED_NEW = (
    '.github/workflows/security.yml', '.github/dependabot.yml',
    'tests/parity_extended.py',
    'scripts/create-lockfiles.py', 'scripts/package-part2.py',
    'scripts/verify-part2.py', 'docs/PART2_CI_SECURITY.md',
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    for workspace in WORKSPACES:
        lock_path = root / workspace / 'package-lock.json'
        if not lock_path.is_file():
            raise SystemExit(f'ERROR: missing lockfile {lock_path}; run scripts/create-lockfiles.py')
        contents = json.loads(lock_path.read_text(encoding='utf-8'))
        if int(contents.get('lockfileVersion', 0)) < 2:
            raise SystemExit(f'ERROR: invalid lockfile {lock_path}')
    changed = subprocess.run(
        ['git', 'diff', '--name-only', '--diff-filter=ACMRT', '-z'],
        cwd=root, check=True, capture_output=True,
    ).stdout.decode('utf-8').strip('\0').split('\0')
    allowed = set(changed) | set(EXPECTED_NEW) | {
        f'{workspace}/package-lock.json' for workspace in WORKSPACES
    }
    # Only explicitly supported files, not all untracked files.
    files = sorted(path for path in allowed if path and (root / path).is_file())
    required = set(EXPECTED_NEW) | {f'{ws}/package-lock.json' for ws in WORKSPACES}
    if not required.issubset(files):
        raise SystemExit('ERROR: required part-2 files missing')
    output = root.parent / 'eyex-part2-modified-files.zip'
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(root / path, arcname=path)
        archive.writestr('MODIFIED_FILES.txt', '\n'.join(files) + '\n')
    print(f'ARCHIVOS_MODIFICADOS={len(files)}')
    print(f'ZIP_GENERADO={output}')
    print('RESULTADO=PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
