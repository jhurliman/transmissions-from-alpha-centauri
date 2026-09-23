import bpy,sys
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-149/geometry'
for label,path in [('before',R/'art/studies/coliseum-148/scene.blend'),('after',O/'scene.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];m=bpy.data.materials.new('148 neutral clay');m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.43,.43,.43,1);b.inputs['Roughness'].default_value=.8
 for ob in C.all_objects:
  if ob.type=='MESH':
   for slot in ob.material_slots:slot.link='OBJECT';slot.material=m
 s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1925/3840;s.render.border_max_x=2080/3840;s.render.border_min_y=1-590/2885;s.render.border_max_y=1-435/2885;s.render.filepath=str(O/(label+'-clay.png'));bpy.ops.render.render(write_still=True)
