import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_cornice_failure_157 import apply,TARGETS
O=R/'art/studies/coliseum-157/geometry';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
def hashes():
 return {o.name:hashlib.sha256(repr(([tuple(v.co)for v in o.data.vertices],[tuple(p.vertices)for p in o.data.polygons],[p.material_index for p in o.data.polygons],[tuple(n.vector)for n in o.data.corner_normals])).encode()).hexdigest()for o in s.objects if o.type=='MESH'and o.name not in TARGETS}
hp=O/'baseline-hashes.json'
before=hashes()
before={n:h for n,h in before.items()if n not in TARGETS}
hp.write_text(json.dumps(before))
try:d=apply(C)
except Exception as e:(O/'failure.json').write_text(json.dumps({'error':str(e)},indent=2));raise
(O/'audit.json').write_text(json.dumps(d,indent=2));after=hashes();(O/'preservation.json').write_text(json.dumps({'non_target_count':len(before),'changed':[n for n in before if before[n]!=after.get(n)]},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('157 BUILD READY — NO RENDER',flush=True)
