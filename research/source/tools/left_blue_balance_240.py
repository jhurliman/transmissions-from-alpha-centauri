"""Restore left-facade blue pigment without changing the accepted239 lighting."""
import bpy
from sun_material_alignment_239 import objects
from entrance_weathering_227 import Paint

def eligible(m):
 n=m.name
 if any(x in n for x in ('COL','masonry','137','189','oxide','Dark exposed substrate','Light exposed aggregate','crack core','spall core')):return False
 return ('Cladding | slate enamel'in n or 'Cladding | pale mineral blue'in n or '042 Street coating'in n or '193 Facade40 facade 064 Projected surface | Front-left'in n)

def apply(scene):
 cache={};rows=[];skipped=[]
 for ob in objects(scene):
  if ob.hide_render or ob.type!='MESH':continue
  if any(x in ob.name.lower()for x in('rubble','scrap','debris','y splice','y arm','y stem','cutter')):continue
  if any(c.name.startswith(('075','077','078','091','099','120','133','236'))for c in ob.users_collection):continue
  for i,slot in enumerate(ob.material_slots):
   old=slot.material
   if not old or not old.use_nodes or not eligible(old)or old.get('240 left blue balance'):continue
   if old not in cache:
    em=next((n for n in old.node_tree.nodes if n.type=='EMISSION'and n.inputs['Color'].is_linked),None)
    if not em:skipped.append(old.name);continue
    m=old.copy();m.name='240 Left blue balance | '+old.name;m['240 left blue balance']=True;m['240 source material']=old.name
    p=Paint(m);em=m.node_tree.nodes[em.name];source=em.inputs['Color'].links[0].from_socket
    geo=p.node('ShaderNodeNewGeometry','240 world-space side isolation');xyz=p.node('ShaderNodeSeparateXYZ','240 actual world X');p.l.new(geo.outputs['Position'],xyz.inputs[0]);side=p.remap(xyz.outputs['X'],-3,-1,1,0,'240 left-only boundary')
    rgb=p.node('ShaderNodeSeparateColor','240 preserve warm plaster and rust');rgb.mode='RGB';p.l.new(source,rgb.inputs['Color']);ratio=p.op('DIVIDE',rgb.outputs['Blue'],p.op('MAXIMUM',rgb.outputs['Red'],.00001));cool=p.remap(ratio,.94,1.12,0,1,'240 cool-pigment eligibility')
    tint=p.mix(1,source,(.82,1.035,1.39,1),'240 restrained blue pigment transfer','MULTIPLY')
    before=p.node('ShaderNodeRGBToBW','240 retained shaded luminance');p.l.new(source,before.inputs[0]);after=p.node('ShaderNodeRGBToBW','240 balanced pigment luminance');p.l.new(tint,after.inputs[0]);gain=p.op('DIVIDE',before.outputs[0],p.op('MAXIMUM',after.outputs[0],.000001));balanced=p.mix(1,tint,gain,'240 preserve239shade value','MULTIPLY')
    weight=p.op('MULTIPLY',side,p.op('MULTIPLY',cool,.82));out=p.mix(weight,source,balanced,'240 left facade blue restoration');p.l.new(out,em.inputs['Color']);cache[old]=m
   slot.link='OBJECT';slot.material=cache[old];rows.append({'object':ob.name,'slot':i,'source':old.name,'material':cache[old].name})
 return {'private_materials':len(cache),'bindings':rows,'skipped_unlinked_emission':sorted(set(skipped)),'sun_direction_and_all_existing_graphs_unchanged':True,'geometry_camera_world_unchanged':True,'right_side_exact_shader_gate':'WorldX≥−1m weight0; no effect regardless shared master use','warm_pigment_exact_gate':'B/R≤.94 weight0; transitionto1at1.12','left_cool_strength':.82,'tint_multiplier':[.82,1.035,1.39],'luminance':'RGBToBW source/tint ratio retains239linear shade value','scope':'Facade pigment families only; excludes services, beam oxide, rubble, landmark, damage cores'}
