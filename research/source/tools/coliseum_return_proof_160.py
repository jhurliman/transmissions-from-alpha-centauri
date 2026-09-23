"""Matched native-camera border proofs; isolated source/candidate only."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-160/repair'
for variant,path in [('before',R/'art/studies/coliseum-156/scene.blend'),('after',O/'study.blend')]:
 for mode in ['painted','clay']:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  s.render.use_freestyle=False;s.render.use_compositing=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
  s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=2030/3840;s.render.border_max_x=2170/3840;s.render.border_min_y=1-640/2885;s.render.border_max_y=1-445/2885
  if mode=='clay':
   m=bpy.data.materials.new('160 neutral clay proof');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.35,.35,.35,1);p.inputs['Roughness'].default_value=.8
   C=bpy.data.collections['110 Coliseum detailed front ruin']
   for ob in C.all_objects:
    if ob.type=='MESH':
     for slot in ob.material_slots:slot.link='OBJECT';slot.material=m
    elif ob.type in {'GREASEPENCIL','CURVE'}:ob.hide_render=True
  s.render.image_settings.file_format='PNG';s.render.filepath=str(O/f'{variant}-{mode}.png');bpy.ops.render.render(write_still=True)
