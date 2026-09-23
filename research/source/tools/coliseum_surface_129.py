"""Native exposed mineral matrix and finite damage/ledge-fed stains. No image projection."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]

def apply(C,strength=.85,core=True,deposits=True):
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 ob=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=ob.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(ob);iv=P.inverted();cache={};rows=[]
 # Bay-angle positions connect true damage, one projecting tower corner and ledges.
 sites=[{'name':'B7 connected arch shoulder','a':-math.pi+7.5*math.tau/36-2.46/75,'z':59.35,'length':10.0,'width':.85},
        {'name':'Broken central crown facing','a':-math.pi+8.5*math.tau/36-.8/75,'z':72.0,'length':12.5,'width':1.0},
        {'name':'Tower10 exposed shoulder','a':-math.pi+10*math.tau/36+2.0/75,'z':75.3,'length':16.8,'width':.95},
        {'name':'Tower7 lower collar corner','a':-math.pi+7*math.tau/36+2.9/75,'z':40.6,'length':6.8,'width':.7}]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('129 surface'):continue
   is_core=old.get('role')=='fracture' or 'Exposed masonry core'in old.name or 'Exposed warm masonry core'in old.name
   is_wall=any(q.label=='Warm exposed stone, violet recesses'for q in old.node_tree.nodes)
   if not((is_core and core)or(is_wall and deposits)):continue
   if old not in cache:
    m=old.copy();m.name='129 Attached mineral '+old.name;cache[old]=m;m['129 surface']=True;n,l=m.node_tree.nodes,m.node_tree.links
    def node(t,label=''):
     q=n.new(t);q.label=label;return q
    def calc(op,*args):
     q=node('ShaderNodeMath');q.operation=op
     for i,v in enumerate(args):
      if isinstance(v,(int,float)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs[0]
    def vec(op,a,b=None):
     q=node('ShaderNodeVectorMath');q.operation=op
     for i,v in enumerate([a,b]if b is not None else[a]):
      if isinstance(v,(tuple,list,Vector)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs['Value']if op in['DOT_PRODUCT','LENGTH']else q.outputs[0]
    def smooth(v,lo,hi):
     q=node('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHERSTEP';q.inputs['From Min'].default_value=lo;q.inputs['From Max'].default_value=hi;l.new(v,q.inputs['Value']);return q.outputs[0]
    def noise(p,sc,detail=2):
     q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=sc;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.7;l.new(p,q.inputs['Vector']);return q.outputs['Fac']
    def mix(f,a,b,mode='MULTIPLY',label=''):
     q=node('ShaderNodeMixRGB',label);q.blend_type=mode
     for i,v in enumerate([f,a,b]):
      if isinstance(v,(int,float,list,tuple)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs[0]
    at=node('ShaderNodeAttribute','129 Original geometry-attached mineral position');at.attribute_name='115 Original world position';comb=node('ShaderNodeCombineXYZ')
    for i in range(3):l.new(calc('ADD',vec('DOT_PRODUCT',at.outputs['Vector'],tuple(iv[i][k]for k in range(3))),iv[i][3]),comb.inputs[i])
    pos=comb.outputs[0];xyz=node('ShaderNodeSeparateXYZ');l.new(pos,xyz.inputs[0]);z=xyz.outputs['Z'];ang=calc('ARCTAN2',xyz.outputs['Y'],xyz.outputs['X'])
    em=next((q for q in n if q.type=='EMISSION'),None)
    if not em or not em.inputs[0].is_linked:continue
    color=em.inputs[0].links[0].from_socket
    if is_core:
     # The old core retained an ochre family from117. Bring only that legacy
     # family into128's dusty-red direction, preserving its normal-light ramp.
     from coliseum_materials_115 import rgba
     for ramp in [q for q in n if q.label=='Continuous muted fracture stone family']:
      for e,h in zip(sorted(ramp.color_ramp.elements,key=lambda e:e.position),['65505b','806066','987570','b29583']):
       col=rgba(h);e.color=tuple(v*.61 for v in col[:3])+(1,)
     # Exposed mortar/mineral matrix: irregular connected islands, sparse grit and
     # modest local pitting. Texture only occupies existing tagged fracture faces.
     broad=noise(pos,.68,2);edge=noise(pos,2.1,2);fine=noise(pos,5.5,1)
     islands=smooth(calc('ADD',broad,calc('MULTIPLY',calc('SUBTRACT',edge,.5),.22)),.46,.63)
     color=mix(calc('MULTIPLY',islands,.60*strength),color,(.57,.54,.65,1),label='129 Connected exposed mineral matrix')
     light=calc('MULTIPLY',calc('SUBTRACT',1,smooth(edge,.27,.40)),.6*strength);color=mix(light,color,(1.42,1.28,1.18,1),label='129 Broken chalky mineral grains')
     pits=calc('MULTIPLY',smooth(fine,.62,.76),.55*strength);color=mix(pits,color,(.38,.36,.46,1),label='129 Fine fracture pores at native pixel scale')
     # A small true normal perturbation only on exposed aggregate materials.
     bump=node('ShaderNodeBump','129 Shallow exposed mineral pitting');bump.inputs['Strength'].default_value=.14*strength;bump.inputs['Distance'].default_value=.035;l.new(edge,bump.inputs['Height'])
     geo=next((q for q in n if q.type=='NEW_GEOMETRY'),None)
     if geo:
      for link in list(geo.outputs['Normal'].links):l.new(bump.outputs['Normal'],link.to_socket)
     for dif in [q for q in n if q.type=='BSDF_DIFFUSE'and not q.inputs['Normal'].is_linked]:l.new(bump.outputs['Normal'],dif.inputs['Normal'])
    elif deposits:
     mask=0;source=0;branch=noise(vec('MULTIPLY',pos,(1.45,1.45,.26)),1.9,2);edge=noise(pos,3.8,2)
     for s in sites:
      down=calc('SUBTRACT',s['z'],z);t=calc('DIVIDE',down,s['length']);du=calc('MULTIPLY',calc('SUBTRACT',ang,s['a']),75)
      # Bounded lateral drift and broken edges; water courses stay connected to source.
      drift=calc('MULTIPLY',calc('SUBTRACT',noise(vec('MULTIPLY',pos,(.30,.30,.25)),1.2,1),.5),.4)
      distance=calc('DIVIDE',calc('ABSOLUTE',calc('ADD',du,drift)),calc('MULTIPLY',s['width'],calc('ADD',.60,calc('MULTIPLY',smooth(t,0,.55),.50))))
      ragged=calc('ADD',distance,calc('MULTIPLY',calc('SUBTRACT',edge,.5),.65));spread=calc('SUBTRACT',1,smooth(ragged,.20,1.25));fall=calc('MULTIPLY',smooth(down,-.15,.3),calc('SUBTRACT',1,smooth(t,.22,1)))
      breakup=calc('ADD',.27,calc('MULTIPLY',smooth(branch,.34,.61),.73));trail=calc('MULTIPLY',calc('MULTIPLY',spread,fall),breakup);mask=calc('MAXIMUM',mask,trail)
      dz=calc('DIVIDE',down,1.45);uu=calc('DIVIDE',du,s['width']*1.3);distance2=calc('SQRT',calc('ADD',calc('MULTIPLY',dz,dz),calc('MULTIPLY',uu,uu)));source=calc('MAXIMUM',source,calc('MULTIPLY',calc('SUBTRACT',1,smooth(calc('ADD',distance2,calc('MULTIPLY',calc('SUBTRACT',edge,.5),.4)),.35,1.25)),smooth(branch,.34,.58)))
     d=node('ShaderNodeAttribute','129 Keep deep arch returns quiet');d.attribute_name='120 Actual arch tunnel depth';gate=calc('SUBTRACT',1,smooth(d.outputs['Fac'],.12,.35));mask=calc('MULTIPLY',calc('MAXIMUM',calc('MULTIPLY',mask,.63),calc('MULTIPLY',source,.44)),calc('MULTIPLY',strength,gate))
     color=mix(mask,color,(.38,.34,.46,1),label='129 Finite ledge and damage-fed runoff')
     flecks=calc('MULTIPLY',calc('MULTIPLY',source,smooth(edge,.58,.72)),.20*strength);color=mix(flecks,color,(1.25,1.12,1.06,1),label='129 Mineral deposit interruptions around sources')
    l.new(color,em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name,'exposed_core':is_core})
 return {'strength':strength,'materials':len(cache),'assignments':rows,'sources':sites,'geometry_changed':False,'coordinates':'Inverse authored115 original position; all masks attached to native masonry','scope':'Exposed-core material family and four finite architectural runoff regions;128 lighting preserved'}
