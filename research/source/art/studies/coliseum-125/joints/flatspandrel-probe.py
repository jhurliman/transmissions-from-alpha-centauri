import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-125/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
for ob in s.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True

m=bpy.data.materials.new('125 diagnostic flat emission');m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(.3,.3,.3,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0])
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if ob.type=='MESH' and 'loadbearing arch tunnel' in ob.name:
  for i in range(len(ob.data.materials)):ob.data.materials[i]=m
s.render.filepath=str(O/'flat-spandrel-noink.png');bpy.ops.render.render(write_still=True)
