import bpy,sys,json,time,shutil,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-136/haze'
for name in ['main-4k.png','scene.blend','final-settings.json','preservation.json']:
 if (O/name).exists() and not (O/('D-'+name)).exists():shutil.copy2(O/name,O/('D-'+name))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));s=bpy.context.scene
# Actual primary object geometry, transforms and material identity before/after.
def snapshot():
 rows={}
 for ob in s.objects:
  v={'matrix':[list(x)for x in ob.matrix_world],'materials':[m.material.name if m.material else None for m in ob.material_slots],'hidden':ob.hide_render}
  if ob.type=='MESH':
   a=array.array('f',[0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);v['geometry']=hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
  if ob.type=='CAMERA':v['camera']=[ob.data.lens,ob.data.shift_x,ob.data.shift_y]
  if ob.type=='LIGHT':v['light']=[ob.data.energy,list(ob.data.color)]
  rows[ob.name]=v
 return rows
before=snapshot();from coliseum_haze_136 import apply
a=apply(s,'E');after=snapshot();changed={k:[q for q in v if v[q]!=after[k][q]]for k,v in before.items() if v!=after[k]};assert changed=={'Distant dust volume - real lighting':['materials']},changed
(O/'preservation.json').write_text(json.dumps({'objects':len(before),'changed':changed,'geometry_camera_lights_and_other_material_assignments_unchanged':True},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_compositing=False;s.render.use_freestyle=True;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);a['render_seconds']=time.time()-t;a['root_candidate']='E: rear source cutoff reduces portal illumination';a['user_approved']=False;(O/'final-settings.json').write_text(json.dumps(a,indent=2))
