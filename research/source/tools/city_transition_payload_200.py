import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-transition-200';sys.path.insert(0,str(R/'tools'));from city_transition_refinement_200 import _mesh_digest
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/beam-rust-197/scene.blend'));before={o.name:dict(mesh_hash=_mesh_digest(o),matrix=[list(r)for r in o.matrix_world],materials=[s.material.name if s.material else None for s in o.material_slots])for o in bpy.data.collections['133 Ruined transition structures'].objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));C=bpy.data.collections['133 Ruined transition structures'];rows=[];ids=set()
for ob in C.objects:
 if ob.type!='MESH':continue
 h=_mesh_digest(ob);changed=h!=before[ob.name]['mesh_hash'];mats=[s.material for s in ob.material_slots];ids.update(m for m in mats if m)
 if changed:ids.add(ob.data)
 rows.append(dict(object=ob.name,before=before[ob.name],after_mesh_hash=h,mesh=ob.data.name if changed else None,materials=[m.name if m else None for m in mats],remove_modifiers=changed))
bpy.data.libraries.write(str(O/'payload.blend'),ids,fake_user=True)
(O/'payload.json').write_text(json.dumps(dict(rows=rows,materials=sorted({m.name for m in ids if isinstance(m,bpy.types.Material)}),meshes=sorted({m.name for m in ids if isinstance(m,bpy.types.Mesh)})),indent=2));print('200_PAYLOAD_READY',len(rows),len(ids),flush=True)
