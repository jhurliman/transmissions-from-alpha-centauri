import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-085';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;m=bpy.data.materials['085 granular broken crack lip'];n=m.node_tree.nodes
for x in n:
 if x.type=='TEX_NOISE':x.inputs['Scale'].default_value=7.5
 if x.type=='VALTORGB' and x.color_ramp.interpolation=='CONSTANT':
  es=sorted(x.color_ramp.elements,key=lambda e:e.position)
  for e,p,v in zip(es,[.48,.57,.68],[.28,.62,1.05]):e.position=p;e.color=(v,v,v,1)
s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
