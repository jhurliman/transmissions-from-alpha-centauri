"""Recheck frozen contact intervals against the saved delivery, without mutation."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import snapshot,digest,tree
from coliseum_contact_certificate_169 import certify
O=R/'art/studies/coliseum-168';P=R/'art/studies/coliseum-169/contact'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-166/scene.blend'))
gp=bpy.data.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy();payload=json.loads((P/'clip-payload.json').read_text());transform=json.loads((P/'source-transform.json').read_text())
assert digest(old)==payload['source_digest']==transform['attribute_digest']
assert [list(v)for v in M]==transform['matrix_world']
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));gp=bpy.data.objects['110 Landmark contact ink']
assert [list(v)for v in gp.matrix_world]==transform['matrix_world']
assert digest(snapshot(gp))==json.loads((O/'contact-ink-preservation.json').read_text())['after_digest']
cert=certify(payload,old,M,tree(bpy.data.collections['110 Coliseum detailed front ruin']))
out={k:v for k,v in cert.items()if k!='intervals'}
out.update(support_source='Actual saved 168 geometry',clip_payload_sha256=hashlib.sha256((P/'clip-payload.json').read_bytes()).hexdigest(),saved_scene_transform_matches_source=True,saved_scene_after_digest=digest(snapshot(gp)),no_geometry_or_clip_interval_change=True)
(O/'continuous-contact-support.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
