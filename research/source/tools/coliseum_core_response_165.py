"""Rebalance only five exposed-core slots using measured existing incident light."""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(scene):
 cfg=json.loads((R/'config/coliseum-core-response-165.json').read_text());copies={};rows=[]
 for name,index in cfg['targets'].items():
  slot=scene.objects[name].material_slots[index];old=slot.material
  assert old and old.name=='151 Warm violet exposed masonry core',(name,index,old.name if old else None)
  if old not in copies:
   m=old.copy();m.name='165 Existing light on exposed masonry core';m['165 actual light response']=True;n,l=m.node_tree.nodes,m.node_tree.links
   ramp=n['Color Ramp'];bw=n['RGB to BW'];source=ramp.inputs[0].links[0].from_socket
   remap=n.new('ShaderNodeMapRange');remap.label='165 Existing diffuse range';remap.clamp=True;remap.interpolation_type='LINEAR'
   for key,value in zip(['From Min','From Max','To Min','To Max'],cfg['diffuse_input_range']+cfg['diffuse_output_range']):remap.inputs[key].default_value=value
   l.new(bw.outputs[0],remap.inputs['Value'])
   def scale(sock,weight,label):
    q=n.new('ShaderNodeMath');q.operation='MULTIPLY';q.label=label;l.new(sock,q.inputs[0]);q.inputs[1].default_value=weight;return q.outputs[0]
   q=n.new('ShaderNodeMath');q.operation='ADD';q.label='165 Preserve local response and reveal real light separation';l.new(scale(source,cfg['existing_input_weight'],'165 Existing response'),q.inputs[0]);l.new(scale(remap.outputs[0],1-cfg['existing_input_weight'],'165 Measured diffuse response'),q.inputs[1]);l.new(q.outputs[0],ramp.inputs[0]);copies[old]=m
  slot.link='OBJECT';slot.material=copies[old];rows.append({'object':name,'slot':index,'old':old.name,'new':copies[old].name})
 return {'assignments':rows,'configuration':cfg,'palette_AO_lights_geometry_unchanged':True,'new_texture':False}
