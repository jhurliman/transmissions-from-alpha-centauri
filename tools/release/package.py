"""Build a portable ZIP from the checksum allowlist, including real LFS bytes."""
import argparse, json, zipfile
from pathlib import Path
from verify import ROOT, MANIFEST, verify, sha256

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args=parser.parse_args()
manifest=verify()
output=Path(args.output).expanduser().resolve()
if output.exists():
    raise SystemExit('Refusing to overwrite: '+str(output))
output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for relative in sorted([*manifest['files'],str(MANIFEST.relative_to(ROOT))]):
        if relative.startswith(('private/','references/','archives/')):
            raise SystemExit('Excluded release path: '+relative)
        archive.write(ROOT/relative,'transmissions-from-alpha-centauri/'+relative)
print(json.dumps({'file':output.name,'bytes':output.stat().st_size,'sha256':sha256(output)},indent=2))
