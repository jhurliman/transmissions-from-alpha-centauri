import bpy,json
from pathlib import Path
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122/rhythm';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-121/scene.blend'));old={}
for j in range(5,14):
 ob=bpy.data.objects.get('COL110 U%d sill wall'%j);old[ob.name]=BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[tuple(f.vertices)for f in ob.data.polygons])
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));rows=[]
for name,tree in old.items():
 ob=bpy.data.objects[name];mask=ob.data.attributes.get('122 Drain interior')or ob.data.attributes.new('122 Drain interior','FLOAT','FACE')
 for face in ob.data.polygons:
  near=tree.find_nearest(ob.matrix_world@face.center);mask.data[face.index].value=float(near and near[0]is not None and near[3]>.004)
 rows.append({'object':name,'drain_interior_faces':sum(d.value>.5 for d in mask.data)})
a=json.loads((O/'audit.json').read_text());a['drain_face_masks']=rows;(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print(rows)
