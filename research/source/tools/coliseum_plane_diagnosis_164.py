"""Separate actual upper-frontage material, explicit ink, and geometry contributions."""
import bpy,sys,json,time,re
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-164/diagnosis';O.mkdir(parents=True,exist_ok=True)
cfg=json.loads((R/'config/coliseum-plane-diagnosis-164.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));s=bpy.context.scene
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
keep=set(C.all_objects);x0,y0,x1,y1=cfg['native_crop']
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
rows=[]
def is_ink(ob):
 return bool(re.search(r'\bink\b',ob.name.lower())) or ob.type in {'GREASEPENCIL','GPENCIL'}
for ob in C.all_objects:
 if ob.type in {'MESH','CURVE','GREASEPENCIL','GPENCIL'}:
  mats=[q.material.name if q.material else None for q in ob.material_slots]
  ink=is_ink(ob)
  rows.append({'object':ob.name,'type':ob.type,'role':ob.get('coliseum_role'),'materials':mats,'explicit_ink':ink})
(O/'inventory.json').write_text(json.dumps(rows,indent=2))
timings={}
def render(label):
 t=time.time();s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True);timings[label]=time.time()-t
render('without-freestyle')
hidden=[]
for ob in C.all_objects:
 if is_ink(ob) and not ob.hide_render:
  ob.hide_render=True;hidden.append(ob.name)
render('without-explicit-ink')
# This lighting is a geometric diagnostic, never a proposed scene light change.
for ob in s.objects:
 if ob not in keep and ob!=s.camera:ob.hide_render=True
world=bpy.data.worlds.new('164 Neutral diagnostic world');world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.35,.35,.35,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35;s.world=world
for label,direction,energy in [('side',(-.85,-1.,.9),2.),('fill',(1.,-.5,.35),.4)]:
 light=bpy.data.lights.new('164 '+label,'SUN');light.energy=energy;light.angle=.12;ob=bpy.data.objects.new(light.name,light);s.collection.objects.link(ob);ob.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
clay=bpy.data.materials.new('164 Neutral diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.8;s.view_layers[0].material_override=clay
render('neutral-side-lit-clay')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'diagnostic-only.blend'))
(O/'audit.json').write_text(json.dumps({'source':cfg['source'],'crop':cfg['native_crop'],'temporarily_hidden_ink':hidden,'render_seconds':timings,'retained_scene_modified':False,'note':'Neutral side light and hidden ink are diagnostic only; no final-art acceptance.'},indent=2))
