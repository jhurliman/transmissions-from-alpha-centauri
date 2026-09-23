import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-111';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-110/scene.blend'));s=bpy.context.scene
m=bpy.data.materials.new('Diagnostic black surface');m.use_nodes=True;n=m.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
for o in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if o.type=='MESH':o.data.materials.clear();o.data.materials.append(m)
s.render.use_freestyle=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=480/1440;s.render.border_max_x=960/1440;s.render.border_min_y=1-440/1082;s.render.border_max_y=1-110/1082;s.render.filepath=str(O/'black-floor-diagnostic.png');bpy.ops.render.render(write_still=True)
