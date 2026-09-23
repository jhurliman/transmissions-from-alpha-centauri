import bpy
from mathutils import Vector
R='/PATH/TO/transmissions-from-alpha-centauri'
bpy.ops.wm.open_mainfile(filepath=R+'/art/reviews/xenon-044/scene.blend');s=bpy.context.scene
beam=next(o for o in bpy.data.collections['DAMAGE | concrete_support_01'].objects if o.name.startswith('Solid concrete'))
for c in bpy.data.collections['044 Hidden damage cutters'].objects:
 c.data.materials.clear();c.data.materials.append(beam.data.materials[0]);c.data.materials.append(bpy.data.materials['044 Exposed concrete aggregate'])
 for f in c.data.polygons:f.material_index=1
bpy.ops.wm.save_as_mainfile(filepath=R+'/art/reviews/xenon-044/scene.blend')
s.camera.location=(4,3.2,3.0);s.camera.rotation_euler=(Vector((8.3,7.15,1.25))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=62;s.render.resolution_x=1100;s.render.resolution_y=1000;s.cycles.samples=48;s.render.filepath=R+'/art/reviews/xenon-044/support-detail.png';bpy.ops.render.render(write_still=True)
