"""Locked-camera clay diagnostic for continuous arcade geometry."""
import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-129';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];members=set(C.all_objects)
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT'] and o not in members:o.hide_render=True
m=bpy.data.materials.new('129 neutral diagnostic clay');m.use_nodes=True;n=m.node_tree.nodes;bs=n.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.35,.35,.35,1);bs.inputs['Roughness'].default_value=.9
for ob in members:
 if ob.type=='MESH':
  for slot in ob.material_slots:slot.link='OBJECT';slot.material=m
s.world=bpy.data.worlds.new('129 neutral diagnostic world');s.world.use_nodes=True;s.world.node_tree.nodes.get('Background').inputs[0].default_value=(.18,.18,.18,1)
s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.31;s.render.border_max_x=.73;s.render.border_min_y=.51;s.render.border_max_y=.90;s.render.filepath=str(O/'clay.png');bpy.ops.render.render(write_still=True)
