"""Read-only R tessellation diagnosis; no mutation of frozen123 tools/scenes."""
import bpy,bmesh,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-124/repair';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-123/repair/geometry.blend'));ob=bpy.data.objects['COL110 U8 fractured upper wall R'];m=ob.data;m.calc_loop_triangles();edges={}
for ti,t in enumerate(m.loop_triangles):
 for k in range(3):edges.setdefault(tuple(sorted((t.vertices[k],t.vertices[(k+1)%3]))),[]).append(ti)
rows=[]
for edge,triangles in edges.items():
 if len(triangles)==2:continue
 fs=sorted(set(m.loop_triangles[i].polygon_index for i in triangles))
 rows.append({'edge':list(edge),'world_endpoints':[list(ob.matrix_world@m.vertices[i].co)for i in edge],'length_world_m':((ob.matrix_world@m.vertices[edge[0]].co)-(ob.matrix_world@m.vertices[edge[1]].co)).length,'incident_triangles':[{'id':i,'source_face':m.loop_triangles[i].polygon_index,'vertices':list(m.loop_triangles[i].vertices),'area':m.loop_triangles[i].area}for i in triangles],'source_faces':[{'id':i,'vertices':list(m.polygons[i].vertices),'normal':list(m.polygons[i].normal),'area':m.polygons[i].area,'world_center':list(ob.matrix_world@m.polygons[i].center)}for i in fs]})
d={'polygon_topology':topology(ob),'bad_render_edges':rows,'interpretation':'Four triangle incidences per edge, not open boundary; blind hole fill is inappropriate.'};O.mkdir(parents=True,exist_ok=True);(O/'diagnosis.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
