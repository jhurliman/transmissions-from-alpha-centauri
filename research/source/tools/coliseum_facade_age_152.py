"""Composed, finite facade age with exhaustive native receiving-face masks."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def shader_group(cfg):
 nt=bpy.data.node_groups.new('152 Composed facade age','ShaderNodeTree');n,l=nt.nodes,nt.links
 for name,typ in [('Source color','NodeSocketColor'),('Original position','NodeSocketVector'),('primary mask','NodeSocketFloat'),('secondary mask','NodeSocketFloat'),('Strength','NodeSocketFloat')]:
  q=nt.interface.new_socket(name=name,in_out='INPUT',socket_type=typ)
  if name=='Strength':q.default_value=1.
 nt.interface.new_socket(name='Color',in_out='OUTPUT',socket_type='NodeSocketColor')
 def node(typ,label=''):
  q=n.new(typ);q.label=label;i=len(n)-1;q.location=((i%12)*210,-(i//12)*180);return q
 def mathn(op,*args):
  q=node('ShaderNodeMath');q.operation=op
  for i,v in enumerate(args):
   if isinstance(v,(float,int)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def add(a,b):return mathn('ADD',a,b)
 def sub(a,b):return mathn('SUBTRACT',a,b)
 def mul(a,b):return mathn('MULTIPLY',a,b)
 def vec(op,a,b):
  q=node('ShaderNodeVectorMath');q.operation=op
  for i,v in enumerate([a,b]):
   if isinstance(v,(list,tuple)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs['Value']if op=='DOT_PRODUCT'else q.outputs['Vector']
 def smooth(x,a,b):
  q=node('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(x,q.inputs['Value']);q.inputs['From Min'].default_value=a;q.inputs['From Max'].default_value=b;return q.outputs[0]
 def noise(pos,scale):
  q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=2;q.inputs['Roughness'].default_value=.64;l.new(pos,q.inputs['Vector']);return q.outputs['Fac']
 def mix(f,col,tint,label):
  q=node('ShaderNodeMixRGB',label);q.blend_type='MULTIPLY';l.new(f,q.inputs[0]);l.new(col,q.inputs[1]);q.inputs[2].default_value=tint;return q.outputs[0]
 inp=node('NodeGroupInput');out=node('NodeGroupOutput');pos=inp.outputs['Original position'];col=inp.outputs['Source color'];coarse=noise(pos,1.4);fine=noise(pos,7.5);warp=add(mul(sub(coarse,.5),.32),mul(sub(fine,.5),.11));bw=node('ShaderNodeRGBToBW');l.new(col,bw.inputs[0]);quiet_dark=smooth(bw.outputs[0],.035,.13)
 for name,g in cfg['groups'].items():
  f=g['frame'];rel=vec('SUBTRACT',pos,f['origin_original']);u=vec('DOT_PRODUCT',rel,f['across_original']);v=vec('DOT_PRODUCT',rel,f['up_original'])
  def polygon(points):
   area=sum(a[0]*b[1]-b[0]*a[1]for a,b in zip(points,points[1:]+points[:1]));points=points if area>0 else list(reversed(points));ds=[]
   for a,b in zip(points,points[1:]+points[:1]):
    dx,dy=b[0]-a[0],b[1]-a[1];ds.append(mathn('DIVIDE',sub(mul(sub(u,a[0]),dy),mul(sub(v,a[1]),dx)),math.hypot(dx,dy)))
   d=ds[0]
   for q in ds[1:]:d=mathn('MAXIMUM',d,q)
   return sub(1,smooth(add(d,warp),-.12,.22))
  def union(polys):
   q=polygon(polys[0])
   for p in polys[1:]:q=mathn('MAXIMUM',q,polygon(p))
   return q
  front=inp.outputs[name+' mask'];gate=mul(mul(front,quiet_dark),inp.outputs['Strength']);deposit=union(g['deposit_polygons']);deposit=mul(deposit,add(.56,mul(smooth(coarse,.22,.75),.44)))
  # Broad upper grouping fades through the unequal lower shoulder.
  deposit=mul(deposit,add(.38,mul(smooth(v,-11.,-3.2),.62)))
  col=mix(mul(mul(deposit,gate),g['strength']),col,g['deposit_tint'],'152 '+name+' connected sheltered deposit')
  exposed=mul(union(g['exposed_polygons']),add(.60,mul(smooth(fine,.24,.73),.40)))
  col=mix(mul(mul(exposed,gate),.50 if name=='primary'else .36),col,(1.26,1.17,1.105,1),'152 '+name+' unequal exposed midtone')
 l.new(col,out.inputs['Color']);return nt

def apply(C):
 cfg=json.loads((R/'config/coliseum-facade-age-152.json').read_text());mapping=json.loads((R/'art/studies/coliseum-152/mapping/package-B-map.json').read_text());group=shader_group(cfg);receivers={};masks=[];cache={};rows=[]
 for name,g in mapping['groups'].items():
  for r in g['receiver_allowlist']:
   ob=C.objects[r['object']];assert len(ob.data.polygons)==r['raw_face_count'];indices=r['exhaustive_front_class_face_ids'];assert indices
   if ob.name not in receivers:
    ob.data=ob.data.copy();receivers[ob.name]={'ob':ob,'slots':set()}
   me=ob.data;attrname=cfg['groups'][name]['receiver_attribute'];attr=me.attributes.get(attrname)or me.attributes.new(attrname,'FLOAT','FACE')
   for i in indices:attr.data[i].value=1.;receivers[ob.name]['slots'].add(me.polygons[i].material_index)
   masks.append({'object':ob.name,'attribute':attrname,'faces':len(indices),'source_face_count':len(me.polygons),'raw_indices_validated':True})
 for name,r in receivers.items():
  ob=r['ob']
  for index in r['slots']:
   slot=ob.material_slots[index];old=slot.material
   if not old or not old.use_nodes:raise RuntimeError('Unexpected receiver material '+name)
   if old.name not in cache:
    m=old.copy();m.name='152 Composed facade age '+old.name;m['152 composed age']=True;n,l=m.node_tree.nodes,m.node_tree.links;em=next(q for q in n if q.type=='EMISSION'and q.inputs[0].is_linked);base=em.inputs[0].links[0].from_socket
    q=n.new('ShaderNodeGroup');q.node_tree=group;q.label='152 Connected facade age';q.location=(em.location.x-260,em.location.y);l.new(base,q.inputs['Source color']);q.inputs['Strength'].default_value=1.
    for att,inputname in [('115 Original world position','Original position')]+[(g['receiver_attribute'],name+' mask')for name,g in cfg['groups'].items()]:
     a=n.new('ShaderNodeAttribute');a.attribute_name=att;a.label=att;a.location=(q.location.x-270,q.location.y-160*len([t for t in n if t.type=='ATTRIBUTE']));l.new(a.outputs['Vector'if inputname=='Original position'else'Fac'],q.inputs[inputname])
    l.new(q.outputs['Color'],em.inputs[0]);cache[old.name]=m
   slot.link='OBJECT';slot.material=cache[old.name];rows.append({'object':name,'slot':index,'old_material':old.name,'material':cache[old.name].name})
 return {'assignments':rows,'receiving_masks':masks,'private_materials':len(cache),'receiving_objects':len(receivers),'geometry_and_normals_unchanged':True,'new_face_attributes_only':True,'source':cfg['source'],'shader_group':group.name,'config':cfg}
