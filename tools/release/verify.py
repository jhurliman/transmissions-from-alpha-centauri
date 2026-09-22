# SPDX-FileCopyrightText: 2026 John Hurliman and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. This program is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See LICENSES/GPL-3.0-or-later.txt for the full terms.
#
"""Verify the frozen release using only Python's standard library."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / 'releases/v1.0.0/manifest.json'
PREFIX = 'releases/v1.0.0/'
REQUIRED = {PREFIX + name for name in ('scene.blend', 'main-4k.png', 'render.py')}
REQUIRED.update(PREFIX + 'runtime/' + name + '.py' for name in (
    'alley_repeat_212', 'coliseum_ink_regression_149',
    'coliseum_foreground_visibility_156', 'coliseum_foreground_visibility_161',
    'architecture_ink_visibility_192', 'architecture_ink_visibility_205',
    'architecture_ink_visibility_207', 'alley_roof_seating_215', 'footing_ground_guard_244'))

def check_required(files):
    missing = REQUIRED - set(files)
    if missing:
        raise SystemExit('Incomplete release allowlist: ' + ', '.join(sorted(missing)))
    for relative in REQUIRED:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit('Missing required file: ' + relative)
        with path.open('rb') as stream:
            header = stream.read(128)
        if header.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise SystemExit('Git LFS pointer instead of real data: ' + relative)
    image = ROOT / PREFIX / 'main-4k.png'
    with image.open('rb') as stream:
        header = stream.read(24)
    import struct
    if header[:8] != b'\x89PNG\r\n\x1a\n' or struct.unpack('>II', header[16:24]) != (3840, 2885):
        raise SystemExit('Authoritative image is not a 3840 x 2885 PNG')

def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def verify():
    manifest = json.loads(MANIFEST.read_text())
    check_required(manifest['files'])
    if manifest.get('authoritative_image') != PREFIX + 'main-4k.png':
        raise SystemExit('Wrong authoritative image entry')
    errors = []
    for relative, record in manifest['files'].items():
        path = ROOT / relative
        if not path.resolve().is_relative_to(ROOT.resolve()):
            errors.append(f'Unsafe path: {relative}')
        elif not path.is_file():
            errors.append(f'Missing: {relative}')
        elif path.stat().st_size != record['bytes'] or sha256(path) != record['sha256']:
            errors.append(f'Changed or missing Git LFS data: {relative}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f"Verified {len(manifest['files'])} files for {manifest['version']}.")
    return manifest

if __name__ == '__main__':
    verify()
