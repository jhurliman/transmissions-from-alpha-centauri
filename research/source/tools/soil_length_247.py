"""Shorten the roadward ends of246's two native soil tracks."""
import bpy

def apply(scene):
 ob=bpy.data.objects['Street foundation'];m=ob.material_slots[0].material.copy();m.name='247 Alley tracks shortened to user marker';ob.material_slots[0].material=m
 live=set()
 def visit(n):
  if n in live:return
  live.add(n)
  for i in n.inputs:
   for l in i.links:visit(l.from_node)
 visit(next(n for n in m.node_tree.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output))
 found=[]
 for n in live:
  if n.type=='MAP_RANGE' and abs(n.inputs['From Min'].default_value-3.7)<1e-5 and abs(n.inputs['From Max'].default_value-5.3)<1e-5:
   n.inputs['From Min'].default_value=6.35;n.inputs['From Max'].default_value=7.15;n.label='247 Roadward fade at user marker';found.append(n.name)
 assert len(found)==1,found
 return {'changed_nodes':found,'roadward_fade_world_x':[6.35,7.15],'previous_fade':[3.7,5.3],'track_count':2,'alley_end_x':21.0,'other_shader_parameters_unchanged':True,'marker_interpretation':'Approximate road-plane limit indicated in user screenshot; soft granular fade, no hard transverse cutoff.'}
