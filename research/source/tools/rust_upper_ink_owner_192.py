import bpy,json,sys,collections
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/plate-runoff-192/ink-diagnostic';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-188/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.hide_render or (ob.type=='MESH' and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;rows=[];edges=[];bounds=[]
roi=(370,275,430,330)
def xy(p):
 v=world_to_camera_view(s,cam,p);return(v.x*3840,(1-v.y)*2885,v.z)
def intersects(ps):return not(max(p[0]for p in ps)<roi[0]or min(p[0]for p in ps)>roi[2]or max(p[1]for p in ps)<roi[1]or min(p[1]for p in ps)>roi[3])
for y in range(roi[1],roi[3],3):
 for x in range(roi[0],roi[2],3):
  q=iv@Vector((2*(x+.5)/3840-1,1-2*(y+.5)/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if ok:rows.append(dict(pixel=[x,y],object=ob.name,face=fi,point=list(p),normal=list(n)))
for inst in dg.object_instances:
 ob=inst.object
 if ob.type!='MESH':continue
 mat=inst.matrix_world;bp=[xy(mat@Vector(p))for p in ob.bound_box]
 if not intersects(bp)or max(p[2]for p in bp)<0:continue
 bounds.append(ob.name);me=ob.to_mesh();vp=[mat@v.co for v in me.vertices];pp=[xy(v)for v in vp]
 for edge in me.edges:
  a,b=[pp[i]for i in edge.vertices]
  if not intersects([a,b])or max(a[2],b[2])<0:continue
  samples=[]
  for t in (0,.25,.5,.75,1):
   pt=vp[edge.vertices[0]].lerp(vp[edge.vertices[1]],t);sx,sy,sz=xy(pt)
   if not(roi[0]<=sx<=roi[2]and roi[1]<=sy<=roi[3]):continue
   delta=pt-origin;hit=s.ray_cast(dg,origin,delta.normalized());samples.append(dict(pixel=[sx,sy],point=list(pt),first_hit=hit[4].name if hit[0]else None,gap=delta.length-(hit[1]-origin).length if hit[0]else None))
  edges.append(dict(object=ob.name,edge=edge.index,screen=[a,b],world=[list(vp[i])for i in edge.vertices],samples=samples,materials=[sl.material.name if sl.material else None for sl in ob.material_slots]))
 ob.to_mesh_clear()
report=dict(source='188',roi=roi,ray_summary=dict(collections.Counter(r['object']for r in rows)),rays=rows,candidate_objects=bounds,edges=edges)
(O/'upper-ownership.json').write_text(json.dumps(report,indent=2));print('SUMMARY',report['ray_summary'],'EDGES',len(edges),'OBJECTS',list(set(e['object']for e in edges)),flush=True)
