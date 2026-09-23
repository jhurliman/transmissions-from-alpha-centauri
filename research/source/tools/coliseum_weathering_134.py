"""Three finite collar-fed native weathering groups, preserving broad133 appearance."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]

def apply(C,strength=1.0):
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 ob=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=ob.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(ob);iv=P.inverted();cache={};rows=[]
 cfg=json.loads((R/'config/coliseum-weathering-134.json').read_text());sites=cfg['sites']
 for ob in C.all_objects:
  if ob.type!='MESH' or ob.library or ob.get('130 barrel tunnel') or 'ink' in ob.name.lower():continue
  if not ('Tower7 ' in ob.name or 'Tower10 ' in ob.name or 'continuous arcade wall' in ob.name):continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('134 collar weathering'):continue
   if not any(q.label=='Warm exposed stone, violet recesses' for q in old.node_tree.nodes):continue
   oldem=next((q for q in old.node_tree.nodes if q.type=='EMISSION'),None)
   if oldem is None or not oldem.inputs[0].is_linked:continue
   if old not in cache:
    m=old.copy();m.name='134 Collar-fed '+old.name;cache[old]=m;m['134 collar weathering']=True;n,l=m.node_tree.nodes,m.node_tree.links
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
    at=node('ShaderNodeAttribute','134 Attached original masonry coordinates');at.attribute_name='115 Original world position';comb=node('ShaderNodeCombineXYZ')
    for i in range(3):l.new(calc('ADD',vec('DOT_PRODUCT',at.outputs['Vector'],tuple(iv[i][k]for k in range(3))),iv[i][3]),comb.inputs[i])
    pos=comb.outputs[0];xyz=node('ShaderNodeSeparateXYZ');l.new(pos,xyz.inputs[0]);z=xyz.outputs['Z'];ang=calc('ARCTAN2',xyz.outputs['Y'],xyz.outputs['X'])
    em=next((q for q in n if q.type=='EMISSION'),None)
    if not em or not em.inputs[0].is_linked:continue
    color=em.inputs[0].links[0].from_socket
    # Real finite source zones: top of selected five-step collars, then gravity-fed falls.
    edge=noise(pos,2.4,2);branch=noise(vec('MULTIPLY',pos,(1.1,1.1,.16)),1.8,2);mask=0;source=0;catch=0
    for site in sites:
     a=-math.pi+site['tower']*math.tau/36+site['u']/75
     du=calc('MULTIPLY',calc('SUBTRACT',ang,a),75);down=calc('SUBTRACT',site['z'],z);t=calc('DIVIDE',down,site['length'])
     drift=calc('MULTIPLY',calc('SUBTRACT',noise(vec('MULTIPLY',pos,(.5,.5,.15)),1.3,1),.5),.5)
     width=calc('MULTIPLY',site['width'],calc('ADD',.6,calc('MULTIPLY',smooth(t,0,.55),.45)))
     lateral=calc('DIVIDE',calc('ABSOLUTE',calc('ADD',du,drift)),width)
     broken=calc('ADD',lateral,calc('MULTIPLY',calc('SUBTRACT',edge,.5),.62))
     spread=calc('SUBTRACT',1,smooth(broken,.45,.80))
     fall=calc('MULTIPLY',smooth(down,-.18,.2),calc('SUBTRACT',1,smooth(t,.60,1.)))
     connected=calc('ADD',.48,calc('MULTIPLY',smooth(branch,.38,.60),.52))
     mask=calc('MAXIMUM',mask,calc('MULTIPLY',calc('MULTIPLY',spread,fall),connected))
     sourcefall=calc('MULTIPLY',smooth(down,-.20,.03),calc('SUBTRACT',1,smooth(down,1.45,2.1)))
     source=calc('MAXIMUM',source,calc('MULTIPLY',spread,sourcefall))
     # Short, interrupted edge catches on actual horizontal step levels, not wall-wide stripes.
     for dz in [.0,.27,.67,1.37]:
      strip=calc('SUBTRACT',1,smooth(calc('ABSOLUTE',calc('SUBTRACT',down,dz)),.04,.16))
      catch=calc('MAXIMUM',catch,calc('MULTIPLY',calc('MULTIPLY',strip,spread),smooth(edge,.45,.62)))
    dep=node('ShaderNodeAttribute');dep.attribute_name='120 Actual arch tunnel depth';gate=calc('SUBTRACT',1,smooth(dep.outputs['Fac'],.08,.25))
    darkmask=calc('MULTIPLY',calc('MULTIPLY',mask,gate),.88*strength)
    color=mix(darkmask,color,(.34,.34,.43,1),label='134 Connected finite water deposits')
    mineral=calc('MULTIPLY',calc('MULTIPLY',source,smooth(edge,.45,.61)),.42*strength)
    color=mix(mineral,color,(1.40,1.23,1.13,1),label='134 Local chalky mineral breaks')
    # Existing actual diffuse response governs warm edge catches; no new illumination.
    dif=node('ShaderNodeBsdfDiffuse');dif.inputs['Color'].default_value=(.7,.7,.7,1);rgb=node('ShaderNodeShaderToRGB');l.new(dif.outputs[0],rgb.inputs[0]);bw=node('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);light=smooth(bw.outputs[0],.06,.55)
    fac=calc('MULTIPLY',calc('MULTIPLY',catch,light),.80*strength)
    color=mix(fac,color,(1.60,1.35,1.16,1),label='134 Selective irregular warm ledge catches')
    l.new(color,em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name})
 return {'strength':strength,'materials':len(cache),'assignments':rows,'sources':sites,'geometry_changed':False,'black_joint_materials_unchanged':True,'scope':'Three attached collar-fed sources; source original coordinate top aligns with actual belt upper face; no full-wall grain or lighting edits'}
