"""Measure current facade diffuse versus palette input, without art edits."""
import bpy,json,time
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-175/diagnosis';cfg=json.loads((R/'config/coliseum-facade-light-signal-175.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];copies={};rows=[]
for ob in C.all_objects:
 if ob.type!='MESH':continue
 at=ob.data.attributes.get('162 primary facade receiver')
 if not at or not any(v.value>.5 for v in at.data):continue
 for i,slot in enumerate(ob.material_slots):
  old=slot.material
  if not old or not old.use_nodes:continue
  pal=next((q for q in old.node_tree.nodes if q.label=='Warm exposed stone, violet recesses'),None)
  if pal is None:continue
  if old not in copies:
   m=old.copy();m.name='175 Facade light signals '+old.name;n,l=m.node_tree.nodes,m.node_tree.links
   pal=next(q for q in n if q.label=='Warm exposed stone, violet recesses')
   def diffuse_source(q):
    if q.bl_idname!='ShaderNodeRGBToBW' or not q.inputs[0].is_linked:return False
    sr=q.inputs[0].links[0].from_node
    return sr.bl_idname=='ShaderNodeShaderToRGB' and sr.inputs[0].is_linked and sr.inputs[0].links[0].from_node.bl_idname=='ShaderNodeBsdfDiffuse'
   bw=next(q for q in n if diffuse_source(q));at=n.new('ShaderNodeAttribute');at.attribute_name='162 primary facade receiver'
   signals=n.new('ShaderNodeCombineXYZ');l.new(bw.outputs[0],signals.inputs[0]);l.new(pal.inputs[0].links[0].from_socket,signals.inputs[1]);l.new(at.outputs['Fac'],signals.inputs[2])
   em=next(q for q in n if q.type=='EMISSION');l.new(signals.outputs[0],em.inputs[0]);copies[old]=m
  slot.link='OBJECT';slot.material=copies[old];rows.append({'object':ob.name,'slot':i,'source':old.name})
box=cfg['crop'];x0,y0,x1,y1=box;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32';s.render.filepath=str(O/'signals.exr');t=time.time();bpy.ops.render.render(write_still=True)
im=bpy.data.images.load(str(O/'signals.exr'),check_existing=False);w,h=im.size;a=np.empty(w*h*4,dtype=np.float32);im.pixels.foreach_get(a);a=a.reshape(h,w,4)[::-1];np.save(O/'signals.npy',a)
v=a[a[:,:,2]>.999];stats={'samples':len(v),'raw_diffuse_quantiles':np.quantile(v[:,0],[0,.1,.25,.5,.75,.9,1]).tolist(),'current_palette_input_quantiles':np.quantile(v[:,1],[0,.1,.25,.5,.75,.9,1]).tolist()}
(O/'audit.json').write_text(json.dumps({'source':cfg['source'],'assignments':rows,'crop':box,'channels':'Linear EXR R actual diffuse, G current weighted palette input, B primary receiver; use B>.999 to exclude antialias/atmosphere-contaminated samples','statistics':stats,'seconds':time.time()-t,'retained_scene_changed':False},indent=2)+'\n');print(stats)
