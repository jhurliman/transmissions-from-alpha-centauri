"""Run only after parent releases render slot. Native matched camera proofs."""
import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=Path(__file__).parent
for stage,path in [('before',R/'art/studies/coliseum-156/scene.blend'),('after',O/'scene.blend')]:
 if '--after-only'in sys.argv and stage=='before':continue
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);s.render.use_compositing=False;s.render.resolution_percentage=100;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=2080/3840;s.render.border_max_x=2280/3840;s.render.border_min_y=1-715/2885;s.render.border_max_y=1-560/2885;s.render.threads_mode='FIXED';s.render.threads=4
 s.render.use_freestyle=False;s.render.filepath=str(O/(stage+'-painted.png'));bpy.ops.render.render(write_still=True)
 clay=bpy.data.materials.new('157 proof neutral clay');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.35,.35,.35,1);clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
 for ob in C.all_objects:
  if ob.type=='MESH':
   for slot in ob.material_slots:slot.link='OBJECT';slot.material=clay
 s.render.filepath=str(O/(stage+'-clay.png'));bpy.ops.render.render(write_still=True)
