import bpy
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-072';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
m=bpy.data.materials['Infill | smoked blue opaque study'];nt=m.node_tree;nt.nodes.clear();g=nt.nodes.new('ShaderNodeBsdfGlossy');g.inputs['Color'].default_value=(.65,.72,.85,1);g.inputs['Roughness'].default_value=.015;o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(g.outputs[0],o.inputs['Surface'])
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.resolution_x=2880;s.render.resolution_y=2160;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.62;s.render.border_max_x=1;s.render.border_min_y=.22;s.render.border_max_y=.95;s.render.filepath=str(O/'right.png');bpy.ops.render.render(write_still=True)
