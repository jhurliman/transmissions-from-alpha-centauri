import bpy
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-085';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;m=bpy.data.materials['085 soil pigment with shallow granular relief']
for n in m.node_tree.nodes:
 if n.type=='MAP_RANGE' and abs(n.inputs['From Min'].default_value-.2)<.001 and abs(n.inputs['From Max'].default_value-.95)<.001:
  n.inputs['From Min'].default_value=.47;n.inputs['From Max'].default_value=.91;n.inputs['To Min'].default_value=.45;n.inputs['To Max'].default_value=1.55
 if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-5.7)<.01:n.inputs['Detail'].default_value=.7;n.inputs['Roughness'].default_value=.45
 if n.type=='BUMP':n.inputs['Distance'].default_value=.12
 if n.type=='MIX_RGB' and n.blend_type=='MULTIPLY' and abs(n.inputs[0].default_value-.45)<.001:n.inputs[0].default_value=.52
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
