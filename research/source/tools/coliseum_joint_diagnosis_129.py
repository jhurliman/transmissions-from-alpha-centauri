"""UCL-01/UCL-02/DP-03 isolated arch joint shading branch diagnosis."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-129/joints';O.mkdir(parents=True,exist_ok=True)
for mode in ['baseline','broad-constant','diffuse-constant','glossy-constant','true-normal']:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];materials={sl.material for ob in C.all_objects if ob.type=='MESH'for sl in ob.material_slots if sl.material};audit=[]
 for m in materials:
  if not m.use_nodes:continue
  ns,ls=m.node_tree.nodes,m.node_tree.links
  for n in list(ns):
   replace=None
   if mode=='broad-constant'and n.label=='Broad form lighting':replace=(n.outputs['Value'],.65)
   if mode in ['diffuse-constant','glossy-constant']and n.type=='SHADERTORGB':
    linked=n.inputs[0].links[0].from_node.type if n.inputs[0].links else ''
    if linked==('BSDF_DIFFUSE'if mode=='diffuse-constant'else'BSDF_GLOSSY'):replace=(n.outputs[0],.4 if mode=='diffuse-constant'else 0.)
   if replace:
    out,val=replace;q=ns.new('ShaderNodeValue');q.outputs[0].default_value=val
    for li in list(out.links):to=li.to_socket;ls.remove(li);ls.new(q.outputs[0],to)
    audit.append(m.name+':'+n.name)
   if mode=='true-normal'and n.type=='NEW_GEOMETRY':
    for li in list(n.outputs['Normal'].links):to=li.to_socket;ls.remove(li);ls.new(n.outputs['True Normal'],to)
    for q in ns:
     if q.type in ['BSDF_DIFFUSE','BSDF_GLOSSY']:ls.new(n.outputs['True Normal'],q.inputs['Normal'])
 s.render.use_freestyle=False
 for ob in s.objects:
  if ob.type=='GREASEPENCIL':ob.hide_render=True
 s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.43;s.render.border_max_x=.53;s.render.border_min_y=.69;s.render.border_max_y=.80;s.render.filepath=str(O/(mode+'.png'));bpy.ops.render.render(write_still=True)
 (O/(mode+'.json')).write_text(json.dumps(audit,indent=2))
