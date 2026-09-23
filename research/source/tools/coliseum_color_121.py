"""User-directed quarter-depth arch light and midpoint cornice tone."""
import math

def _sample(ramp,x):
 es=sorted(ramp.elements,key=lambda e:e.position)
 if x<=es[0].position:return tuple(es[0].color)
 for a,b in zip(es,es[1:]):
  if a.position<=x<=b.position:
   t=(x-a.position)/(b.position-a.position)
   if ramp.interpolation=='EASE':t=t*t*(3-2*t)
   return tuple(a.color[k]*(1-t)+b.color[k]*t for k in range(4))
 return tuple(es[-1].color)

def apply(C):
 materials={m for ob in C.objects if ob.type=='MESH' for m in ob.data.materials if m}
 arch=0
 for m in materials:
  if not m.use_nodes:continue
  for node in m.node_tree.nodes:
   if node.type=='VALTORGB' and node.label=='Front half lighter, rear half darker':
    node.color_ramp.elements[0].position=.235;node.color_ramp.elements[1].position=.265
    node.label='Front quarter lighter, rear three quarters darker';arch+=1
 cache={};blocks=0;tones=[]
 for ob in C.objects:
  if ob.type!='MESH' or ob.get('feature')!='shared undercornice dentil':continue
  for slot in ob.material_slots:
   old=slot.material
   if old in cache:slot.link='OBJECT';slot.material=cache[old];continue
   if not old:continue
   m=old.copy();m.name='121 Midpoint cornice masonry';cache[old]=m;slot.link='OBJECT';slot.material=m
   n,l=m.node_tree.nodes,m.node_tree.links
   pal=next((q for q in n if q.label=='Warm exposed stone, violet recesses'),None)
   if not pal:continue
   outward=_sample(pal.color_ramp,.68);downward=_sample(pal.color_ramp,0.)
   # Midpoint of perceived painted values, returned to linear working space.
   midpoint=tuple(((max(0,outward[k])**(1/2.2)+max(0,downward[k])**(1/2.2))*.5)**2.2 for k in range(3))+(1,)
   tone=n.new('ShaderNodeRGB');tone.label='User midpoint: outward light and downward shade';tone.outputs[0].default_value=midpoint
   for link in list(pal.outputs['Color'].links):l.new(tone.outputs[0],link.to_socket)
   tones.append({'material':m.name,'outward_linear':outward,'underside_linear':downward,'midpoint_linear':midpoint})
  blocks+=1
 return {'arch_materials':arch,'light_fraction':.25,'transition':[.235,.265],'cornice_blocks':blocks,'midpoint_tones':tones,'geometry_unchanged':True,'method':'Midpoint of outward-facing and downward-facing palette samples in perceived values; retained existing attached wear and contact shading'}
