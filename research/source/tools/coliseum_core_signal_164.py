"""Render ungraded existing diffuse/ramp signals on151/154 core receivers only."""
import bpy,json,time
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-164/diagnosis'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));s=bpy.context.scene
names=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L','COL110 U9 fractured upper wall L','COL110 U9 aperture head','COL110 U9 fractured upper wall R']
copies={};rows=[]
for name in names:
 ob=s.objects[name]
 for index,slot in enumerate(ob.material_slots):
  old=slot.material
  if not old or not old.name.startswith('151 Warm violet exposed masonry core'):continue
  if old not in copies:
   m=old.copy();m.name='164 Diagnostic core signals';n,l=m.node_tree.nodes,m.node_tree.links
   ramp=next(q for q in n if q.label=='Continuous muted fracture stone family')
   bw=n['RGB to BW'];assert bw.inputs[0].links[0].from_node.bl_idname=='ShaderNodeShaderToRGB'
   q=n.new('ShaderNodeCombineXYZ');q.label='R actual diffuse, G existing ramp input, B core mask';q.inputs[2].default_value=1
   l.new(bw.outputs[0],q.inputs[0]);l.new(ramp.inputs[0].links[0].from_socket,q.inputs[1])
   em=next(q for q in n if q.type=='EMISSION');l.new(q.outputs[0],em.inputs[0]);copies[old]=m
  slot.link='OBJECT';slot.material=copies[old];rows.append({'object':name,'slot':index,'source':old.name})
assert len(rows)>=5,rows
box=(1400,350,2470,840);x0,y0,x1,y1=box;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'core-signals.exr');bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(O/'core-signals.exr'),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1];np.save(O/'core-signals.npy',a)
out={'assignments':rows,'channels':'Linear EXR: R actual existing diffuse luminance; G existing weighted ramp input; B1 eligible core. Antialias boundary pixels excluded below.','native_crop':box,'statistics':{}}
for name,b in [('whole',box),('left',(1450,455,1625,605)),('center',(1930,435,2085,605))]:
 d=a[b[1]-y0:b[3]-y0,b[0]-x0:b[2]-x0];mask=d[:,:,2]>.999;v=d[mask];out['statistics'][name]={'samples':int(len(v)),'diffuse_quantiles':np.quantile(v[:,0],[0,.1,.25,.5,.75,.9,1]).tolist(),'ramp_input_quantiles':np.quantile(v[:,1],[0,.1,.25,.5,.75,.9,1]).tolist(),'clamped_low_fraction':float((v[:,1]<=0).mean())}
(O/'core-signal-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
