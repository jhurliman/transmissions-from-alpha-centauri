"""Four achromatic native signal probes plus affine volume calibration; no art save."""
import bpy,json,time,sys,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-182/diagnosis';cfg=json.loads((R/'config/coliseum-right-core-signal-182.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];old=bpy.data.materials[cfg['source_material']];m=old.copy();m.name='182 DIAGNOSTIC oldcore scalars';n,l=m.node_tree.nodes,m.node_tree.links;oldsignal=n['Color Ramp'].inputs[0].links[0].from_socket;actual=n['RGB to BW'].outputs[0];em=n.new('ShaderNodeEmission');out=next(q for q in n if q.type=='OUTPUT_MATERIAL' and q.is_active_output);l.new(em.outputs[0],out.inputs['Surface']);assignments=[]
for ob in C.all_objects:
 if ob.type!='MESH':continue
 for i,sl in enumerate(ob.material_slots):
  if sl.material==old:assignments.append({'object':ob.name,'slot':i});sl.link='OBJECT';sl.material=m
x0,y0,x1,y1=cfg['crop'];s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=s.render.use_crop_to_border=True
# Small positive border offset guarantees the intended integer floor despiteRNAfloat rounding.
s.render.border_min_x=(x0+.01)/3840;s.render.border_max_x=(x1+.01)/3840;s.render.border_min_y=(2885-y1+.01)/2885;s.render.border_max_y=(2885-y0+.01)/2885;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';times={}
for mode in cfg['probes']:
 for link in list(em.inputs['Color'].links):l.remove(link)
 if mode=='black0':em.inputs['Color'].default_value=(0,0,0,1)
 elif mode=='white1':em.inputs['Color'].default_value=(1,1,1,1)
 else:l.new(actual if mode=='actual_diffuse' else oldsignal,em.inputs['Color'])
 s.render.filepath=str(O/(mode+'.exr'));t=time.time();bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False);w,h=im.size;assert(w,h)==(x1-x0,y1-y0),(mode,w,h);p=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(p);np.save(O/(mode+'.npy'),p.reshape(h,w,4)[::-1]);times[mode]=time.time()-t;print('182 PROBE',mode,times[mode],flush=True)
# CPU first-hit inventory uses original source material semantic before privatecopy.
for ob in s.objects:
 if ob.hide_render or(ob.type=='MESH' and any(sl.material and sl.material.use_nodes and any(q.type=='OUTPUT_MATERIAL' and q.inputs['Volume'].is_linked for q in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;rows=[];cache={}
for yy in range(y0,y1):
 for xx in range(x0,x1):
  q=iv@Vector((2*(xx+.5)/3840-1,1-2*(yy+.5)/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,no,fi,ob,_=s.ray_cast(dg,origin,di)
  if not ok or ob.type!='MESH':continue
  if ob.name not in cache:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();cache[ob.name]=(ev,me)
  me=cache[ob.name][1];f=me.polygons[fi]
  if f.material_index>=len(ob.material_slots) or ob.material_slots[f.material_index].material!=m:continue
  rows.append({'pixel':[xx,yy],'object':ob.name,'face':fi,'slot':f.material_index,'source_material':old.name,'world':list(p),'normal':list(no),'area_local':f.area})
for ev,me in cache.values():ev.to_mesh_clear()
(O/'first-hit-core.json').write_text(json.dumps(rows,indent=2));(O/'audit.json').write_text(json.dumps({'source':cfg['source'],'crop':cfg['crop'],'assignments':assignments,'render_seconds':times,'first_hit_core_pixels':len(rows),'transport_correction':'Four matched direct achromatic emissions into active Surface; black/white linearEXR endpoints calibrate additive volume radiance and multiplicative spectral transmission perchannel. Geometry/light/volume/nativeink unchanged.','saved_scene':False,'no_art_candidate':True},indent=2));print('182 COMPLETE',len(rows),flush=True)
