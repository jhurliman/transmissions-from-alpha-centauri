"""Scoped warm/violet core and fracture-fed mineral deposit on the149 loss."""
import bpy
from mathutils import Vector

def apply(C):
 ob=C.objects['COL110 U9 fractured upper wall L'];tag=ob.data.attributes['149 Exposed crown core'];indices={p.material_index for p in ob.data.polygons if tag.data[p.index].value>.5};rows=[]
 for index in indices:
  old=ob.material_slots[index].material
  assert old and 'Exposed masonry core' in old.name,old.name if old else None
  m=old.copy();m.name='149 Warm violet exposed crown core';m['149 crown core']=True;n=m.node_tree.nodes;l=m.node_tree.links
  ramp=next(q for q in n if q.type=='VALTORGB' and len(q.color_ramp.elements)==4)
  palette=[(.062,.041,.058,1),(.089,.052,.069,1),(.159,.089,.073,1),(.217,.13,.092,1)]
  for e,c in zip(ramp.color_ramp.elements,palette):e.color=c
  def node(t,label=''):q=n.new(t);q.label=label;return q
  def mathn(op,*args):
   q=node('ShaderNodeMath');q.operation=op
   for i,v in enumerate(args):
    if isinstance(v,(int,float)):q.inputs[i].default_value=v
    else:l.new(v,q.inputs[i])
   return q.outputs[0]
  def smooth(v,a,b):
   q=node('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(v,q.inputs['Value']);q.inputs['From Min'].default_value=a;q.inputs['From Max'].default_value=b;return q.outputs[0]
  def mul(a,b):return mathn('MULTIPLY',a,b)
  def sub(a,b):return mathn('SUBTRACT',a,b)
  at=node('ShaderNodeAttribute','149 Attached original stone coordinates');at.attribute_name='115 Original world position'
  xyz=node('ShaderNodeSeparateXYZ');l.new(at.outputs['Vector'],xyz.inputs[0]);x,z=xyz.outputs['X'],xyz.outputs['Z']
  noise=node('ShaderNodeTexNoise','149 Fine broken deposit edge');noise.inputs['Scale'].default_value=5.;noise.inputs['Detail'].default_value=1.5;l.new(at.outputs['Vector'],noise.inputs['Vector']);edge=mul(sub(noise.outputs['Fac'],.5),.14)
  # Two unequal downward lobes, both fed by the genuine open fracture above.
  masks=[]
  for center,width,bottom,top,strength in [(.73,.84,48.15,51.1,.31),(2.88,.57,49.9,51.4,.18)]:
   height=smooth(z,bottom,top);w=mathn('ADD',.15,mul(height,width));distance=mathn('DIVIDE',mathn('ABSOLUTE',sub(x,center)),w)
   masks.append(mul(mul(sub(1,smooth(mathn('ADD',distance,edge),.65,1.05)),height),strength))
  mask=mathn('MAXIMUM',*masks)
  em=next(q for q in n if q.type=='EMISSION');base=em.inputs[0].links[0].from_socket
  q=node('ShaderNodeMixRGB','149 Subtle sheltered mineral at open fracture');q.blend_type='MULTIPLY';l.new(mask,q.inputs[0]);l.new(base,q.inputs[1]);q.inputs[2].default_value=(.59,.61,.70,1);l.new(q.outputs[0],em.inputs[0])
  # Existing old core on all other structures remains untouched.
  ob.material_slots[index].link='OBJECT';ob.material_slots[index].material=m;rows.append({'object':ob.name,'slot':index,'old':old.name,'material':m.name})
 return {'assignments':rows,'geometry_changed':False,'existing_material_graphs_changed':False,'source':'149 validated native core surfaces only','palette_linear':palette}
