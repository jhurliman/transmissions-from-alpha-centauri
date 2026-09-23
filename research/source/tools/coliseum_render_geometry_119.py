import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-119'
bpy.ops.wm.open_mainfile(filepath=str(O/'geometry-proof.blend'));s=bpy.context.scene;s.render.filepath=str(O/'sample-painted.png');bpy.ops.render.render(write_still=True)
m=bpy.data.materials.new('117 Neutral clay');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.45,.45,.45,1);p.inputs['Roughness'].default_value=.7
for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
 if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(m)
s.render.filepath=str(O/'sample-clay.png');bpy.ops.render.render(write_still=True)
