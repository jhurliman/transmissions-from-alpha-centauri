import bpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';bpy.ops.wm.open_mainfile(filepath=str(O/'main-scene.blend'));s=bpy.context.scene;m=bpy.data.objects['Street foundation'].data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links;gain=next(q for q in reversed(list(n)) if q.type=='MATH' and q.operation=='MULTIPLY');raw=gain.inputs[0].links[0].from_socket;probe=n.new('ShaderNodeMath');probe.operation='MULTIPLY';probe.inputs[1].default_value=.1;l.new(raw,probe.inputs[0]);em=next(q for q in n if q.type=='EMISSION');l.new(probe.outputs[0],em.inputs[0])
s.camera.location=(0,-5,4);s.camera.rotation_euler=Vector((0,5,-4)).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=3.625;s.render.resolution_x=512;s.render.resolution_y=256;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.filepath=str(O/'light-probe.png');bpy.ops.render.render(write_still=True)
