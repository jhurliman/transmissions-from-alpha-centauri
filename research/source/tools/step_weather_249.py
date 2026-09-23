"""Native stone stains and connected fine fractures on existing five step courses."""
import bpy
from entrance_weathering_227 import Paint

def apply(scene):
 rows=[]
 for ob in sorted((o for o in scene.objects if o.get('228 stone step')),key=lambda o:o.name):
  k=int(ob['course_from_ground']);slot=ob.material_slots[0];m=slot.material.copy();m.name=f'249 Weathered stone step {k}';slot.link='OBJECT';slot.material=m
  p=Paint(m);op=p.op;em=next(n for n in p.n if n.type=='EMISSION');src=em.inputs['Color'].links[0].from_socket
  geo=p.node('ShaderNodeNewGeometry','249 actual step surface');axes=p.node('ShaderNodeSeparateXYZ','249 world stone axes');p.l.new(geo.outputs['Position'],axes.inputs[0]);x,y,z=axes.outputs
  coarse=p.noise(p.vec(op('MULTIPLY',x,.38),op('MULTIPLY',y,.85),op('ADD',z,k*.23)),1,2.8)
  grain=p.noise(geo.outputs['Position'],13,2)
  islands=p.remap(op('ADD',coarse,op('MULTIPLY',op('SUBTRACT',grain,.5),.16)),.50,.64)
  stain=p.mix(1,src,(.10,.12,.16,1),'249 mineral moisture staining','MULTIPLY')
  body=p.mix(op('MULTIPLY',islands,.96),src,stain,'249 uneven stain islands')
  # Scarce dry mineral flecks, broader enough to survive the accepted haze.
  pale=op('MULTIPLY',p.remap(coarse,.27,.36,1,0),p.remap(grain,.57,.71))
  body=p.mix(op('MULTIPLY',pale,.30),body,p.mix(1,src,(1.28,1.24,1.17,1),'249 dry mineral fleck','MULTIPLY'),'249 pale rough aggregate')
  fissures=0;families=[]
  jitter=op('MULTIPLY',op('SUBTRACT',p.noise(p.vec(0,op('MULTIPLY',y,1.45),op('MULTIPLY',z,.75)),1,2),.5),.30)
  dy=op('SUBTRACT',y,190)
  for center,slope,lo,hi in [(-16.6,-.13,1,2),(-8.2,.19,2,5),(3.7,-.21,1,3),(12.1,.16,3,5)]:
   if not lo<=k<=hi:continue
   mid=op('ADD',center,op('ADD',op('MULTIPLY',dy,slope),jitter));dist=op('ABSOLUTE',op('SUBTRACT',x,mid))
   mask=p.remap(dist,.045,.135,1,0);fissures=op('MAXIMUM',fissures,mask);families.append(center)
   if center in (-8.2,12.1):
    branch=op('ADD',mid,op('ADD',.42,op('MULTIPLY',dy,-.24)))
    bd=op('ABSOLUTE',op('SUBTRACT',x,branch));bmask=op('MULTIPLY',p.remap(bd,.014,.062,1,0),p.remap(op('ABSOLUTE',dy),.3,2.4,1,0));fissures=op('MAXIMUM',fissures,bmask)
  crack=p.mix(1,src,(.06,.075,.11,1),'249 fissure depth tone','MULTIPLY')
  body=p.mix(fissures,body,crack,'249 branching cross-course stone cracks');p.l.new(body,em.inputs['Color'])
  rows.append({'object':ob.name,'course':k,'fracture_origins_x':families,'material':m.name})
 assert len(rows)==5
 return {'steps':rows,'geometry_unchanged':True,'crack_width_m':[.045,.135],'haze_and_all_other_materials_unchanged':True,'method':'Private actual-slot native materials; unequal staining spots, mineral flecks and interrupted shared-coordinate fractures across selected courses.'}
