import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-116'
for src,name in [('scene.blend','main-clay.png'),('kit.blend','kit-clay.png')]:
 bpy.ops.wm.open_mainfile(filepath=str(O/src));s=bpy.context.scene;m=bpy.data.materials.new('116 Neutral clay proof');m.use_nodes=True;n=m.node_tree.nodes;n.clear();d=n.new('ShaderNodeBsdfDiffuse');d.inputs['Color'].default_value=(.4,.4,.4,1);o=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(d.outputs[0],o.inputs['Surface'])
 for ob in s.objects:
  if ob.type=='MESH' and ob.get('coliseum_role'):
   ob.data.materials.clear();ob.data.materials.append(m)
 s.render.use_freestyle=False;s.render.filepath=str(O/name);bpy.ops.render.render(write_still=True)
