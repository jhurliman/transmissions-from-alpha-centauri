import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-perspective-115/E/scene.blend'));s=bpy.context.scene
m=bpy.data.materials.new('115 Neutral clay proof');m.use_nodes=True;n=m.node_tree.nodes;n.clear();d=n.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(.4,.4,.4,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(d.outputs[0],o.inputs['Surface'])
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].all_objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
s.render.use_freestyle=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.filepath=str(R/'art/studies/coliseum-115/E/clay.png');bpy.ops.render.render(write_still=True)
