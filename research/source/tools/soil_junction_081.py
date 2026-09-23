import bpy
from pathlib import Path
from mathutils import Vector
import sys
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-081'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=900;s.render.resolution_y=700
sys.path.insert(0,str(R/'tools'));from soil_study_081 import mat,CFG
cfg={**CFG,'grain_mode':'discrete','noise_scale':26,'noise_detail':1.8};g=bpy.data.objects['081 editable soil slab'];g.data.materials[0]=mat(cfg);g.data.materials[1]=mat(cfg,'081 grain fracture',.38)
for m in bpy.data.materials:
 if m.use_nodes and 'lip' in m.name:
  for n in m.node_tree.nodes:
   if n.type=='TEX_NOISE' and abs(n.inputs['Scale'].default_value-2.6)<.01:n.inputs['Scale'].default_value=26
s.camera.location=(3.4,-.5,1.5);s.camera.rotation_euler=(Vector((3,1.2,0))-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.type='ORTHO';s.camera.data.ortho_scale=1.1;s.render.filepath=str(O/'junction.png');bpy.ops.render.render(write_still=True)
m=bpy.data.materials.new('081 clay topology');m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.4,.4,.4,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.7
s.view_layers[0].material_override=m;s.render.filepath=str(O/'junction-clay.png');bpy.ops.render.render(write_still=True)
s.view_layers[0].material_override=None
sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN');sun.rotation_euler=Vector((.4,-1.7,-1.5)).to_track_quat('-Z','Y').to_euler();sun.data.energy=3
s.render.filepath=str(O/'junction-grazing.png');bpy.ops.render.render(write_still=True)
