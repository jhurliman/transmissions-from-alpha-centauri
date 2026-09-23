"""Two finite, unequal support/collar age fields in editable masonry space."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def apply(C):
 cfg=json.loads((R/'config/coliseum-support-weathering-150.json').read_text());rows=[];cache={}
 for f in cfg['fields']:
  tower='7' if f['id'].startswith('primary') else '10'
  names=[o.name for o in C.all_objects if o.type=='MESH' and (o.name==f['shaft_object'] or o.name.startswith('COL111 Tower'+tower+' tier2 stepped belt'))]
  for name in names:
   ob=bpy.data.objects[name];collar=name!=f['shaft_object']
   if not ob.data.attributes.get('115 Original world position'):continue
   A=Vector(f['collar_hit']['original_world'] if collar else f['shaft_origin_hit']['original_world']);X=Vector(f['original_world_basis']['across']);Y=Vector(f['original_world_basis']['up']);N=Vector(f['original_world_basis']['outward'])
   for slot in ob.material_slots:
    old=slot.material
    if not old or not old.use_nodes or old.get('150 support age'):continue
    em=next((n for n in old.node_tree.nodes if n.type=='EMISSION' and n.inputs[0].is_linked),None)
    if not em:continue
    key=(old.name,f['id'],collar)
    if key not in cache:
     m=old.copy();m.name='150 '+('Collar ' if collar else 'Shaft ')+f['id']+' '+old.name;m['150 support age']=True;cache[key]=m;n,l=m.node_tree.nodes,m.node_tree.links
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
      q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=2.;q.inputs['Roughness'].default_value=.65;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
     def mul(a,b):return mathn('MULTIPLY',a,b)
     def sub(a,b):return mathn('SUBTRACT',a,b)
     def add(a,b):return mathn('ADD',a,b)
     def mix(fac,col,tint,label):
      q=node('ShaderNodeMixRGB',label);q.blend_type='MULTIPLY';l.new(fac,q.inputs[0]);l.new(col,q.inputs[1]);q.inputs[2].default_value=tint;return q.outputs[0]
     at=node('ShaderNodeAttribute','150 Native original masonry position');at.attribute_name='115 Original world position';pos=at.outputs['Vector'];rel=vec('SUBTRACT',pos,A);u=vec('DOT_PRODUCT',rel,X);v=vec('DOT_PRODUCT',rel,Y)
     coarse=noise(pos,1.6);fine=noise(pos,8.5);warp=add(mul(sub(coarse,.5),.22),mul(sub(fine,.5),.08))
     def polygon(points):
      area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))
      if area<0:points=list(reversed(points))
      distances=[]
      for a,b in zip(points,points[1:]+points[:1]):
       dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
       distances.append(mathn('DIVIDE',sub(mul(sub(u,a[0]),dy),mul(sub(v,a[1]),dx)),length))
      d=distances[0]
      for q in distances[1:]:d=mathn('MAXIMUM',d,q)
      return sub(1,smooth(add(d,warp),-.075,.10))
     def union(polys):
      q=polygon(polys[0])
      for p in polys[1:]:q=mathn('MAXIMUM',q,polygon(p))
      return q
     if collar:
      w=f['collar_width']/2
      deposit=union([[[-w,1.4],[w*.77,1.3],[w,-.05],[w*.52,-.9],[-w*.7,-1.1],[-w*.9,.1]],[[-w*.15,1.5],[w*1.22,1.2],[w*.85,.28],[-w*.10,.40]]])
      exposed=polygon([[-w*1.30,1.1],[-w*.90,1.25],[-w*.42,-.65],[-w*.93,-.80]])
      amount=f['collar_strength']
     else:
      # Recessed niche floors are ~0.17 units behind the actual front face.
      depth=vec('DOT_PRODUCT',rel,N);gate=mul(smooth(depth,-.105,-.055),sub(1,smooth(depth,.07,.13)))
      deposit=mul(union(f['deposit_polygons']),gate);exposed=mul(union(f['exposed_polygons']),gate);amount=f['strength']
     if not collar and f.get('tail_fade'):
      deposit=mul(deposit,add(.40,mul(smooth(v,-8.3,-2.1),.60)))
     # Broad connected history, varied internally; noise only modulates, never generates blobs.
     deposit=mul(deposit,add(.52,mul(smooth(coarse,.25,.72),.48)))
     em=next(q for q in n if q.type=='EMISSION' and q.inputs[0].is_linked);base=em.inputs[0].links[0].from_socket
     bw=node('ShaderNodeRGBToBW');l.new(base,bw.inputs[0]);quiet_dark=smooth(bw.outputs[0],.035,.12)
     col=mix(mul(mul(deposit,quiet_dark),amount),base,f['deposit_tint'],'150 Muted sheltered mineral deposit')
     exposed=mul(exposed,add(.55,mul(smooth(fine,.30,.70),.45)))
     col=mix(mul(mul(exposed,quiet_dark),.48 if not collar else .32),col,(1.22,1.14,1.09,1),'150 Unequal warm exposed midtone')
     l.new(col,em.inputs[0])
    slot.link='OBJECT';slot.material=cache[key];rows.append({'object':ob.name,'material':cache[key].name,'field':f['id'],'collar':collar})
 return {'source':cfg['source'],'assignments':rows,'private_materials':len(cache),'geometry_changed':False,'config':cfg}
