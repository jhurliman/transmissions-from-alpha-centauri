"""Separate current native ink, AO and painted deposits; never edit retained168."""
import bpy,sys,json,time,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-171/diagnosis';O.mkdir(parents=True,exist_ok=True)
cfg=json.loads((R/'config/coliseum-hierarchy-diagnosis-171.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));s=bpy.context.scene
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
x0,y0,x1,y1=cfg['native_crop'];s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100
s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
hidden=[]
for ob in list(C.all_objects)+[bpy.data.objects['110 Landmark contact ink']]:
 if (bool(re.search(r'\bink\b',ob.name.lower())) or ob.type in {'GREASEPENCIL','GPENCIL'}) and not ob.hide_render:
  ob.hide_render=True;hidden.append(ob.name)
mats={sl.material for ob in C.all_objects for sl in ob.material_slots if sl.material and sl.material.use_nodes}
timings={};edits=[]
def render(name):
 t=time.time();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);timings[name]=time.time()-t
render('without-explicit-ink')
# Independent AO bypass: preserve all surface-color and lighting nodes.
saved=[]
for m in mats:
 n,l=m.node_tree.nodes,m.node_tree.links
 for q in list(n):
  if q.type!='AMBIENT_OCCLUSION':continue
  val=n.new('ShaderNodeValue');val.outputs[0].default_value=1.
  for link in list(q.outputs['AO'].links):saved.append((l,link.from_socket,link.to_socket));l.new(val.outputs[0],link.to_socket)
  edits.append({'pass':'without-AO','material':m.name,'node':q.name,'label':q.label})
render('without-AO')
for l,src,dst in saved:l.new(src,dst)
# Bypass specific painted color mixes after their thresholds, leaving AO and
# highlight catches intact. No noise inputs are flattened indiscriminately.
def linear_hex(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in a)
pigments={h:linear_hex(h)for h in ['242039','39323e','201a30','100e23']}
for m in mats:
 n,l=m.node_tree.nodes,m.node_tree.links
 for q in list(n):
  if q.type=='GROUP' and q.label=='152 Connected facade age':
   base=q.inputs['Source color'].links[0].from_socket
   for link in list(q.outputs['Color'].links):l.new(base,link.to_socket)
   edits.append({'pass':'without-painted-deposits','material':m.name,'node':q.name,'label':q.label,'action':'bypass current composed age group'})
  if q.type!='MIX_RGB':continue
  dark=next((h for h,c in pigments.items()if not q.inputs[2].is_linked and max(abs(q.inputs[2].default_value[i]-c[i])for i in range(3))<1e-5),None)
  labelled=q.label.startswith(('134 ','135 ','148 '))
  if not dark and not labelled:continue
  for link in list(q.inputs[0].links):l.remove(link)
  q.inputs[0].default_value=0.
  edits.append({'pass':'without-painted-deposits','material':m.name,'node':q.name,'label':q.label,'dark_color_hex':dark,'action':'zero final pigment mix factor'})
render('without-painted-deposits')
(O/'audit.json').write_text(json.dumps({'source':cfg['source'],'crop':cfg['native_crop'],'hidden_explicit_ink':hidden,'edits':edits,'seconds':timings,'retained_scene_changed':False,'geometry_and_lighting_unchanged':True,'limits':'These are diagnostic bypasses. AO and deposits are each removed independently from the same no-explicit-ink baseline. They are not proposed art variants.'},indent=2)+'\n')
