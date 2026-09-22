"""Maintainer-only release capture: hash the explicit Git index allowlist.
Run after staging the intended release files and before final commit/tag.
"""
import json, subprocess
from pathlib import Path
from verify import ROOT, MANIFEST, sha256, check_required

paths = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
check_required(paths)
files = {}
for relative in sorted(filter(None, paths)):
    path=ROOT/relative
    if path==MANIFEST:
        continue
    if relative.startswith(('private/','references/','archives/')) or path.is_symlink():
        raise SystemExit('Excluded release path: '+relative)
    files[relative]={'bytes':path.stat().st_size,'sha256':sha256(path)}
manifest={
    'version':'v1.0.0',
    'approved_date':'2026-09-21',
    'approval_quote':"we did it! we're done. v1.0.",
    'source_iteration':258,
    'scope':'Approved illustration; frozen-state reproduction, not a game release',
    'blender_version':'5.2.1 LTS',
    'blender_build_hash':'9e2066aef7ef',
    'authoritative_image':'releases/v1.0.0/main-4k.png',
    'resolution':[3840,2885],
    'files':files,
}
MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
print('Captured',len(files),'files')
