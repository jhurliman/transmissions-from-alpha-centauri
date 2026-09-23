"""Export an editable intact architectural bay/tower library from the integrated candidate."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-114';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
keep={o for o in C.objects if o.type=='MESH' and o.get('bay')==4}
bpy.data.batch_remove(ids=[o for o in list(s.objects) if o not in keep and o.type not in ['CAMERA','LIGHT']])
C.name='Coliseum reusable bay and tower'
bounds=[o.matrix_world@Vector(v) for o in keep for v in o.bound_box];lo=Vector(tuple(min(v[k] for v in bounds) for k in range(3)));hi=Vector(tuple(max(v[k] for v in bounds) for k in range(3)));target=(lo+hi)/2
cam=s.camera;cam.location=target+Vector((-70,-80,15));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=(hi.z-lo.z)*1.15
s.world=bpy.data.worlds.new('Kit neutral background');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.19,.19,.19,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.4
s.render.resolution_x=1200;s.render.resolution_y=1600;s.render.line_thickness=1;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'kit.png')
roles={}
for o in keep:roles.setdefault(o.get('coliseum_role'),[]).append(o.name)
(O/'kit-inventory.json').write_text(json.dumps({'collection':C.name,'source_bay':4,'objects':len(keep),'roles':roles,'dimensions_m':list(hi-lo),'interfaces':{'authored_radius':75,'wall_thickness':8,'floor_pitch':18.33,'bay_angle_degrees':10,'uniform_scene_scale':.715},'reuse':'Append named collection or linked mesh datablocks into another Blender scene. Source transforms and attached materials retained.','separate_damage_sources':['tools/coliseum_damage_detail_110.py','tools/coliseum_breakage_110.py','tools/coliseum_fracture_112.py','tools/coliseum_collapse_113.py']},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'kit.blend'));bpy.ops.render.render(write_still=True)
