import bpy,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from soil_relief_083 import material
O=R/'art/studies/soil-083';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-081/selected-scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
g=bpy.data.objects['Street foundation'];m=g.data.materials[0].copy();m.name='083 illustrated microrelief soil';n=m.node_tree.nodes;l=m.node_tree.links;em=next(x for x in n if x.type=='EMISSION');previous=em.inputs[0].links[0].from_node;mask=previous.inputs[0].links[0].from_socket;lightsoil=previous.inputs[2].links[0].from_socket;relief=material(target=m);mix=n.new('ShaderNodeMixRGB');l.new(mask,mix.inputs[0]);l.new(relief,mix.inputs[1]);l.new(lightsoil,mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0]);g.data.materials[0]=m
bpy.ops.wm.save_as_mainfile(filepath=str(O/'main-scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
