import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-125/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
for ob in s.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True

cache={}
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if ob.type!='MESH' or 'archivolt1 stone' not in ob.name:continue
 for i,old in enumerate(ob.data.materials):
  if old not in cache:
   m=old.copy();cache[old]=m;nt=m.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');original=em.inputs[0].links[0].from_socket;n=nt.nodes.new('ShaderNodeMixRGB');n.blend_type='MULTIPLY';n.inputs[0].default_value=1;n.inputs[2].default_value=(.92,.92,.92,1);nt.links.new(original,n.inputs[1]);nt.links.new(n.outputs[0],em.inputs[0])
  ob.data.materials[i]=cache[old]
s.render.filepath=str(O/'outer-stone-contrast-noink.png');bpy.ops.render.render(write_still=True)
