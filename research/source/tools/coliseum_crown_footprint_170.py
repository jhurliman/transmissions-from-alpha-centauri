"""Read-only current crown camera/material/available-mass inventory."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
from collections import Counter
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-170/mapping';from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-168/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH'and(ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;cache={};rows=[];_,_,unpack=mapping()
for y in range(440,636,4):
 for x in range(1440,1651,4):
  q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,hit,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if not ok or not ob.name.startswith(('COL','130','131')):continue
  if ob.name not in cache:
   ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me.calc_loop_triangles();face_ts={}
   for t in me.loop_triangles:face_ts.setdefault(t.polygon_index,[]).append(t)
   cache[ob.name]=(me,face_ts,ob.matrix_world.copy())
  me,ts,M=cache[ob.name];p=me.polygons[fi];at=me.attributes.get('115 Original world position');orig=None
  if at and fi in ts:
   v=M.inverted()@hit;t=min(ts[fi],key=lambda t:(geometry.closest_point_on_tri(v,*[me.vertices[i].co for i in t.vertices])-v).length_squared);orig=list(geometry.barycentric_transform(v,*[me.vertices[i].co for i in t.vertices],*[at.data[i].vector for i in t.vertices]))
  mat=ob.material_slots[p.material_index].material if p.material_index<len(ob.material_slots)else None
  rows.append({'pixel':[x,y],'object':ob.name,'face':fi,'material_slot':p.material_index,'material':mat.name if mat else None,'world':list(hit),'authored':list(unpack(hit)),'original_world':orig,'normal':list(n)})
objects=[]
for name,(me,ts,M)in cache.items():
 if not('upper wall'in name or 'aperture head'in name or 'sill wall'in name or 'Tower'in name):continue
 ob=bpy.data.objects[name];vv=[(M@v.co,list(unpack(M@v.co)))for v in me.vertices];upper=[(p,a)for p,a in vv if a[2]>=67.8]
 def bbox(seq):
  pp=[world_to_camera_view(s,cam,p)for p,a in seq];return [min(p.x for p in pp)*3840,min(1-p.y for p in pp)*2885,max(p.x for p in pp)*3840,max(1-p.y for p in pp)*2885]if pp else None
 hit=[r for r in rows if r['object']==name];objects.append({'object':name,'vertices':len(me.vertices),'faces':len(me.polygons),'whole_camera_bbox':bbox(vv),'above67_8_camera_bbox':bbox(upper),'above67_8_authored_bounds':[[min(a[i]for p,a in upper),max(a[i]for p,a in upper)]for i in range(3)]if upper else None,'visible_sample_count':len(hit),'visible_upper_sample_count':sum(r['authored'][2]>=67.8 for r in hit),'visible_materials':dict(Counter(r['material']for r in hit)),'visible_face_indices':sorted(set(r['face']for r in hit))})
(O/'rays.json').write_text(json.dumps(rows,indent=2));(O/'objects.json').write_text(json.dumps(objects,indent=2));print('rays',len(rows),Counter(r['object']for r in rows),flush=True)
