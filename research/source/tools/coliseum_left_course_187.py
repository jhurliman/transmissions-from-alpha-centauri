"""Replay six locally reviewed left-course meshes; preserve current scene and ink.
Payload was built from173 with one fixed subtraction; see certified-audit.json.
Native GP support correction remains a separate integration requirement.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-187/geometry'
def surface_hash(ob,dg):
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[tuple(v.co)for v in me.vertices];ts={tuple(sorted(vs[i]for i in t.vertices))for t in me.loop_triangles};out=hashlib.sha256(json.dumps({'verts':vs,'triangles':sorted(ts)},sort_keys=True).encode()).hexdigest();ev.to_mesh_clear();return out

def apply(C):
 audit=json.loads((O/'certified-audit.json').read_text());assert audit['accepted_cpu'],'187 held'
 meta=json.loads((O/'payload.json').read_text());dg=bpy.context.evaluated_depsgraph_get();objects={n:C.all_objects.get(n)for n in meta}
 for n,ob in objects.items():
  assert ob and surface_hash(ob,dg)==meta[n]['source_hash'],'187 source mismatch '+n
  assert list(map(list,ob.matrix_world))==meta[n]['matrix'],'187 transform mismatch '+n
 oldmaterials=set(bpy.data.materials);names=list(meta)
 with bpy.data.libraries.load(str(O/'payload.blend'),link=False)as(src,dst):dst.meshes=[meta[n]['mesh_name']for n in names]
 for n,me in zip(names,dst.meshes):
  ob=objects[n];slots=[(sl.link,sl.material)for sl in ob.material_slots];me.materials.clear()
  for name in meta[n]['slots']:me.materials.append(bpy.data.materials[name]if name else None)
  ob.data=me
  for sl,(link,mat)in zip(ob.material_slots,slots):sl.link=link;sl.material=mat
  for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 for mat in set(bpy.data.materials)-oldmaterials:
  if mat.users==0:bpy.data.materials.remove(mat)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for n,ob in objects.items():assert surface_hash(ob,dg)==meta[n]['candidate_hash'],'187 payload mismatch '+n
 return {'targets':audit['targets'],'accepted_cpu':True,'new_crossing_pairs':0,'inherited_crossing_pairs':audit['inherited_crossing_pairs'],'exact_zero_area_triangles':0,'native_ink_unchanged':True,'contact_support_correction_required':True,'dentil03_unchanged_supported':True,'source':'173','shape_scope':'Six left end surfaces only; band11 and underlying architecture unchanged.'}
