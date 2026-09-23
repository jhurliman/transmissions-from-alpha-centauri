import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from soil_study_081 import mat,CFG
O=R/'art/studies/soil-081';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1370;s.render.resolution_y=746
for ob in s.objects:
 if ob.type=='MESH':ob.hide_render=True
bpy.ops.mesh.primitive_plane_add(size=40);g=bpy.context.object;s.camera.location=(0,-10,8);s.camera.rotation_euler=(Vector((0,0,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=3.625
for mode,freq,detail in [('soft',2.6,1),('fine',18,2),('discrete',26,1.8)]:
 cfg={**CFG,'grain_mode':mode,'noise_scale':freq,'noise_detail':detail};g.data.materials.clear();g.data.materials.append(mat(cfg));s.render.filepath=str(O/(mode+'-clean.png'));bpy.ops.render.render(write_still=True)
