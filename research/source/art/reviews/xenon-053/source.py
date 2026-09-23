import bpy,json,sys
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-053'
k=sys.argv[sys.argv.index('--')+1]
settings={'A':(1.00,1.12,1.25,.52,1.4,1.5),'B':(1.00,1.28,1.50,.70,1.6,1.8),'C':(.99,1.19,1.35,.60,2.15,2.4)}
sat,contrast,line,crease,runoff,width=settings[k]
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-052/scene.blend'));s=bpy.context.scene
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree
 if not any(n.type=='GROUP' and n.node_tree.name.startswith('051 ') for n in nt.nodes):continue
 em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked),None)
 if not em:continue
 source=em.inputs['Color'].links[0].from_socket
 hs=nt.nodes.new('ShaderNodeHueSaturation');hs.label='053 modest material saturation';hs.inputs['Saturation'].default_value=sat;nt.links.new(source,hs.inputs['Color'])
 mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='SCALE';mul.inputs['Scale'].default_value=contrast;nt.links.new(hs.outputs[0],mul.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';add.inputs[1].default_value=tuple(.065*(1-contrast) for _ in range(3));nt.links.new(mul.outputs[0],add.inputs[0]);nt.links.new(add.outputs[0],em.inputs['Color'])
 for n in list(nt.nodes):
  if n.type=='GROUP' and n.node_tree.name=='048 Chromatic seam-fed runoff':
   strength=n.inputs['Strength']
   if strength.is_linked:
    old=strength.links[0].from_socket;v=nt.nodes.new('ShaderNodeMath');v.operation='MULTIPLY';v.inputs[1].default_value=runoff;nt.links.new(old,v.inputs[0]);cap=nt.nodes.new('ShaderNodeMath');cap.operation='MINIMUM';cap.inputs[1].default_value=1;nt.links.new(v.outputs[0],cap.inputs[0]);nt.links.new(cap.outputs[0],strength)
   else:strength.default_value=min(1,strength.default_value*runoff)
# C adds a bounded runoff specimen at existing foreground window-head elevations.
if k=='C':
 m=bpy.data.materials.get('042 Street coating | right_front')
 if m:
  nt=m.node_tree;wear=next(n for n in nt.nodes if n.type=='GROUP' and n.node_tree.name.startswith('051 '));base=wear.inputs['Base'].links[0].from_socket
  geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0])
  def op(kind,a,b):
   n=nt.nodes.new('ShaderNodeMath');n.operation=kind
   for i,v in enumerate([a,b]):
    if isinstance(v,(int,float)):n.inputs[i].default_value=v
    else:nt.links.new(v,n.inputs[i])
   return n.outputs[0]
  norm=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Normal'],norm.inputs[0]);face=op('GREATER_THAN',op('ABSOLUTE',norm.outputs['X'],0),.72)
  for start,height,stretch in [(0.2,12.11,1.7),(-3.0,5.87,1.1)]:
   co=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(op('SUBTRACT',11.6,op('SUBTRACT',sep.outputs['Y'],start)),co.inputs['Y']);nt.links.new(op('ADD',op('DIVIDE',op('SUBTRACT',sep.outputs['Z'],height),stretch),2.639),co.inputs['Z'])
   node=nt.nodes.new('ShaderNodeGroup');node.node_tree=bpy.data.node_groups['048 Chromatic seam-fed runoff'];node.label='053 foreground window-head runoff';nt.links.new(co.outputs[0],node.inputs['Position']);nt.links.new(base,node.inputs['Base']);nt.links.new(op('MULTIPLY',face,.90),node.inputs['Strength']);base=node.outputs[0]
  nt.links.new(base,wear.inputs['Base'])
g=bpy.data.node_groups.get('048 Chromatic seam-fed runoff');count=0
if g:
 for n in g.nodes:
  if n.type=='MATH' and n.operation=='MULTIPLY' and not n.inputs[0].is_linked and n.inputs[1].is_linked and .004<=n.inputs[0].default_value<=.0151:
   n.inputs[0].default_value*=width;count+=1
for ls in s.view_layers[0].freestyle_settings.linesets:
 st=ls.linestyle
 if 'Fine structural' in ls.name:st.thickness=crease;st.alpha=.67 if k=='A' else .80;st.color=(.010,.007,.014)
 else:st.thickness=line;st.alpha=.96;st.color=(.004,.0025,.006)
s.render.filepath=str(O/(k+'.png'));bpy.ops.wm.save_as_mainfile(filepath=str(O/(k+'.blend')))
(O/(k+'-settings.json')).write_text(json.dumps({'saturation':sat,'linear_contrast':contrast,'contrast_pivot':.065,'contour_width':line,'crease_width':crease,'runoff_strength_multiplier':runoff,'runoff_width_multiplier':width,'finite_runoff_paths_widened':count,'geometry_changed':False},indent=2));bpy.ops.render.render(write_still=True)
