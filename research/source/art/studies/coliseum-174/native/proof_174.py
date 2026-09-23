"""Matched native preservation crop; execute only after render-lane release."""
import bpy,json,time,re
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-174/native';rows=[]
for variant,path in [('before',R/'art/studies/coliseum-168/scene.blend'),('after',O/'candidate.blend')]:
 for mode in ['painted','clay']:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];preserved_ink=[]
  s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1440/3840;s.render.border_max_x=1650/3840;s.render.border_min_y=1-635/2885;s.render.border_max_y=1-440/2885
  if mode=='clay':
   m=bpy.data.materials.new('174 Diagnostic clay');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.8
   for ob in C.all_objects:
    if ob.type!='MESH'or re.search(r'\bink\b',ob.name.lower()):continue
    for slot in ob.material_slots:
     if slot.material and('ink'in slot.material.name.lower()or 'physical rim'in slot.material.name.lower()):preserved_ink.append(slot.material.name);continue
     slot.link='OBJECT';slot.material=m
  gp=bpy.data.objects.get('110 Landmark contact ink')
  if gp is None or gp.hide_render:raise RuntimeError('Expected visible native contact ink')
  s.render.filepath=str(O/f'{variant}-{mode}.png');t=time.time();bpy.ops.render.render(write_still=True);rows.append({'variant':variant,'mode':mode,'source':str(path.relative_to(R)),'seconds':time.time()-t,'contact_ink_visible':True,'preserved_mesh_ink_materials':sorted(set(preserved_ink))})
(O/'proof-audit.json').write_text(json.dumps({'crop':[1440,440,1650,635],'Freestyle':False,'all_native_ink_preserved':True,'lighting_camera_world_haze':'Unchanged actual168 in both modes; clay replaces only non-ink landmark mesh slots','no_canonical_save':True,'rows':rows},indent=2))
