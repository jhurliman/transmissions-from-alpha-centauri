"""Accepted222 geometry; facade-matched receivers and substantial directional metal wear."""
import bpy,math,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]

class Paint:
 def __init__(self,m):self.n=m.node_tree.nodes;self.l=m.node_tree.links
 def node(self,t,label):q=self.n.new(t);q.label='227 '+label;return q
 def put(self,v,s):
  if hasattr(v,'node'):self.l.new(v,s)
  else:s.default_value=v
 def op(self,op,*xs):
  q=self.node('ShaderNodeMath',op);q.operation=op
  for i,x in enumerate(xs):self.put(x,q.inputs[i])
  return q.outputs[0]
 def vec(self,*xs):
  q=self.node('ShaderNodeCombineXYZ','native spatial field')
  for i,x in enumerate(xs):self.put(x,q.inputs[i])
  return q.outputs[0]
 def remap(self,x,a,b,c=0,d=1,label='soft ragged transition'):
  q=self.node('ShaderNodeMapRange',label);q.clamp=True;q.interpolation_type='SMOOTHSTEP'
  for i,v in enumerate((x,a,b,c,d)):self.put(v,q.inputs[i])
  return q.outputs[0]
 def mix(self,f,a,b,label,kind='MIX'):
  q=self.node('ShaderNodeMixRGB',label);q.blend_type=kind
  for i,x in enumerate((f,a,b)):self.put(x,q.inputs[i])
  return q.outputs[0]
 def noise(self,p,scale,detail=2):
  q=self.node('ShaderNodeTexNoise','fine broken pigment');self.put(p,q.inputs['Vector']);q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.72;return q.outputs['Fac']
 def hash(self,a):return self.op('FRACT',self.op('MULTIPLY',self.op('SINE',self.op('ADD',self.op('MULTIPLY',a,12.9898),78.233)),43758.5453))

def metal_finish(base,role):
 m=base.copy();m.name='227 '+role+' worn metal';p=Paint(m);op=p.op;n=p.n;l=p.l
 em=next(q for q in n if q.type=='EMISSION');old=em.inputs['Color'].links[0].from_socket
 light=next((q.outputs[0]for q in n if q.type=='MAP_RANGE' and abs(q.inputs['To Min'].default_value-.46)<.001),None);assert light
 geo=p.node('ShaderNodeNewGeometry','world coordinates; real gravity');sep=p.node('ShaderNodeSeparateXYZ','world axes');l.new(geo.outputs['Position'],sep.inputs[0]);x,y,z=sep.outputs
 tex=p.node('ShaderNodeTexCoord','manufactured member bounds');g=p.node('ShaderNodeSeparateXYZ','edge-local bounds');l.new(tex.outputs['Generated'],g.inputs[0]);gy,gz=g.outputs['Y'],g.outputs['Z']
 edge=op('MINIMUM',op('MINIMUM',gy,op('SUBTRACT',1,gy)),op('MINIMUM',gz,op('SUBTRACT',1,gz)));edge=p.remap(edge,.015,.19,1,0,'real member edge susceptibility')
 bottom=p.remap(z,.18,.80,1,0,'ground moisture and foot oxidation')
 fine=p.noise(geo.outputs['Position'],48,2.7);medium=p.noise(geo.outputs['Position'],9.7,2.2)
 # A torn coating field combines fine thresholded mineral islands with edge
 # roots. Noise only roughens the breakup, never supplies the overall shape.
 broken=p.remap(op('ADD',op('MULTIPLY',medium,.65),op('MULTIPLY',fine,.35)),.49,.61)
 support=op('MAXIMUM',op('MULTIPLY',edge,.88),op('MAXIMUM',op('MULTIPLY',bottom,.86),.32 if role=='garage door'else .16))
 chip=op('MULTIPLY',broken,support)
 # Horizontal gate rails/hinges are corrosion collectors. The mask is a band
 # of unequal oxide roots with a downward tail, not all-over brown paint.
 if role=='iron gate':
  joints=0
  for h in(.22,.70,1.70,2.15):joints=op('MAXIMUM',joints,p.remap(op('ABSOLUTE',op('SUBTRACT',z,h)),.012,.085,1,0))
  chip=op('MAXIMUM',chip,op('MULTIPLY',joints,p.remap(medium,.28,.70,.32,.95)))
 # Three unequal seam-origin rain families, analytically tapered and fading.
 rain=0
 origins=(2.24,1.54,.83)if role=='garage door'else(2.16,1.71,.71)
 for k,start in enumerate(origins):
  coord=op('ADD',y,k*.173);cell=op('FLOOR',op('DIVIDE',coord,.31));ha=p.hash(op('ADD',cell,k*71.19));hb=p.hash(op('ADD',cell,k*71.19+19.2));center=op('MULTIPLY',.31,op('ADD',cell,op('ADD',.18,op('MULTIPLY',ha,.64))))
  down=op('SUBTRACT',start,z);length=op('ADD',.23,op('MULTIPLY',hb,.87));t=op('DIVIDE',down,length)
  width=op('MULTIPLY',op('ADD',.014,op('MULTIPLY',ha,.026)),p.remap(t,0,1,1,.10))
  lateral=op('ABSOLUTE',op('SUBTRACT',coord,center));body=p.remap(op('SUBTRACT',width,lateral),0,.018)
  fade=op('MULTIPLY',p.remap(down,-.005,.025),p.remap(t,.18,1,.9,0));active=p.remap(ha,.26,.38)
  rain=op('MAXIMUM',rain,op('MULTIPLY',body,op('MULTIPLY',fade,active)))
 # Sparse little slanted gashes have independent cell lengths and widths.
 yy=op('MULTIPLY',y,7);zz=op('MULTIPLY',z,8);cy=op('FLOOR',yy);cz=op('FLOOR',zz);h=p.hash(op('ADD',cy,op('MULTIPLY',cz,67.9)));fy=op('SUBTRACT',op('FRACT',yy),.5);fz=op('SUBTRACT',op('FRACT',zz),.5)
 scratch=op('MULTIPLY',p.remap(op('ABSOLUTE',op('SUBTRACT',fz,op('MULTIPLY',fy,.35))),.022,.055,1,0),op('MULTIPLY',p.remap(op('ABSOLUTE',fy),.10,.31,1,0),p.remap(h,.76,.88)))
 # All new tones use the same actual-light bound as accepted222 steel.
 def lit(c):return p.mix(1,(*c,1),light,'accepted bounded native lighting','MULTIPLY')
 body=p.mix(.32,old,lit((.115,.165,.20)if role=='garage door'else(.075,.082,.086)),'aged original coating')
 body=p.mix(op('MULTIPLY',rain,.86),body,lit((.26,.115,.042)),'tapered rusty water wash')
 body=p.mix(op('MULTIPLY',chip,.91),body,lit((.10,.042,.023)),'dark torn oxide roots')
 orange=op('MULTIPLY',chip,p.remap(fine,.49,.70,0,.85));body=p.mix(orange,body,lit((.33,.135,.044)),'broken warm oxide grains')
 pale=op('MULTIPLY',chip,p.remap(medium,.44,.52,1,0));body=p.mix(op('MULTIPLY',pale,.52),body,lit((.34,.34,.30)),'small exposed steel abrasion')
 body=p.mix(op('MULTIPLY',scratch,.80),body,lit((.08,.075,.073)),'short dark gashes');l.new(body,em.inputs['Color'])
 m['227 role']=role;m['227 directional native weathering']=True
 return m

