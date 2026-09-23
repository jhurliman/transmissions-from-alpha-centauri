import bpy,sys,json
from mathutils import Vector
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri')
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/service-fit-242/scene.blend'))
s=bpy.context.scene
parts=[]
for i in bpy.context.evaluated_depsgraph_get().object_instances:
 if i.parent and i.parent.original.name.startswith('Architecture | duct_M') and i.object.type=='MESH':
  pts=[i.matrix_world@Vector(v) for v in i.object.bound_box];lo=[min(p[a] for p in pts)for a in range(3)];hi=[max(p[a]for p in pts)for a in range(3)]
  if lo[1]<6 and hi[1]>5:parts.append((lo,hi))
print('DUCT_MAX_Y',max(p[1][1]for p in parts),'DUCT_MAX_X',max(p[1][0]for p in parts),flush=True)
assert max(p[1][1]for p in parts)<5.97
assert max(p[1][0]for p in parts)<-8.25
for su in ['', '.001','.002','.003']:
 o=bpy.data.objects['U-return bracket'+su]
 assert len(o.data.polygons)==8
 counts={}
 for p in o.data.polygons:
  vs=list(p.vertices)
  for a,b in zip(vs,vs[1:]+vs[:1]):counts[tuple(sorted((a,b)))]=counts.get(tuple(sorted((a,b))),0)+1
 assert set(counts.values())=={2}
print('PASS four closed bracket meshes clear duct bounding envelope; pier termination below receiver roof',flush=True)
