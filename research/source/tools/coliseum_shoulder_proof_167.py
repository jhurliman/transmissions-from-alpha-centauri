"""Isolated matched native crop; neutral side lighting is diagnostic only."""
import bpy,json,time,re
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-167/geometry';times={}
for variant,path in [('after',O/'scene.blend')]:
 for mode in ['painted','clay']:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];keep=set(C.all_objects)
  s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1660/3840;s.render.border_max_x=1870/3840;s.render.border_min_y=1-790/2885;s.render.border_max_y=1-515/2885
  for ob in C.all_objects:
   if 'landmark contact ink'in ob.name.lower():ob.hide_render=True
  if mode=='clay':
   for ob in s.objects:
    if ob not in keep and ob!=s.camera:ob.hide_render=True
   for ob in keep:
    if re.search(r'\bink\b',ob.name.lower())or ob.type in {'GREASEPENCIL','GPENCIL'}:ob.hide_render=True
   w=bpy.data.worlds.new('167 Diagnostic neutral world');w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.35,.35,1);w.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;s.world=w
   for label,direction,energy in [('side',(-.85,-1.,.9),2.),('fill',(1.,-.5,.35),.4)]:
    l=bpy.data.lights.new('167 Diagnostic '+label,'SUN');l.energy=energy;l.angle=.12;ob=bpy.data.objects.new(l.name,l);s.collection.objects.link(ob);ob.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
   m=bpy.data.materials.new('167 Diagnostic clay');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.8;s.view_layers[0].material_override=m
  s.render.filepath=str(O/f'{variant}-{mode}.png');t=time.time();bpy.ops.render.render(write_still=True);times[variant+'-'+mode]=time.time()-t
(O/'proof-audit.json').write_text(json.dumps({'source_before':'166','candidate_geometry_source':'163','crop':[1660,515,1870,790],'seconds':times,'freestyle':False,'stale_landmark_contact_ink_hidden_in_both':True,'neutral_side_lighting':'clay only, diagnostic; no saved source changes','candidate_not_integrated':True},indent=2))
