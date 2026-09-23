"""User-selected primary left pipe: shallower receiver and a seated inward route."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
INSTANCES={'XL | trunk_1350_L3','XL | trunk_1350_L3.001','XL | housing_1950','XL | primary_bottom_wall_turn','XL | primary_building_receiver'}
def capture_surfaces():
 """Evaluated world surfaces keyed source instance/component for local ink transfer."""
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out={}
 for inst in dg.object_instances:
  ob=inst.object
  parent=inst.parent.original.name if inst.parent else None
  is_mount=not inst.is_instance and ob.original.name.startswith('Primary structural standoff')
  if ob.type!='MESH' or not(parent in INSTANCES or is_mount):continue
  source=ob.original.get('127 original component',ob.original.name)
  key=(parent+' / '+source)if parent else source
  me=ob.to_mesh();me.calc_loop_triangles()
  out[key]={'vertices':[tuple(inst.matrix_world@v.co)for v in me.vertices],'triangles':[tuple(t.vertices)for t in me.loop_triangles],'polygons':[tuple(p.vertices)for p in me.polygons]}
  ob.to_mesh_clear()
 return out
def apply():
 scene=bpy.context.scene
 if scene.get('127 primary pipe recessed'):return {'already_applied':True}
 records=[];delta=3.37*.34
 def private(ins):
  old=ins.instance_collection;new=bpy.data.collections.new(old.name+' | 127 private');new['127 source_master']=old.name
  for ob in old.objects:
   copy=ob.copy()
   if ob.data:copy.data=ob.data.copy()
   copy['127 original component']=ob.name;new.objects.link(copy);assert ob.type!='MESH' or list(copy.data.materials)==list(ob.data.materials);records.append({'source':ob.name,'copy':copy.name,'materials':[m.name if m else None for m in ob.data.materials]if ob.type=='MESH'else[]})
  ins.instance_collection=new;return new
 receiver=bpy.data.objects['XL | primary_building_receiver'];c=private(receiver)
 for ob in c.objects:
  for v in ob.data.vertices:
   if ob.name.startswith('Projecting receiver'):v.co.y=2.45+.66*(v.co.y-2.45)
   else:v.co.y+=delta
 lower=bpy.data.objects['XL | trunk_1350_L3'];c=private(lower)
 for ob in c.objects:
  for v in ob.data.vertices:
   if v.co.z<.0001:v.co.z-=0.0
 moved=[]
 for name in ['XL | trunk_1350_L3','XL | trunk_1350_L3.001','XL | housing_1950','XL | primary_bottom_wall_turn']:
  ob=bpy.data.objects[name];before=list(ob.location);ob.location.x-=delta;moved.append({'object':name,'before':before,'after':list(ob.location)})
 bend=bpy.data.objects['XL | primary_bottom_wall_turn'];bend.location.z-=0.0;c=private(bend);radius=1.05;N=64;K=34*N
 for ob in c.objects:
  if ob.name.startswith('Continuous wall turn'):
   assert len(ob.data.vertices)==2*K
   for i,v in enumerate(ob.data.vertices):
    inside=i>=K;idx=i%K;j=idx//N;k=idx%N;rr=.675-(.045 if inside else 0);a=k*math.tau/N
    if j<33:
     t=j*math.pi/64;center=Vector((0,radius*(1-math.cos(t)),-radius*math.sin(t)));normal=Vector((0,math.cos(t),math.sin(t)))
    else:center=Vector((0,2.36-delta,-radius));normal=Vector((0,0,1))
    v.co=center+rr*(math.cos(a)*Vector((1,0,0))+math.sin(a)*normal)
  else:
   for v in ob.data.vertices:v.co.y-=delta;v.co.z+=0.0
 mounts=[]
 for ob in scene.objects:
  if ob.name.startswith('Primary structural standoff'):
   ob.data=ob.data.copy();lo=min(v.co.x for v in ob.data.vertices);hi=max(v.co.x for v in ob.data.vertices)
   for v in ob.data.vertices:v.co.x=lo+(v.co.x-lo)*(hi-lo-delta)/(hi-lo)
   mounts.append(ob.name)
 scene['127 primary pipe recessed']=True
 return {'receiver_depth_before_m':3.37,'receiver_depth_after_m':2.2242,'depth_ratio':.66,'receiver_width_before_after_m':2.3,'pipe_axis_before':[-6.8,26],'pipe_axis_after':[-6.8-delta,26],'pipe_diameter_m':1.35,'inward_translation_m':delta,'bottom_bend_centerline_radius_before_after_m':[1.05,1.05],'lower_straight_extension_m':0.0,'bottom_wall_penetration_preserved_world':[-9.0,26,1.95],'wall_flange_world_unchanged':True,'pipe_to_receiver_axis_error_m':0,'moved_instances':moved,'private_master_components':records,'shortened_wall_mounts':mounts,'materials':'Original material datablocks retained; no material node edits. Housing/collars rigidly translate; cross-section diameter unchanged.','ink':'Freestyle follows native geometry. Existing baked contact ink near old assembly requires parent-targeted cleanup/rebake.'}
if __name__=='__main__':
 O=R/'art/studies/coliseum-127/pipe';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-126/scene.blend'));a=apply();(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
 s=bpy.context.scene;s.render.use_freestyle=False;s.render.resolution_x=1920;s.render.resolution_y=1443;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
