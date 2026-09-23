import bpy
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-085';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;m=bpy.data.materials['085 soil pigment with shallow granular relief']
for n in m.node_tree.nodes:
 if n.type=='BUMP':n.inputs['Distance'].default_value=.12
 if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and abs(n.inputs[0].default_value-.45)<.001:n.inputs[0].default_value=.78
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=240/1440;s.render.border_max_x=650/1440;s.render.border_min_y=1-875/1082;s.render.border_max_y=1-650/1082;s.render.use_freestyle=False;s.render.filepath=str(O/'coherent-relief-probe.png');bpy.ops.render.render(write_still=True)
