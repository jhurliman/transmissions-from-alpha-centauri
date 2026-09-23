"""Five private material receivers: local pigment quieting, no new light or ink."""
import bpy,json,hashlib
from pathlib import Path
SITES=[
 ('COL110 T2 band08 profile1',[-3.505833,190.692078,40.805504],[1.55,.85,.78],[.251502,-.963506,.091669],'C1'),
 ('COL110 T2 band08 profile0',[-3.094561,191.018677,40.568371],[1.55,.85,.78],[.251515,-.963661,.089986],'C1'),
 ('COL120 bay8 arcade2 dentil05',[-2.978218,191.362854,40.277630],[.55,.55,.65],[.998271,.058745,-.001980],'C1'),
 ('COL110 T2 band10 profile1',[12.516734,192.095062,40.705345],[1.15,1.15,.8],[.703542,-.707095,.071030],'C2'),
 ('COL110 T2 band10 profile0',[14.318850,193.712906,40.615982],[.95,.95,.75],[.490327,-.863329,.119343],'C2')]
def graph_signature(m):
 if not m or not m.use_nodes:return None
 return repr(([(n.name,n.bl_idname,[(p.name,str(p.default_value))for p in n.inputs if hasattr(p,'default_value')])for n in m.node_tree.nodes],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)for l in m.node_tree.links]))
def apply(scene):
 oldgraphs={m:graph_signature(m)for m in bpy.data.materials};rows=[]
 for name,origin,radii,normal,group in SITES:
  ob=scene.objects.get(name)
  if ob is None:raise RuntimeError('Missing exact153 receiver '+name)
  for sl in ob.material_slots:
   old=sl.material
   if not old or not old.use_nodes or not any(n.label=='Warm exposed stone, violet recesses'for n in old.node_tree.nodes):continue
   radii=[v*1.3 for v in radii]
   m=old.copy();m.name='153 Quiet fracture receiver '+name+' '+old.name;m['153 bounded readability']=True;n,l=m.node_tree.nodes,m.node_tree.links
   def node(typ,label):q=n.new(typ);q.label=label;return q
   def calc(op,*args):
    q=node('ShaderNodeMath','153 finite pigment gate');q.operation=op
    for i,v in enumerate(args):
     if isinstance(v,(int,float)):q.inputs[i].default_value=v
     else:l.new(v,q.inputs[i])
    return q.outputs[0]
   def smooth(sock,a,b):
    q=node('ShaderNodeMapRange','153 soft geometric support');q.clamp=True;q.interpolation_type='SMOOTHERSTEP';q.inputs['From Min'].default_value=a;q.inputs['From Max'].default_value=b;l.new(sock,q.inputs['Value']);return q.outputs[0]
   at=node('ShaderNodeAttribute','153 Existing attached material coordinates');at.attribute_name='115 Original world position'
   sub=node('ShaderNodeVectorMath','153 Source-space center');sub.operation='SUBTRACT';l.new(at.outputs['Vector'],sub.inputs[0]);sub.inputs[1].default_value=origin
   div=node('ShaderNodeVectorMath','153 Finite ellipsoid');div.operation='DIVIDE';l.new(sub.outputs[0],div.inputs[0]);div.inputs[1].default_value=radii
   length=node('ShaderNodeVectorMath','153 Finite ellipsoid distance');length.operation='LENGTH';l.new(div.outputs[0],length.inputs[0]);spatial=calc('SUBTRACT',1,smooth(length.outputs['Value'],.55,1.))
   geo=node('ShaderNodeNewGeometry','153 Actual outward plane');dot=node('ShaderNodeVectorMath','153 Protect returns and undersides');dot.operation='DOT_PRODUCT';l.new(geo.outputs['True Normal'],dot.inputs[0]);dot.inputs[1].default_value=normal
   facegate=smooth(dot.outputs['Value'],.80,.97)
   if 'dentil05' in name:
    other=node('ShaderNodeVectorMath','153 Actual exposed dentil plane4');other.operation='DOT_PRODUCT';l.new(geo.outputs['True Normal'],other.inputs[0]);other.inputs[1].default_value=(-.080621,.290493,.953475);facegate=calc('MAXIMUM',smooth(calc('ABSOLUTE',dot.outputs['Value']),.80,.97),smooth(calc('ABSOLUTE',other.outputs['Value']),.80,.97))
   gate=calc('MULTIPLY',spatial,facegate);changes=[]
   strengths={'Fine stone pits and dry pigment':.90,'Connected worn pigment islands':.85,'127 Broken sponge pigment at 4K scale':.85,'Interrupted vertical runoff':.88,'Grime branches':.80}
   for q in list(n):
    if q.type=='TEX_NOISE'and q.label in strengths:
     links=list(q.outputs['Fac'].links);g=calc('MULTIPLY',gate,strengths[q.label]);quiet=calc('ADD',calc('MULTIPLY',q.outputs['Fac'],calc('SUBTRACT',1,g)),calc('MULTIPLY',g,.5))
     for link in links:l.new(quiet,link.to_socket)
     changes.append({'node':q.name,'label':q.label,'toward_neutral_strength':strengths[q.label]})
    if group=='C1'and q.type=='MIX_RGB'and q.label in ['135 Deposits fed by broken cornice','148 Connected sheltered oxide and dust']:
     original=q.inputs[0].links[0].from_socket if q.inputs[0].is_linked else q.inputs[0].default_value;strength=.78 if q.label.startswith('135')else.72;fac=calc('MULTIPLY',original,calc('SUBTRACT',1,calc('MULTIPLY',gate,strength)));l.new(fac,q.inputs[0]);changes.append({'node':q.name,'label':q.label,'maximum_factor_reduction':strength})
   sl.link='OBJECT';sl.material=m;rows.append({'object':name,'group':group,'old_material':old.name,'new_material':m.name,'original_coordinate_anchor':origin,'ellipsoid_radii':radii,'world_outward_normal':normal,'edits':changes})
 unchanged=all(graph_signature(m)==s for m,s in oldgraphs.items())
 if not unchanged:raise RuntimeError('Original material graph mutated')
 return {'source':'152','references':['UCL-01','UCL-02','DP-03'],'assignments':rows,'original_material_graphs_preserved':unchanged,'geometry_mutated':False,'lighting_ramps_AO_and_ink_unchanged':True,'protected':['band10 profile3 inward returns','arch interiors','cornice undersides','all original material datablocks','152 age nodes/fields','151 crown geometry/core','approved black joints and curved arch rims'],'status':'Bounded candidate, independent review pending'}
