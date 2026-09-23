import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/edge-diagnosis';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);s.render.use_compositing=False;s.render.use_freestyle=False;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=3;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1725/3840;s.render.border_max_x=2330/3840;s.render.border_min_y=1-960/2885;s.render.border_max_y=1-560/2885
gp=bpy.data.objects.get('110 Landmark contact ink');gp.hide_render=True
s.render.filepath=str(O/'no-contact-only.png');bpy.ops.render.render(write_still=True)
mat=bpy.data.materials.new('153 diagnostic clay');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.35,.35,.35,1)
for ob in C.all_objects:
 if ob.type=='MESH':
  for sl in ob.material_slots:sl.link='OBJECT';sl.material=mat
s.render.filepath=str(O/'clay-no-contact.png');bpy.ops.render.render(write_still=True)
