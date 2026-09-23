"""Recolor the existing primary age body at its unchanged linear luminance."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(C):
 cfg=json.loads((R/'config/coliseum-primary-chroma-172.json').read_text())
 old=bpy.data.node_groups[cfg['group_name']];g=old.copy();g.name='172 Existing age with sheltered chroma';n,l=g.nodes,g.links
 primary=next(q for q in n if q.label==cfg['primary_mix_label'])
 assert primary.blend_type=='MULTIPLY' and primary.inputs[0].is_linked
 weight=primary.inputs[0].links[0].from_socket
 inp=next(q for q in n if q.type=='GROUP_INPUT');out=next(q for q in n if q.type=='GROUP_OUTPUT');col=out.inputs['Color'].links[0].from_socket
 def node(t,label):q=n.new(t);q.label=label;return q
 weights=cfg['luminance_weights'];h=cfg['target_chroma_srgb'];rgb=[int(h[i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in rgb];y=sum(a*b for a,b in zip(rgb,weights));target=[v/y for v in rgb]
 lum=node('ShaderNodeVectorMath','172 Existing final linear luminance');lum.operation='DOT_PRODUCT';l.new(col,lum.inputs[0]);lum.inputs[1].default_value=weights
 tint=node('ShaderNodeVectorMath','172 Sheltered hue at the same luminance');tint.operation='SCALE';tint.inputs[0].default_value=target;l.new(lum.outputs['Value'],tint.inputs['Scale'])
 protect=node('ShaderNodeMath','172 Preserve all secondary receiver faces');protect.operation='SUBTRACT';protect.inputs[0].default_value=1.;l.new(inp.outputs['secondary mask'],protect.inputs[1])
 gate=node('ShaderNodeMath','172 Reuse existing primary deposit factor');gate.operation='MULTIPLY';l.new(weight,gate.inputs[0]);l.new(protect.outputs[0],gate.inputs[1])
 mix=node('ShaderNodeMixRGB','172 Primary chroma only, no added coverage');mix.blend_type='MIX';l.new(gate.outputs[0],mix.inputs[0]);l.new(col,mix.inputs[1]);l.new(tint.outputs['Vector'],mix.inputs[2]);l.new(mix.outputs['Color'],out.inputs['Color'])
 copies={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  a=ob.data.attributes.get(cfg['primary_attribute'])
  if not a or not any(v.value>.5 for v in a.data):continue
  for i,slot in enumerate(ob.material_slots):
   source=slot.material
   if not source or not source.use_nodes or not any(q.type=='GROUP' and q.node_tree==old for q in source.node_tree.nodes):continue
   if source not in copies:
    m=source.copy();m.name='172 Sheltered facing '+source.name
    for q in m.node_tree.nodes:
     if q.type=='GROUP' and q.node_tree==old:q.node_tree=g
    copies[source]=m
   slot.link='OBJECT';slot.material=copies[source];rows.append({'object':ob.name,'slot':i,'source_material':source.name,'new_material':slot.material.name})
 assert rows
 return {'source':cfg['source'],'assignments':rows,'private_materials':len(copies),'group':g.name,'target_chroma_srgb':h,'normalized_linear_chroma':target,'luminance_weights':weights,'normalized_chroma_luminance':sum(a*b for a,b in zip(target,weights)),'primary_factor_source':weight.node.name+'.'+weight.name,'secondary_receiver_factor':0,'existing_geometry_attributes_normals_ink_lighting_and_masks_preserved':True,'claim_scope':'Primary chroma only; exact linear luminance at group output by construction, final rendered differences measured separately.'}
