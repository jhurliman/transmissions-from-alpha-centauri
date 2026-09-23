import bpy,os
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-124/arch-ratio';key=os.environ.get('ARCH_KEY','10')
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));matrix=bpy.context.scene.camera.matrix_world.copy();matrix.translation.z-=15
bpy.ops.wm.open_mainfile(filepath=str(O/key/'geometry.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.use_border=False;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100;s.camera.matrix_world=matrix;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=27;s.use_nodes=False
for ob in s.objects:
 if ob.type not in ['CAMERA','LIGHT']:ob.hide_render=not(ob.get('bay')in [7,8,9]and ob.name.startswith('COL'))
s.render.filepath=str(O/key/'painted.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('124 Arch ratio clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.4,.4,.4,1);bs.inputs['Roughness'].default_value=.8
for ob in s.objects:
 if ob.type=='MESH'and not ob.hide_render:ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(mat)
s.render.filepath=str(O/key/'clay.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/key/'proof.blend'))
