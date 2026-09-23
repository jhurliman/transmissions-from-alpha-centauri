import bpy,sys,json,time
import numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
O=R/'art/studies/lines-095'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-094/scene-C.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
contacts=json.loads((O/'contacts.json').read_text());names={c['name'] for c in contacts};d=bpy.context.evaluated_depsgraph_get();copies=[];occluders=[]
# Capture evaluated instance geometry before changing scene.
for ins in d.object_instances:
 if ins.object.type=='MESH' and ins.object.name in names:
  vs=[ins.matrix_world@Vector(v) for v in ins.object.bound_box]
  if min(v.z for v in vs)>.3:continue
  me=bpy.data.meshes.new_from_object(ins.object,depsgraph=d);me.transform(ins.matrix_world);copies.append((ins.object.name,me))
# Include nearby solids solely for visibility during line extraction.
for ins in d.object_instances:
 if ins.object.type!='MESH' or ins.object.name in names or ins.object.name=='Street foundation':continue
 vs=[ins.matrix_world@Vector(v) for v in ins.object.bound_box];mn=[min(v[k] for v in vs) for k in range(3)];mx=[max(v[k] for v in vs) for k in range(3)]
 near=any(all(mx[k]>a['min'][k]-.5 and mn[k]<a['max'][k]+.5 for k in range(3)) for a in contacts)
 if near:
  me=bpy.data.meshes.new_from_object(ins.object,depsgraph=d);me.transform(ins.matrix_world);occluders.append((ins.object.name,me))
old=[(o,o.lineart.usage) for o in bpy.data.objects if hasattr(o,'lineart')]
for o,_ in old:o.lineart.usage='EXCLUDE'
c=bpy.data.collections.new('095 Exact contact calculation sources');s.collection.children.link(c)
for name,me in copies:
 o=bpy.data.objects.new('095 source '+name,me);c.objects.link(o)
g=s.objects['Street foundation'];me=g.data;v=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3)
me.calc_loop_triangles();f=np.empty(len(me.loop_triangles)*3,dtype=np.int32);me.loop_triangles.foreach_get('vertices',f);f=f.reshape(-1,3);cent=v[f].mean(axis=1);sel=np.zeros(len(f),bool)
for a in contacts:
 mn=a['min'];mx=a['max'];sel|=(cent[:,0]>mn[0]-.35)&(cent[:,0]<mx[0]+.35)&(cent[:,1]>mn[1]-.35)&(cent[:,1]<mx[1]+.35)
f=f[sel];inds,inv=np.unique(f,return_inverse=True);patch=bpy.data.meshes.new('Exact approved terrain contact patches');patch.from_pydata(v[inds].tolist(),[],inv.reshape(-1,3).tolist());patch.transform(g.matrix_world);patch.update();ob=bpy.data.objects.new(patch.name,patch);c.objects.link(ob)
for name,me in occluders:
 ob=bpy.data.objects.new('095 occluder '+name,me);c.objects.link(ob);ob.lineart.usage='OCCLUSION_ONLY'
ink=add_intersection_ink(c,'095 Structural intersection ink',radius=.007);count=bake_intersection_ink(ink)
for frame in ink.data.layers[0].frames:
 for st in frame.drawing.strokes:
  for p in st.points:
   pos=Vector(p.position);a=world_to_camera_view(s,s.camera,pos);b=world_to_camera_view(s,s.camera,pos+s.camera.matrix_world.to_quaternion()@Vector((1,0,0)));ppm=abs(b.x-a.x)*s.render.resolution_x;p.radius=.8/max(ppm,1)
   if not any(all(q['min'][k]-.02<=pos[k]<=q['max'][k]+.02 for k in (0,1)) for q in contacts):p.opacity=0
for ob in list(c.objects):bpy.data.objects.remove(ob,do_unlink=True)
bpy.data.collections.remove(c)
for ob,usage in old:ob.lineart.usage=usage
(O/'audit.json').write_text(json.dumps({'footings':len(copies),'terrain_triangles':len(f),'baked_strokes':count,'screen_radius_pixels':.8,'occluder_meshes':len(occluders),'camera_dependent':True},indent=2));print('BAKED',count,flush=True)
s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_freestyle=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-structural.blend'))
s.render.filepath=str(O/'main-structural.png');bpy.ops.render.render(write_still=True)
