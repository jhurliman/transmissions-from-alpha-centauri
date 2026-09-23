"""One connected, finite ledge-fed aging field in original masonry coordinates."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def apply(C,strength=1.0):
 cfg=json.loads((R/'config/coliseum-weathering-148.json').read_text());A=Vector(cfg['anchor']);X=Vector(cfg['across']);Y=Vector(cfg['up']);N=X.cross(Y).normalized();cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH' or 'ink' in ob.name.lower():continue
  attr=ob.data.attributes.get('115 Original world position')
  if not attr:continue
  uv=[((a.vector-A).dot(X),(a.vector-A).dot(Y)) for a in attr.data]
  if not uv or max(v[0] for v in uv)<-8 or min(v[0] for v in uv)>3 or max(v[1] for v in uv)<-6.7 or min(v[1] for v in uv)>5.8:continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('148 connected age'):continue
   if not any(n.label=='Warm exposed stone, violet recesses' for n in old.node_tree.nodes):continue
   em=next((n for n in old.node_tree.nodes if n.type=='EMISSION'),None)
   if not em or not em.inputs[0].is_linked:continue
   if old not in cache:
    m=old.copy();m.name='148 Connected ledge age '+old.name;m['148 connected age']=True;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
    def node(t,label=''):q=n.new(t);q.label=label;return q
    def mathn(op,*args):
     q=node('ShaderNodeMath');q.operation=op
     for i,v in enumerate(args):
      if isinstance(v,(int,float)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs[0]
    def vec(op,a,b):
     q=node('ShaderNodeVectorMath');q.operation=op
     for i,v in enumerate([a,b]):
      if isinstance(v,(tuple,list,Vector)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs['Value'] if op=='DOT_PRODUCT' else q.outputs['Vector']
    def smooth(v,a,b):
     q=node('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(v,q.inputs['Value']);q.inputs['From Min'].default_value=a;q.inputs['From Max'].default_value=b;return q.outputs[0]
    def noise(v,scale):
     q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=2.;q.inputs['Roughness'].default_value=.67;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
    def mul(a,b):return mathn('MULTIPLY',a,b)
    def sub(a,b):return mathn('SUBTRACT',a,b)
    def add(a,b):return mathn('ADD',a,b)
    def mix(f,col,tint,label):
     q=node('ShaderNodeMixRGB',label);q.blend_type='MULTIPLY';l.new(f,q.inputs[0]);l.new(col,q.inputs[1]);q.inputs[2].default_value=tint;return q.outputs[0]
    at=node('ShaderNodeAttribute','148 Fixed native masonry space');at.attribute_name='115 Original world position';pos=at.outputs['Vector'];rel=vec('SUBTRACT',pos,A);u=vec('DOT_PRODUCT',rel,X);v=vec('DOT_PRODUCT',rel,Y)
    coarse=noise(pos,1.35);fine=noise(pos,6.8);warp=add(mul(sub(coarse,.5),.38),mul(sub(fine,.5),.12))
    def polygon(points):
     # Convex, counter-clockwise authored envelope; fine noise only breaks its finite edge.
     area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
     if area<0:points=list(reversed(points))
     distances=[]
     for a,b in zip(points,points[1:]+points[:1]):
      dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
      distances.append(mathn('DIVIDE',sub(mul(sub(u,a[0]),dy),mul(sub(v,a[1]),dx)),length))
     d=distances[0]
     for q in distances[1:]:d=mathn('MAXIMUM',d,q)
     return sub(1,smooth(add(d,warp),-.12,.16))
    def union(polys):
     q=polygon(polys[0])
     for p in polys[1:]:q=mathn('MAXIMUM',q,polygon(p))
     return q
    depth=mathn('ABSOLUTE',vec('DOT_PRODUCT',rel,N));gate=sub(1,smooth(depth,1.25,2.2))
    deposit=mul(union(cfg['deposit_polygons']),gate)
    # Broken intermediate areas within the common envelope; most of the facade stays untouched.
    deposit=mul(deposit,add(.53,mul(smooth(coarse,.31,.67),.47)))
    em=next(q for q in n if q.type=='EMISSION');base=em.inputs[0].links[0].from_socket
    bw=node('ShaderNodeRGBToBW');l.new(base,bw.inputs[0]);quiet_dark=smooth(bw.outputs[0],.027,.11)
    col=mix(mul(mul(deposit,quiet_dark),.84*strength),base,(.55,.56,.64,1),'148 Connected sheltered oxide and dust')
    exposed=mul(union(cfg['exposed_polygons']),gate);exposed=mul(exposed,add(.46,mul(smooth(fine,.3,.68),.54)))
    col=mix(mul(exposed,.62*strength),col,(1.24,1.18,1.12,1),'148 Unequal warm exposed midtone')
    l.new(col,em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name})
 return {'materials':len(cache),'assignments':rows,'config':cfg,'geometry_changed':False,'source':'147 actual scene; rejected139V3 excluded'}
