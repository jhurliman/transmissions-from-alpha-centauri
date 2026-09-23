"""Attached mineral weathering; concentration follows authored masonry ledges."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
def apply(C,strength=.85):
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 ob=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=ob.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(ob);inv=P.inverted();cache={};rows=[]
 for ob in C.objects:
  if ob.type!='MESH' or ob.get('coliseum_role')not in ['wall','tower','band']:continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or old.get('role') in ['fracture','recess']or 'Two-depth'in old.name or 'Exposed'in old.name:continue
   if old not in cache:
    m=old.copy();m.name='126 Ledge mineral '+old.name;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
    em=next((x for x in n if x.type=='EMISSION'),None)
    if not em or not em.inputs[0].is_linked:continue
    color=em.inputs[0].links[0].from_socket
    def node(t,label=''):
     q=n.new(t);q.label=label;return q
    def calc(op,*v):
     q=node('ShaderNodeMath');q.operation=op
     for i,x in enumerate(v):
      if isinstance(x,(int,float)):q.inputs[i].default_value=x
      else:l.new(x,q.inputs[i])
     return q.outputs[0]
    def vec(op,a,b):
     q=node('ShaderNodeVectorMath');q.operation=op
     for i,x in enumerate([a,b]):
      if isinstance(x,(tuple,list,Vector)):q.inputs[i].default_value=x
      else:l.new(x,q.inputs[i])
     return q.outputs['Value']if op=='DOT_PRODUCT'else q.outputs[0]
    def smooth(v,lo,hi):
     q=node('ShaderNodeMapRange');q.interpolation_type='SMOOTHERSTEP';q.clamp=True;q.inputs['From Min'].default_value=lo;q.inputs['From Max'].default_value=hi;l.new(v,q.inputs[0]);return q.outputs[0]
    at=node('ShaderNodeAttribute','Stable native paint coordinates');at.attribute_name='115 Original world position';xyz=node('ShaderNodeCombineXYZ')
    for i in range(3):l.new(calc('ADD',vec('DOT_PRODUCT',at.outputs['Vector'],tuple(inv[i][k]for k in range(3))),inv[i][3]),xyz.inputs[i])
    pos=xyz.outputs[0];sep=node('ShaderNodeSeparateXYZ');l.new(pos,sep.inputs[0]);z=sep.outputs['Z']
    def noise(v,scale,detail=2):
     q=node('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.7;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
    near=0
    for height in [21.06,39.39,57.72]:
     d=calc('SUBTRACT',z,height);face=calc('MULTIPLY',smooth(d,-.22,.05),calc('SUBTRACT',1,smooth(d,1.25,1.78)));under=calc('MULTIPLY',smooth(d,-1.6,-.2),calc('SUBTRACT',1,smooth(d,-.1,.2)));near=calc('MAXIMUM',near,calc('MAXIMUM',face,calc('MULTIPLY',under,.45)))
    coarse=smooth(noise(pos,.55,2),.49,.57)
    near=calc('MULTIPLY',near,coarse)
    angle=calc('ARCTAN2',sep.outputs['Y'],sep.outputs['X']);junction=0
    for bay,height,width,reach in [(7,57.72,2.4,4.8),(10,39.39,2.7,4.2),(12,57.72,1.9,3.4)]:
     du=calc('DIVIDE',calc('MULTIPLY',calc('ABSOLUTE',calc('SUBTRACT',angle,-math.pi+bay*math.tau/36)),75),width)
     dz=calc('DIVIDE',calc('SUBTRACT',z,height+.4),reach)
     distance=calc('SQRT',calc('ADD',calc('MULTIPLY',du,du),calc('MULTIPLY',dz,dz)))
     junction=calc('MAXIMUM',junction,calc('SUBTRACT',1,smooth(distance,.25,1.2)))
    near=calc('MAXIMUM',near,calc('MULTIPLY',junction,.82))
    stretched=vec('MULTIPLY',pos,(1.2,1.2,1.4));branch=noise(stretched,2.4,3);edge=noise(pos,5.8,2);grain=noise(pos,13,1)
    mask=calc('MULTIPLY',near,smooth(calc('ADD',branch,calc('MULTIPLY',calc('SUBTRACT',edge,.5),.42)),.46,.515));mask=calc('MULTIPLY',mask,strength)
    mix=node('ShaderNodeMixRGB','126 Broken mineral deposits below actual floor bands');mix.blend_type='MULTIPLY';l.new(mask,mix.inputs[0]);l.new(color,mix.inputs[1]);mix.inputs[2].default_value=(.35,.31,.43,1);color=mix.outputs[0]
    fleck=calc('MULTIPLY',calc('MULTIPLY',near,smooth(grain,.57,.72)),strength*.55)
    q=node('ShaderNodeMixRGB','126 Mineral grit retains masonry light');q.blend_type='MULTIPLY';l.new(fleck,q.inputs[0]);l.new(color,q.inputs[1]);q.inputs[2].default_value=(1.52,1.40,1.25,1);l.new(q.outputs[0],em.inputs[0])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'material':cache[old].name})
 return {'strength':strength,'materials':len(cache),'assignments':len(rows),'coordinates':'Inverse authored transform of115 Original world position','source_ledge_heights':[21.06,39.39,57.72],'scope':'wall tower and band materials only; preserve original light response and all geometry','rows':rows}
