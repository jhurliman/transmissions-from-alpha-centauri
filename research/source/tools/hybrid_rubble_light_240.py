"""Receiver-linked previous sun for foreground junk and stones; architecture retains239sun."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from sun_material_alignment_239 import objects
from entrance_weathering_227 import Paint
R=Path(__file__).resolve().parents[1]
def apply(scene):
 audit=json.loads((R/'art/studies/road-characters-239/audit.json').read_text())['material_alignment'];changes={}
 for row in audit['changes']:changes.setdefault(row['material'],[]).append(row)
 rocksources={r['material']for r in audit['changes']if 'rock form light'in r['role']}
 targets=[];middle=[]
 for ob in objects(scene):
  if ob.type!='MESH'or ob.hide_render:continue
  cn={c.name for c in ob.users_collection};name=ob.name.lower();mats=[s.material for s in ob.material_slots if s.material]
  near=('075 Scrap integration'in cn and ob.get('zone')=='near')or'06 Actual foreground wreckage and rubble'in cn
  rock=any(m.name in rocksources for m in mats)or'075 Soil and mineral scatter'in cn or'090 Small embedded stones'in cn or name.startswith(('077 embedded stone','077 layered masonry fragment','077 broken low rubble tongue','077 interstitial small debris','236 left rubble tongue masonry','236 right rubble tongue masonry'))
  if near or rock:targets.append(ob)
  if cn.intersection({'077 End rubble depth clusters','078 End rubble tangled structural remnants','236 Backward rubble transition'})or('075 Scrap integration'in cn and ob.get('zone')=='end'):middle.append(ob)
 assert len(targets)>500
 # Restore only old light-vector sockets on the selected receivers.
 cache={};restored=[]
 for ob in targets:
  for sl in ob.material_slots:
   old=sl.material
   if not old or old.name not in changes:continue
   if old not in cache:
    m=old.copy();m.name='240 Previous rock light | '+old.name
    for row in changes[old.name]:m.node_tree.nodes[row['node']].inputs[1].default_value=row['before']
    cache[old]=m
   sl.link='OBJECT';sl.material=cache[old];restored.append(ob.name)
 def linkcollection(name,exclude=False):
  c=bpy.data.collections.new(name);c.use_fake_user=True
  for ob in targets:c.objects.link(ob)
  for item in c.collection_objects:item.light_linking.link_state='EXCLUDE'if exclude else'INCLUDE'
  return c
 sun=bpy.data.objects['Soft warm directional daylight'];sun.light_linking.receiver_collection=linkcollection('240 New sun excludes old-lit rubble',True)
 fill=bpy.data.objects['Broad diffuse facade fill'];fill.light_linking.receiver_collection=linkcollection('240 Fill excludes old-lit rubble',True)
 oldsun=sun.copy();oldsun.data=sun.data.copy();oldsun.name='240 Previous sun | rubble and stones only';scene.collection.objects.link(oldsun);oldsun.rotation_euler=Vector((.4348281919956207,.4928053915500641,-.7537024021148682)).to_track_quat('-Z','Y').to_euler();oldsun.light_linking.receiver_collection=linkcollection('240 Previous sun rubble receivers')
 # Small pigment lift for the middle piles only, before existing atmosphere.
 liftcache={};lifted=[]
 for ob in middle:
  for sl in ob.material_slots:
   old=sl.material
   if not old or not old.use_nodes:continue
   if old not in liftcache:
    m=old.copy();m.name='240 Gentle middle rubble lift | '+old.name;p=Paint(m);em=next((n for n in p.n if n.type=='EMISSION'),None)
    if em:
     src=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value);out=p.mix(1,src,(1.10,1.10,1.10,1),'240 ten percent middle-pile lift','MULTIPLY');p.l.new(out,em.inputs['Color'])
    liftcache[old]=m
   sl.link='OBJECT';sl.material=liftcache[old];lifted.append(ob.name)
 # Undo rejected239road treatment, retaining native shadow receiver and bootcontacts.
 soil=bpy.data.objects['Street foundation'];old=soil.material_slots[0].material;m=old.copy();m.name='240 Original road texture restored with character contact';soil.material_slots[0].link='OBJECT';soil.material_slots[0].material=m;n=m.node_tree.nodes;l=m.node_tree.links;l.new(n['Image Texture'].outputs['Color'],n['Mix (Legacy).012'].inputs[1])
 return {'previous_sun_receivers':len(targets),'receiver_names':[o.name for o in targets],'restored_materials':len(cache),'middle_lift_materials':len(liftcache),'middle_lift_factor':1.10,'middle_objects':len(set(lifted)),'road':'Original packed image feeds existing AO directly again; no averaging or239broad paint connected. Character contact preserved.','architecture_sun_239_unchanged':True,'geometry_world_sprite_compositor_unchanged':True}
