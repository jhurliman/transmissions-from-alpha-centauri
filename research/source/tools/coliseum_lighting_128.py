"""Native facade-relative illumination; preserve local normals, depth and painted wear."""
import bpy,math,json
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]

def rgba(h):
 s=[int(h[i:i+2],16)/255 for i in(0,2,4)]
 return tuple(v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4 for v in s)+(1,)

def apply(C,variant='A'):
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 ob=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=ob.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(ob);inv=P.inverted()
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);N=(Y@A@P).to_3x3().inverted().transposed()
 cache={};rows=[];diagnostics=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes or not any(q.label=='Warm exposed stone, violet recesses' for q in old.node_tree.nodes):continue
   if old.get('128 lighting variant') == variant:continue
   if old.get('128 lighting variant'):raise ValueError('Change study variants from fresh127 source')
   if old not in cache:
    m=old.copy();m.name='128 Even masonry '+variant+' '+old.name;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
    def node(t,label=''):
     q=n.new(t);q.label=label;return q
    def calc(op,*v):
     q=node('ShaderNodeMath');q.operation=op
     for i,x in enumerate(v):
      if isinstance(x,(int,float)):q.inputs[i].default_value=x
      else:l.new(x,q.inputs[i])
     return q.outputs[0]
    def vec(op,a,b=None):
     q=node('ShaderNodeVectorMath');q.operation=op
     for i,x in enumerate([a,b] if b is not None else [a]):
      if isinstance(x,(tuple,list,Vector)):q.inputs[i].default_value=x
      else:l.new(x,q.inputs[i])
     return q.outputs['Value']if op=='DOT_PRODUCT'else q.outputs[0]
    def combine(values):
     q=node('ShaderNodeCombineXYZ')
     for i,x in enumerate(values):
      if isinstance(x,(int,float)):q.inputs[i].default_value=x
      else:l.new(x,q.inputs[i])
     return q.outputs[0]
    at=node('ShaderNodeAttribute','128 Authored cylindrical surface coordinates');at.attribute_name='115 Original world position'
    pos=combine([calc('ADD',vec('DOT_PRODUCT',at.outputs['Vector'],tuple(inv[i][k]for k in range(3))),inv[i][3])for i in range(3)])
    xyz=node('ShaderNodeSeparateXYZ');l.new(pos,xyz.inputs[0]);theta=calc('ARCTAN2',xyz.outputs['Y'],xyz.outputs['X']);theta=calc('ADD',calc('MULTIPLY',calc('ADD',theta,math.pi/2),.68),-math.pi/2)
    authored=combine([calc('COSINE',theta),calc('SINE',theta),75*.055/78]);macro=vec('NORMALIZE',combine([vec('DOT_PRODUCT',authored,tuple(N[i][k]for k in range(3)))for i in range(3)]))
    g=next(q for q in n if q.type=='NEW_GEOMETRY');orient=next(q for q in n if q.label=='Broad form lighting');lightvec=tuple(orient.inputs[1].default_value)
    correction=calc('SUBTRACT',.72,vec('DOT_PRODUCT',macro,lightvec))
    gate=node('ShaderNodeMapRange','128 Only outward-facing masonry receives broad fill');gate.clamp=True;gate.interpolation_type='SMOOTHSTEP';gate.inputs['From Min'].default_value=.18;gate.inputs['From Max'].default_value=.78;l.new(vec('DOT_PRODUCT',g.outputs['Normal'],macro),gate.inputs['Value'])
    strength=.86 if variant=='A' else .90
    original=orient.outputs['Value'];targets=[x.to_socket for x in list(original.links)];corrected=calc('ADD',original,calc('MULTIPLY',calc('MULTIPLY',correction,gate.outputs[0]),strength))
    for dst in targets:l.new(corrected,dst)
    pal=next(q for q in n if q.label=='Warm exposed stone, violet recesses')
    # Mid/high values sampled against the dusty rose reference. Deep violet is retained.
    colors=(['514353','705563','88685f','a07c6b','b9927d','c8a38b'] if variant=='A' else ['514353','705363','88645f','a17668','b98b77','c89d87'])
    gain=.69
    for e,h in zip(sorted(pal.color_ramp.elements,key=lambda e:e.position),colors):
     c=rgba(h);e.color=tuple(v*gain for v in c[:3])+(1,)
    m['128 lighting variant']=variant;m['128 broad normal compensation']=strength;m['128 palette gain']=gain
    diagnostics.append({'source':old.name,'new':m.name,'role':old.get('role'),'macro_compensation':strength,'palette_gain':gain,'palette':colors,'local_specular_preserved':True,'ambient_occlusion_preserved':True,'arch_depth_split_preserved':True})
   slot.link='OBJECT';slot.material=cache[old];rows.append(ob.name)
 return {'variant':variant,'materials':diagnostics,'object_slot_assignments':len(rows),'geometry_changed':False,'scene_lights_changed':False,'world_changed':False,'method':'Analytic cylindrical macro-normal compensation gated to outward faces; actual geometry normals retained for local detail. Native shader only.'}
