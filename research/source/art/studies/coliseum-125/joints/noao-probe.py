import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-125/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
for ob in s.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True

mats=set(m for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects if ob.type=='MESH' for m in ob.data.materials if m)
for m in mats:
 nt=m.node_tree
 for n in list(nt.nodes):
  if n.type=='AMBIENT_OCCLUSION':
   for socket in n.outputs:
    for link in list(socket.links):
     dest=link.to_socket;nt.links.remove(link)
     try:dest.default_value=1.0
     except:dest.default_value=(1,1,1,1)
s.render.filepath=str(O/'ao-bypassed-noink.png');bpy.ops.render.render(write_still=True)
