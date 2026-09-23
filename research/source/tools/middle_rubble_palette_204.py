"""Palette-only50% native lit blue/rust transfer; preserve source luminance/depth."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/middle-rubble-204'
FAMILIES=('075 Scrap integration','077 End rubble depth clusters','078 End rubble tangled structural remnants','133 Ruined transition structures')
def _palette(scene):
 near=bpy.data.collections['075 Scrap integration'];sources=[]
 for o in near.all_objects:
  if o.type!='MESH'or o.get('zone')!='near':continue
  for slot in o.material_slots:
   m=slot.material
   if not m or not m.use_nodes:continue
   ramp=next((n for n in m.node_tree.nodes if n.label=='104 steel blue shade to warm rust light'),None)
   if ramp:sources.append((m,ramp))
 assert sources,'Accepted104 lighting-driven near-scrap palette not found'
 m,ramp=sources[0]
 return {'material':m.name,'ramp_label':ramp.label,'interpolation':ramp.color_ramp.interpolation,'elements':[(float(e.position),tuple(e.color))for e in ramp.color_ramp.elements],'value105_note':'105 preserves104 hues through a scalar value curve;204 preserves target luminance rather than importing foreground darkness'}
def _group(palette):
 g=bpy.data.node_groups.new('204 Half near-junk hue at retained target luminance','ShaderNodeTree');g.interface.new_socket(name='Original lit color',in_out='INPUT',socket_type='NodeSocketColor');g.interface.new_socket(name='Half palette color',in_out='OUTPUT',socket_type='NodeSocketColor');n=g.nodes;l=g.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput')
 df=n.new('ShaderNodeBsdfDiffuse');df.label='204 Same104 actual illumination response';df.inputs['Color'].default_value=(.65,.65,.65,1)
 sr=n.new('ShaderNodeShaderToRGB');l.new(df.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0])
 pal=n.new('ShaderNodeValToRGB');pal.label='204 Copied accepted104 blue shade to rusty light';pal.color_ramp.interpolation=palette['interpolation']
 for idx,(pos,color)in enumerate(palette['elements']):
  e=pal.color_ramp.elements[idx]if idx<2 else pal.color_ramp.elements.new(pos);e.position=pos;e.color=color
 l.new(bw.outputs[0],pal.inputs[0])
 old_y=n.new('ShaderNodeRGBToBW');old_y.label='204 Retain original200 shadow AO weathering value';l.new(i.outputs[0],old_y.inputs[0]);new_y=n.new('ShaderNodeRGBToBW');l.new(pal.outputs[0],new_y.inputs[0])
 denom=n.new('ShaderNodeMath');denom.operation='MAXIMUM';denom.inputs[1].default_value=.00001;l.new(new_y.outputs[0],denom.inputs[0]);gain=n.new('ShaderNodeMath');gain.operation='DIVIDE';l.new(old_y.outputs[0],gain.inputs[0]);l.new(denom.outputs[0],gain.inputs[1])
 recolor=n.new('ShaderNodeVectorMath');recolor.operation='SCALE';recolor.label='204 Palette hue with exact original luminance';l.new(pal.outputs[0],recolor.inputs[0]);l.new(gain.outputs[0],recolor.inputs['Scale'])
 mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.5;mix.label='204 Exactly50 percent original +50 percent near-junk hue';l.new(i.outputs[0],mix.inputs[1]);l.new(recolor.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],o.inputs[0]);return g

def _center(ob):
 return sum((ob.matrix_world@Vector(v)for v in ob.bound_box),Vector())/8

def apply(scene):
 O.mkdir(parents=True,exist_ok=True);palette=_palette(scene);group=_group(palette);targets={};hidden=[]
 for family in FAMILIES:
  c=bpy.data.collections.get(family)
  assert c is not None,family
  for ob in c.all_objects:
   if ob.type!='MESH'or(family=='075 Scrap integration'and ob.get('zone')!='end'):continue
   if c.hide_render or ob.hide_render:hidden.append(ob.name);continue
   targets[ob.name]=(ob,family)
 for ob in scene.objects:
  if ob.type!='MESH'or ob.get('scatter_zone')!='bank'or not ob.get('rock_family'):continue
  center=_center(ob)
  if not(24<=center.y<=60):continue
  if ob.hide_render:hidden.append(ob.name);continue
  targets[ob.name]=(ob,'Middle bank/foundation fragments y24–60')
 cache={};rows=[];familycounts={}
 for name,(ob,family)in sorted(targets.items()):
  center=_center(ob);bound=[world_to_camera_view(scene,scene.camera,ob.matrix_world@Vector(v))for v in ob.bound_box];assign=[]
  for slot in ob.material_slots:
   old=slot.material
   if old is None:continue
   assert not old.get('204 middle palette'),'Apply204 only once'
   if old not in cache:
    old.use_fake_user=True
    m=old.copy();m.name='204 Half blue-rust hue | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
    ems=[q for q in n if q.type=='EMISSION'and q.inputs['Color'].is_linked]
    assert ems,('Expected existing linked native lit pigment',old.name)
    for em in ems:
     original=em.inputs['Color'].links[0].from_socket;q=n.new('ShaderNodeGroup');q.node_tree=group;q.label='20450% hue transfer after retained original lighting';l.new(original,q.inputs[0]);l.new(q.outputs[0],em.inputs['Color'])
    m['204 middle palette']=True;cache[old]=m
   slot.link='OBJECT';slot.material=cache[old];assign.append({'original':old.name,'private':slot.material.name})
  familycounts[family]=familycounts.get(family,0)+1
  rows.append({'object':name,'family':family,'center_world':list(center),'projected_bounds_4k':[min(v.x for v in bound)*3840,(1-max(v.y for v in bound))*2885,max(v.x for v in bound)*3840,(1-min(v.y for v in bound))*2885],'slots':assign})
 report={'study':204,'targets':rows,'target_counts':familycounts,'total_objects':len(rows),'private_materials':len(cache),'hidden_excluded':sorted(set(hidden)),'palette_source':palette,'mix_fraction':.5,'existing_luminance_preserved':True,'placement_geometry_normals_unchanged':True,'source_material_graphs_private_copied':True,'excluded':['075zone=near foreground junk','scatter_zone=road accepted stones','farcity','bank fragments outsidey24–60'],'references':['UM-01','UP-03','DP-08'],'integration_order':'Apply after200native replay so final200worn facing and darker recessed core retain their value modulation','visual_status':'Final203native proof pending; no standaloneGPU'}
 return report
if __name__=='__main__':
 s=bpy.context.scene;a=apply(s);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('204_READY',a['total_objects'],a['private_materials'],a['target_counts'])
