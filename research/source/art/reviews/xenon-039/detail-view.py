import bpy
from mathutils import Vector
R='/PATH/TO/transmissions-from-alpha-centauri'
bpy.ops.wm.open_mainfile(filepath=R+'/art/reviews/xenon-039/scene.blend');s=bpy.context.scene;s.camera.location=(0,-7.5,5.5);s.camera.rotation_euler=(Vector((-8,-3.8,4.2))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=40;s.render.resolution_x=1100;s.render.resolution_y=1000;s.cycles.samples=48;s.render.filepath=R+'/art/reviews/xenon-039/coating-detail.png';bpy.ops.render.render(write_still=True)
