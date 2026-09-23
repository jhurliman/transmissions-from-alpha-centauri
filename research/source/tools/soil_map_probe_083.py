import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';bpy.ops.wm.open_mainfile(filepath=str(O/'main-scene.blend'));s=bpy.context.scene;g=bpy.data.objects['Street foundation'];m=g.data.materials[0];gain=next(q for q in reversed(list(m.node_tree.nodes)) if q.type=='MATH' and q.operation=='MULTIPLY');gain.operation='MULTIPLY_ADD';gain.inputs[1].default_value=3.2;gain.inputs[2].default_value=-2.34
# Save corrected material before temporarily changing the preview camera and visibility.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'main-scene.blend'))
for ob in s.objects:
 if ob.type=='MESH' and ob!=g:ob.hide_render=True
s.camera.location=(0,-5,4);s.camera.rotation_euler=Vector((0,5,-4)).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=3.625;s.render.resolution_x=1370;s.render.resolution_y=746;s.render.use_freestyle=False;s.render.filepath=str(O/'scene-ground-closeup.png');bpy.ops.render.render(write_still=True)
