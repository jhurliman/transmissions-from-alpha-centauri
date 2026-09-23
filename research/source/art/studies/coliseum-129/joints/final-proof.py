import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'));from coliseum_joint_shading_129 import apply
O=R/'art/studies/coliseum-129/joints'
for label in ['current129','corrected129']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-129/scene.blend'));s=bpy.context.scene
 if label=='corrected129':
  a=apply(bpy.data.collections['110 Coliseum detailed front ruin'],strength=1.,actual_diffuse=False,reduce_ao=True);(O/'final-audit.json').write_text(json.dumps(a,indent=2))
 s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.43;s.render.border_max_x=.53;s.render.border_min_y=.69;s.render.border_max_y=.80;s.render.filepath=str(O/(label+'.png'));print('PROOF_INK',s.render.use_freestyle,flush=True);bpy.ops.render.render(write_still=True)
