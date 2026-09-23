import bpy,sys
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-123/repair';sys.path.insert(0,str(R/'tools'));from coliseum_crown_repair_123 import NAMES,apply_prepared
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'));s=bpy.context.scene;s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4;s.use_nodes=False
mat=bpy.data.materials.new('123 matched baseline clay');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.85
for o in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(mat)
s.render.filepath=str(O/'before-clay.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.use_nodes=False;s.render.film_transparent=True;s.render.image_settings.color_mode='RGBA'
mat=bpy.data.materials.new('123 silhouette mask');mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(1,1,1,1);out=n.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs[0])
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT']:o.hide_render=o.name not in NAMES
 if o.name in NAMES:o.data.materials.clear();o.data.materials.append(mat)
for label in ['before','after']:
 if label=='after':apply_prepared(bpy.data.collections['110 Coliseum detailed front ruin'])
 s.render.filepath=str(O/(label+'-main4k-mask.png'));bpy.ops.render.render(write_still=True)
