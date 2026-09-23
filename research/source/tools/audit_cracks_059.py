import bpy,bmesh,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-059';results={}
for variant in ['density','network']:
 bpy.ops.wm.open_mainfile(filepath=str(O/(variant+'.blend')));s=bpy.context.scene;checks=[]
 for host in s.objects:
  if not host.instance_collection or not host.instance_collection.name.startswith('059 '):continue
  for o in host.instance_collection.objects:
   if not any(m.type=='BOOLEAN' and m.name.startswith('059') for m in o.modifiers):continue
   me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me)
   check={'part':o.name,'faces':len(bm.faces),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':abs(bm.calc_volume())};checks.append(check);assert check['faces'] and check['volume']>0;bm.free()
 results[variant]={'parts':checks,'camera':list(s.camera.location),'rotation':list(s.camera.rotation_euler),'lens':s.camera.data.lens}
 if variant=='network':bpy.data.libraries.write(str(O/'fracture-proof-kit.blend'),{o.instance_collection for o in s.objects if o.instance_collection and o.instance_collection.name.startswith('059 ')},fake_user=True)
assert results['density']['camera']==results['network']['camera']
(O/'validation.json').write_text(json.dumps(results,indent=2))
