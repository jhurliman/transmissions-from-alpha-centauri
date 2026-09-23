import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-127/fracture-solid'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));cam=bpy.context.scene.camera;matrix=cam.matrix_world.copy();scale=cam.data.ortho_scale
for label,file in [('original',str(R/'art/studies/coliseum-125/scene.blend')),('before','baseline.blend'),('after','geometry.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(O/file));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=False;s.render.resolution_percentage=100
 # Actual unchanged main camera at4K; narrow crop, not a zoomed substitute.
 s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1780/3840;s.render.border_max_x=2060/3840;s.render.border_min_y=1-670/2885;s.render.border_max_y=1-370/2885;s.render.filepath=str(O/(label+'-main4k.png'));bpy.ops.render.render(write_still=True)
 # Matched close proof showing actual editable geometry; source material and neutral clay.
 s.render.use_border=False;s.render.resolution_x=1600;s.render.resolution_y=1600;s.camera.matrix_world=matrix;s.camera.data.type='ORTHO';s.camera.data.ortho_scale=scale
 for ob in s.objects:
  if ob.type not in ['CAMERA','LIGHT']:ob.hide_render=ob.get('bay')!=8
 s.use_nodes=False;s.render.filepath=str(O/(label+'-painted.png'));bpy.ops.render.render(write_still=True)
 mat=bpy.data.materials.new('123 chips neutral');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.85
 for ob in s.objects:
  if ob.type=='MESH'and not ob.hide_render:ob.data.materials.clear();ob.data.materials.append(mat)
 s.world=bpy.data.worlds.new('123 Neutral');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.2,.2,.23,1);s.world.node_tree.nodes.get('Background').inputs[1].default_value=.65
 s.render.filepath=str(O/(label+'-clay.png'));bpy.ops.render.render(write_still=True)
 if label=='after':bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'))
