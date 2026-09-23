"""Attached finite weathering at one existing broken cornice; editable native nodes."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
def apply(C,strength=1.0):
 cfg=json.loads((R/'config/coliseum-weathering-139.json').read_text());anchor=Vector(cfg['anchor_original_world']);right=Vector(cfg['right_original_world']);up=Vector(cfg['up_original_world']);cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  eligible=any((' U%d '%i)in ob.name for i in [7,8,9])
  if not eligible or 'ink' in ob.name.lower():continue
  if not ob.data.attributes.get('115 Original world position'):continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('139 broken cornice'):continue
   if not any(n.label=='Warm exposed stone, violet recesses' for n in old.node_tree.nodes):continue
   em=next((n for n in old.node_tree.nodes if n.type=='EMISSION'),None)
   if not em or not em.inputs[0].is_linked:continue
   if old not in cache:
    m=old.copy();m.name='139 Broken cornice wear '+old.name;m['139 broken cornice']=True;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
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
    at=node('ShaderNodeAttribute','139 Attached original masonry space');at.attribute_name='115 Original world position';pos=at.outputs['Vector'];rel=vec('SUBTRACT',pos,anchor);u=vec('DOT_PRODUCT',rel,right);down=mul(vec('DOT_PRODUCT',rel,up),-1)
    edge=noise(pos,3.2,2);broad=noise(pos,1.05,2)
    em=next(q for q in n if q.type=='EMISSION');base_color=em.inputs[0].links[0].from_socket;color=base_color
    plane_normal=right.cross(up).normalized()
    for field in cfg['fields']:
     offset=vec('SUBTRACT',pos,Vector(field['center_original_world']));fu=vec('DOT_PRODUCT',offset,right);fv=vec('DOT_PRODUCT',offset,up);depth=mathn('ABSOLUTE',vec('DOT_PRODUCT',offset,plane_normal))
     du=mathn('DIVIDE',mathn('ABSOLUTE',fu),field['half_width']);dv=mathn('DIVIDE',mathn('ABSOLUTE',fv),field['half_height'])
     irregular=mathn('ADD',mathn('MAXIMUM',du,dv),mul(sub(broad,.5),.55));gate=sub(1,smooth(depth,.42,.72))
     outer=mul(sub(1,smooth(irregular,.66,1.02)),gate)
     # Sheltered/lost-coating fringe remains finite; interior pigment is derived from original lit base.
     inner=mul(sub(1,smooth(mathn('ADD',irregular,mul(sub(edge,.5),.24)),.42,.77)),gate)
     deposit=mul(sub(outer,mul(inner,.82)),.72*strength)
     color=mix(deposit,color,(.43,.37,.51,1),'139 Finite lost-coating edge')
     mineral=mix(mathn('ADD',1,0),base_color,tuple(field['pigment_multiplier']),'139 Original-lit pale coating remnant')
     blend=node('ShaderNodeMixRGB','139 Readable flat masonry pigment field');l.new(mul(inner,.92*strength),blend.inputs[0]);l.new(color,blend.inputs[1]);l.new(mineral,blend.inputs[2]);color=blend.outputs[0]
    l.new(color,em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name})
 return {'source':'scene-details-138','strength':strength,'materials':len(cache),'assignments':rows,'config':cfg,'geometry_changed':False,'black_ink_unchanged':True}
