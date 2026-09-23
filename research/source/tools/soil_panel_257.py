import bpy
from entrance_weathering_227 import Paint

def apply(s):
 ob=bpy.data.objects['Utility base.028'];removed=[]
 for mod in list(ob.modifiers):
  if mod.name in ['069 localized fracture','071 localized endpoint spall']:
   removed.append(mod.name);ob.modifiers.remove(mod)
 assert len(removed)==2
 # Existing baked fracture outlines must disappear with their source cut.
 gp=s.objects['096 damage ink'];gp.data=gp.data.copy();removed_ink=[]
 for layer in gp.data.layers:
  for f in layer.frames:
   ids=[]
   for i,st in enumerate(f.drawing.strokes):
    pts=[gp.matrix_world@p.position for p in st.points]
    if pts and all(9.10<p.x<9.25 and 17.15<p.y<20.45 and .13<p.z<1.26 for p in pts):ids.append(i)
   if ids:f.drawing.remove_strokes(indices=ids);removed_ink.extend(ids)
 assert removed_ink==[2,3,4],removed_ink
 ground=s.objects['Street foundation'];m=ground.material_slots[0].material.copy();m.name='257 Disturbed granular alley tracks';ground.material_slots[0].material=m
 p=Paint(m);op=p.op;region=m.node_tree.nodes['Mix (Legacy).008'];geo=p.node('ShaderNodeNewGeometry','257 stable world grain');pos=geo.outputs['Position']
 grain=p.remap(p.noise(pos,31,2),.54,.69);clumps=p.remap(p.noise(pos,8.5,2.4),.58,.72)
 grit=op('MAXIMUM',op('MULTIPLY',grain,.82),op('MULTIPLY',clumps,.67))
 control=p.node('ShaderNodeValue','257 grit strength');control.name='257 Grit strength';control.outputs[0].default_value=.9
 for idx in [1,2]:
  old=region.inputs[idx].links[0].from_socket;trace=old.node;assert '246 continuous granular tyre trace'in trace.label,trace.label
  mask=trace.inputs[0].links[0].from_socket
  dark=p.mix(1,old,(.27,.24,.21,1),'257 mineral clod tone','MULTIPLY')
  f=op('MULTIPLY',mask,op('MULTIPLY',control.outputs[0],grit))
  p.l.new(p.mix(f,old,dark,'257 grains within existing tracks'),region.inputs[idx])
 return {'removed_modifiers':removed,'removed_damage_strokes':removed_ink,'panel':'Utility base.028','upper_crack_unchanged':True,'track_mask_unchanged':True,'grit_strength':.9}