def adapt_receiver_coordinates(material):
 """Recreate normalized DamageLocal without adding attributes to accepted mesh."""
 n=material.node_tree.nodes;l=material.node_tree.links;replaced=[]
 for uv in list(n):
  if uv.type!='UVMAP':continue
  assert uv.uv_map=='DamageLocal',uv.uv_map
  p=Paint(material);tex=p.node('ShaderNodeTexCoord','receiver normalized bounds');axes=p.node('ShaderNodeSeparateXYZ','generated axes');l.new(tex.outputs['Generated'],axes.inputs[0]);geo=p.node('ShaderNodeNewGeometry','native face normal');tr=p.node('ShaderNodeVectorTransform','local face orientation');tr.vector_type='NORMAL';tr.convert_from='WORLD';tr.convert_to='OBJECT';l.new(geo.outputs['Normal'],tr.inputs[0]);ns=p.node('ShaderNodeSeparateXYZ','local face axes');l.new(tr.outputs[0],ns.inputs[0]);selector=p.op('GREATER_THAN',p.op('ABSOLUTE',ns.outputs['X']),p.op('ABSOLUTE',ns.outputs['Y']));horizontal=p.op('ADD',p.op('MULTIPLY',selector,axes.outputs['Y']),p.op('MULTIPLY',p.op('SUBTRACT',1,selector),axes.outputs['X']));coord=p.vec(horizontal,axes.outputs['Z'],0)
  for link in list(uv.outputs[0].links):l.new(coord,link.to_socket)
  replaced.append(uv.uv_map);n.remove(uv)
 material['227 receiver UV adaptation']=json.dumps(replaced)
 return replaced


def apply(scene):
 hosts={'warm':bpy.data.objects['Gallery base panel.011'].material_slots[0].material,'blue':bpy.data.objects['Utility base.022'].material_slots[0].material}
 cache={};rows=[]
 # Only actual editable222 masters; original two host panel copies stay exact.
 targets=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('222 garage ','222 passage '))]
 assert len(targets)==70,len(targets)
 for ob in targets:
  name=ob.name
  if name.startswith('222 passage gate '):role='iron gate'
  elif name.startswith('222 garage ') and any(t in name for t in('closed section','pressed lower bead','flush lift handle','fastener')):role='garage door'
  elif name.startswith('222 garage '):role='blue receiver'
  elif any(t in name for t in('walkway','threshold')):role='warm floor'
  else:role='warm receiver'
  for slot in ob.material_slots:
   old=slot.material;key=(role,old.name)
   if key not in cache:
    if role in('iron gate','garage door'):m=metal_finish(old,role)
    else:
     base=hosts['blue'if role=='blue receiver'else'warm'];m=base.copy();m.name='227 Facade matched '+role+' | '+base.name;m['227 role']=role;adapt_receiver_coordinates(m)
    cache[key]=m
   slot.link='OBJECT';slot.material=cache[key];rows.append({'object':name,'role':role,'source_material':old.name,'material':slot.material.name})
 return {'material_assignments':rows,'new_materials':sorted(m.name for m in set(cache.values())),'receiver_coordinate_adaptations':{m.name:json.loads(m.get('227 receiver UV adaptation','[]')) for m in set(cache.values()) if '227 receiver UV adaptation'in m},'objects':len(targets),'geometry_unchanged':True,'host_material_sources':{k:m.name for k,m in hosts.items()},'references':['RS-01','RS-02','RS-03','UP-03'],'method':'Native world/gravity directional seam and hinge runoff, edge-supported torn pigment chips, small gashes; existing facade receivers copied exactly.'}
