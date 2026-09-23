"""User-directed20% perceived brightening of tapered under-cornice supports only."""
import bpy

def apply(C,factor=1.26):
 cache={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH' or ob.get('feature')!='shared undercornice dentil':continue
  for slot in ob.material_slots:
   old=slot.material
   if not old or not old.use_nodes:continue
   if old.get('129 cornice display gain')==factor:continue
   if old not in cache:
    m=old.copy();m.name='129 Cornice20% brighter '+old.name;m['129 cornice display gain']=factor;cache[old]=m;n,l=m.node_tree.nodes,m.node_tree.links
    em=next(q for q in n if q.type=='EMISSION');source=em.inputs['Color'].links[0].from_socket
    def calc(op,*values):
     q=n.new('ShaderNodeMath');q.operation=op
     for i,v in enumerate(values):
      if isinstance(v,(int,float)):q.inputs[i].default_value=v
      else:l.new(v,q.inputs[i])
     return q.outputs[0]
    def select(cond,a,b):return calc('ADD',calc('MULTIPLY',cond,a),calc('MULTIPLY',calc('SUBTRACT',1,cond),b))
    sep=n.new('ShaderNodeSeparateColor');sep.mode='RGB';sep.label='129 Linear to display-color correction';l.new(source,sep.inputs[0]);out=n.new('ShaderNodeCombineColor');out.mode='RGB';out.label='12920% brighter, hue and native lighting retained'
    for i in range(3):
     c=calc('MAXIMUM',sep.outputs[i],0);srgb=select(calc('LESS_THAN',c,.0031308),calc('MULTIPLY',c,12.92),calc('SUBTRACT',calc('MULTIPLY',calc('POWER',c,1/2.4),1.055),.055));v=calc('MINIMUM',calc('MULTIPLY',srgb,factor),1);linear=select(calc('LESS_THAN',v,.04045),calc('DIVIDE',v,12.92),calc('POWER',calc('DIVIDE',calc('ADD',v,.055),1.055),2.4));l.new(linear,out.inputs[i])
    l.new(out.outputs[0],em.inputs['Color'])
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'source':old.name,'material':cache[old].name})
 return {'requested_final_display_gain':1.2,'calibrated_shader_srgb_gain':factor,'blocks':len({x['object']for x in rows}),'material_variants':len(cache),'geometry_changed':False,'method':'Exact sRGB encode/gain/decode within native material. Shader gain1.26 compensates existing scene postprocessing; target final displayed gain1.20. Native lighting and pigment preserved.','assignments':rows}
