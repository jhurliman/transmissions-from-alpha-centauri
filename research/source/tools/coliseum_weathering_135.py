"""Attached finite weathering at one existing broken cornice; editable native nodes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def apply(C,strength=1.0):
 cfg=json.loads((R/'config/coliseum-weathering-135.json').read_text());anchor=Vector(cfg['anchor_original_world']);right=Vector(cfg['right_original_world']);up=Vector(cfg['up_original_world']);names=set(cfg['objects']);cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH' or ob.name not in names:continue
  if not ob.data.attributes.get('115 Original world position'):continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('135 broken cornice'):continue
   if not any(n.label=='Warm exposed stone, violet recesses' for n in old.node_tree.nodes):continue
   em=next((n for n in old.node_tree.nodes if n.type=='EMISSION'),None)
   if not em or not em.inputs[0].is_linked:continue
   if old not in cache:
    m=old.copy();m.name='135 Broken cornice wear '+old.name;m['135 broken cornice']=True;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
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
    def noise(v,scale,detail=2):
     q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.70;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
    def mul(a,b):return mathn('MULTIPLY',a,b)
    def sub(a,b):return mathn('SUBTRACT',a,b)
    def mix(f,col,tint,label):
     q=node('ShaderNodeMixRGB',label);q.blend_type='MULTIPLY';l.new(f,q.inputs[0]);l.new(col,q.inputs[1]);q.inputs[2].default_value=tint;return q.outputs[0]
    at=node('ShaderNodeAttribute','135 Attached original masonry space');at.attribute_name='115 Original world position';pos=at.outputs['Vector'];rel=vec('SUBTRACT',pos,anchor);u=vec('DOT_PRODUCT',rel,right);down=mul(vec('DOT_PRODUCT',rel,up),-1)
    edge=noise(pos,3.5,2);broad=noise(pos,.85,2);fibre=noise(vec('MULTIPLY',pos,(1.8,1.8,.20)),2.1,2)
    # One connected weather front, feathered unevenly at the sides and diminishing below its actual ledge.
    drift=mul(sub(broad,.5),.65);distance=mathn('ABSOLUTE',mathn('ADD',u,drift));width=cfg['width'];length=cfg['length'];lateral=mathn('ADD',mathn('DIVIDE',distance,width),mul(sub(edge,.5),.34));spread=sub(1,smooth(lateral,.35,1.0));fall=mul(smooth(down,-.14,.20),sub(1,smooth(down,length*.45,length)))
    patch=mul(mul(spread,fall),mathn('ADD',.32,mul(smooth(fibre,.35,.66),.68)))
    # Restrict deep tunnel surfaces; current archive's black joint material is excluded by its shader.
    dep=node('ShaderNodeAttribute');dep.attribute_name='120 Actual arch tunnel depth';gate=sub(1,smooth(dep.outputs['Fac'],.06,.25));patch=mul(patch,gate)
    em=next(q for q in n if q.type=='EMISSION');color=em.inputs[0].links[0].from_socket
    color=mix(mul(patch,.58*strength),color,(.52,.49,.57,1),'135 Deposits fed by broken cornice')
    # Fine warm mineral islands around the source; finite and broken, never continuous ledge stripes.
    top=mul(smooth(down,-.28,.02),sub(1,smooth(down,.65,1.6)));mineral=mul(mul(top,spread),smooth(edge,.46,.63));color=mix(mul(mineral,.30*strength),color,(1.40,1.22,1.10,1),'135 Exposed mineral interruptions')
    catches=0
    for level in cfg['lip_levels']:
     band=sub(1,smooth(mathn('ABSOLUTE',sub(down,level)),.025,.11));catches=mathn('MAXIMUM',catches,mul(mul(band,spread),smooth(edge,.40,.63)))
    dif=node('ShaderNodeBsdfDiffuse');dif.inputs['Color'].default_value=(.7,.7,.7,1);rgb=node('ShaderNodeShaderToRGB');l.new(dif.outputs[0],rgb.inputs[0]);bw=node('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);light=smooth(bw.outputs[0],.06,.55)
    color=mix(mul(mul(catches,light),.40*strength),color,(1.65,1.35,1.16,1),'135 Interrupted lit stone lips');l.new(color,em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name})
 return {'source':'134 scene','strength':strength,'materials':len(cache),'assignments':rows,'config':cfg,'geometry_changed':False,'black_ink_unchanged':True}
