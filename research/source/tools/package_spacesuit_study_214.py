from pathlib import Path
from PIL import Image
import json,zipfile,hashlib,re,urllib.request
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-spacesuit-214'
rows=json.loads((O/'pixel/exports.json').read_text());checks=[]
for row in rows:
 p=O/'pixel'/row['file'];im=Image.open(p);a=np.array(im.convert('RGBA'));alpha=set(np.unique(a[:,:,3]).tolist());used=len(np.unique(a[:,:,:3][a[:,:,3]>0],axis=0));bbox=im.convert('RGBA').getchannel('A').getbbox()
 assert im.mode=='P' and alpha=={0,255} and used<=int(row['file'].split('-')[-1][:-5])
 assert bbox[3]-bbox[1]==row['logical_silhouette_height']
 checks.append({'file':row['file'],'indexed':True,'binary_alpha':True,'actual_body_height':bbox[3]-bbox[1],'opaque_colors':used})
for n in ['traveler-a','traveler-b']:
 assert (O/f'anime/{n}-anime.png').read_bytes()==(O/f'anime/{n}-anime-raw.png').read_bytes()
report={'study':214,'verdict':'Ready for user comparison; not user-approved','actual_review':['All four generated masters preserve silver suit, dark straps/cuffs and boots, rear-view identity and hair.','Both pixel detail composites inspected after two-tone sage correction; Traveler-A yellow badge remains a readable accent, Traveler-B brown/green hair remains distinct.','Actual scene-lit anime detail inspected: restrained native light response, both figures stand in clear road, no old proxy or ghost contact ink.','Native47/49pixel grids simplify fine suit bands; double detail preserves more structure.','No claim of volumetric self-shadow, contact shadows, or3Dgeometry acceptance.'],'technical_checks':checks,'light_test':json.loads((O/'anime/lighting-response-audit.json').read_text()),'user_approved':False}
(O/'review.json').write_text(json.dumps(report,indent=2))
p=O/'composite-audit.json';data=json.loads(p.read_text())
for row in data:row.pop('palette_colors',None);row['palette_budget']=24
p.write_text(json.dumps(data,indent=2))
# Explicit allowlist; exclude private originals and external references.
allowed=[]
for pattern in ['README.md','provenance.json','prompts.json','review.json','composite-audit.json','pixel/*.png','pixel/*.json','pixel/*-prompt.txt','anime/*.png','anime/*.json','anime/*.md','anime/*-prompt.txt','anime/proof.blend','*-scene.png','*-scene-detail.png']:
 allowed.extend(O.glob(pattern))
allowed=sorted(set(allowed));manifest=[{'file':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in allowed]
(O/'package-manifest.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(O/'spacesuit-character-assets-214.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in allowed+[O/'package-manifest.json']:z.write(p,p.relative_to(O))
page=R/'prototype/review-214.html';html=page.read_text();links=set(re.findall(r'(?:src|href)="(/art/[^\"]+)"',html));missing=[u for u in links if not (R/u.lstrip('/')).exists()];assert not missing,missing
assert len(re.findall('data-mode=',html))==3
print(json.dumps({'assets':len(allowed),'sprite_checks':len(checks),'page_links':len(links),'missing':missing,'buttons':3,'zip_bytes':(O/'spacesuit-character-assets-214.zip').stat().st_size},indent=2))
