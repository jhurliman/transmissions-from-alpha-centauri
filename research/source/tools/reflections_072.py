import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-072'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;changes=json.loads((O/'changes.json').read_text());m=bpy.data.materials['Infill | smoked blue opaque study']
# Planar captures include opposite architecture outside the main camera frame.
from mathutils import Vector
planes={}
for ins in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=ins.object
 if ob.type!='MESH' or ob.hide_render or not any(slot.material and slot.material.name==m.name for slot in ob.material_slots):continue
 center=ins.matrix_world @ Vector(tuple(sum(v[i] for v in ob.bound_box)/8 for i in range(3)))
 if abs(center.x)<4 or abs(center.x)>15 or center.y>40:continue
 key=round(center.x,1);planes.setdefault(key,[]).append(center)
for x,pts in sorted(planes.items(),key=lambda kv:len(kv[1]),reverse=True)[:8]:
 n=Vector((-1 if x>0 else 1,0,0));p=bpy.data.lightprobes.new('072 window plane '+str(x),'PLANE');p.influence_distance=.6;p.clip_start=.02
 ob=bpy.data.objects.new(p.name,p);s.collection.objects.link(ob);ob.location=(x+n.x*.025,sum(v.y for v in pts)/len(pts),sum(v.z for v in pts)/len(pts));ob.rotation_euler=n.to_track_quat('Z','Y').to_euler();ob.scale=(20,18,1)
changes['planar_reflection_groups']={str(k):len(v) for k,v in planes.items()}
(O/'changes.json').write_text(json.dumps(changes,indent=2));s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.62;s.render.border_max_x=1;s.render.border_min_y=.22;s.render.border_max_y=.95;s.render.filepath=str(O/'right.png');bpy.ops.render.render(write_still=True)
