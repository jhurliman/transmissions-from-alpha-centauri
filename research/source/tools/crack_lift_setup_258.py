import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/crack-lift-258'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/soil-panel-257/scene.blend'));s=bpy.context.scene
ob=bpy.data.objects['Recessed base wall.034'];mod=ob.modifiers['069 localized fracture'];c=mod.object.copy();c.data=mod.object.data.copy();c.name='258 Raised panel fracture cutter';s.collection.objects.link(c);mod.object=c;c.location.z+=.75
c.hide_render=True;c.hide_set(True)
gp=s.objects['096 damage ink'];gp.data=gp.data.copy();drawing=gp.data.layers[0].frames[0].drawing
for index,n in [(360,107),(361,27)]:
 st=drawing.strokes[index];assert len(st.points)==n
 for p in st.points:
  assert 1.9<p.position.z<2.3
  p.position.z+=.75
drawing.tag_positions_changed()
(O/'audit.json').write_text(json.dumps({'object':ob.name,'cutter':c.name,'vertical_shift_metres':.75,'damage_ink_strokes':[360,361],'spalling_unchanged':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.use_freestyle=False;s.render.use_compositing=False
for vl in s.view_layers:vl.use=vl.name=='ViewLayer'
s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=50/3840;s.render.border_max_x=330/3840;s.render.border_min_y=1-1660/2885;s.render.border_max_y=1-1120/2885
s.eevee.taa_render_samples=32;s.eevee.shadow_pool_size='1024'
