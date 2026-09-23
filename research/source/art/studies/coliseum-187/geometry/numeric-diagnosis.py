import bpy,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';bpy.ops.wm.open_mainfile(filepath=str(O/'fixed-shape-technical.blend'));out=[]
for n in json.load(open(R/'config/coliseum-left-course-187.json'))['targets']:
 ob=bpy.data.objects[n];me=ob.data;me.calc_loop_triangles();rr=[]
 for t in me.loop_triangles:
  p=np.array([tuple(me.vertices[i].co)for i in t.vertices]);ar=float(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))/2)
  if ar<1e-10:rr.append({'poly':t.polygon_index,'vertices':list(t.vertices),'coords':p.tolist(),'area':ar,'polygon_vertices':list(me.polygons[t.polygon_index].vertices)})
 out.append({'object':n,'triangles':rr})
(O/'zero-triangle-detail.json').write_text(json.dumps(out,indent=2));print(out)
