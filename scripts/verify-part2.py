#!/usr/bin/env python3
"""Static local preflight checks; NOT a substitute for CI/runtime tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

WORKSPACES = (
    'implementations/typescript-node', 'frontend/vue', 'web',
    'sdk/react', 'sdk/react-native', 'sdk-ts',
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    checks = [
        ('go module', 'go 1.26' in (root / 'go.mod').read_text()),
        ('docker Go toolchain', 'golang:1.27.4-alpine' in (root / 'Dockerfile').read_text()),
        ('Spring Boot 4.0.10', '<version>4.0.10</version>' in (root / 'implementations/java/pom.xml').read_text()),
        ('Spring Web MVC starter', '<artifactId>spring-boot-starter-webmvc</artifactId>' in (root / 'implementations/java/pom.xml').read_text()),
        ('CI uses npm ci', 'npm ci' in (root / '.github/workflows/ci.yml').read_text()),
        ('CI checks extended parity', 'tests/parity_extended.py --wait 120' in (root / '.github/workflows/ci.yml').read_text()),
        ('CodeQL configured', 'github/codeql-action/init@v4' in (root / '.github/workflows/security.yml').read_text()),
        ('Trivy configured', 'aquasecurity/trivy-action@0.36.0' in (root / '.github/workflows/security.yml').read_text()),
        ('SBOM configured', 'anchore/sbom-action@v0' in (root / '.github/workflows/security.yml').read_text()),
    ]
    for workspace in WORKSPACES:
        manifest = json.loads((root / workspace / 'package.json').read_text(encoding='utf-8'))
        lockpath = root / workspace / 'package-lock.json'
        valid = False
        if lockpath.is_file():
            lock = json.loads(lockpath.read_text(encoding='utf-8'))
            valid = (lock.get('name') == manifest.get('name')
                     and lock.get('version') == manifest.get('version')
                     and int(lock.get('lockfileVersion', 0)) >= 2)
        checks.append((f'npm lockfile {workspace}', valid))
    for name, valid in checks:
        print(('PASS' if valid else 'FAIL') + ' ' + name)
    print('RESULTADO=' + ('PASS' if all(ok for _, ok in checks) else 'FAIL'))
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == '__main__':
    raise SystemExit(main())
