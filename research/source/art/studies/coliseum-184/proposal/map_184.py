import bpy,json,sys,numpy as np
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-184/proposal';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();names=[r['object']for r in json.loads((R/'art/studies/coliseum-157/geometry/audit.json').read_text())['targets']];out=[]
for name in names:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();M=ob.matrix_world;N=M.to_3x3().inverted().transposed();v=[M@q.co for q in me.vertices];tag=me.attributes.get('157 Exposed course core');faces=[]
 for f in me.polygons:
  if not tag or tag.data[f.index].value<.5:continue
  p=[v[i]for i in f.vertices];uv=[world_to_camera_view(s,s.camera,q)for q in p];bbox=[min(q.x for q in uv)*3840,min(1-q.y for q in uv)*2885,max(q.x for q in uv)*3840,max(1-q.y for q in uv)*2885]
  if bbox[2]<2115 or bbox[0]>2220 or bbox[3]<580 or bbox[1]>685:continue
  faces.append({'face':f.index,'slot':f.material_index,'material':ob.material_slots[f.material_index].material.name,'bbox':bbox,'normal_world':list((N@f.normal).normalized()),'world_vertices':[list(q)for q in p],'vertices':list(f.vertices)})
 out.append({'object':name,'faces':len(me.polygons),'core_faces_in_context':faces,'matrix':list(map(list,M))});ev.to_mesh_clear()
(O/'native-core-faces.json').write_text(json.dumps({'source':'173','context':[2115,580,2220,685],'targets':out},indent=2));print([(r['object'],len(r['core_faces_in_context']))for r in out])
