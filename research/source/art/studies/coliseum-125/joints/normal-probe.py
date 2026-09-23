import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-125/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82
for ob in s.objects:
 if ob.type=='GREASEPENCIL':ob.hide_render=True

cache={}
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if ob.type!='MESH' or 'loadbearing arch tunnel' not in ob.name:continue
 for i,old in enumerate(ob.data.materials):
  if old not in cache:
   m=old.copy();cache[old]=m;nt=m.node_tree
   for n in list(nt.nodes):
    if n.type=='NEW_GEOMETRY':
     for socketname in ['Normal','True Normal']:
      for link in list(n.outputs[socketname].links):
       dest=link.to_socket;nt.links.remove(link);dest.default_value=(0,-1,.04)
  ob.data.materials[i]=cache[old]
s.render.filepath=str(O/'constant-spandrel-normal-noink.png');bpy.ops.render.render(write_still=True)
