"""Reallocate one existing age lobe onto its mapped lit spandrel; no added layer."""
import bpy,json
from pathlib import Path
from coliseum_facade_age_152 import shader_group
R=Path(__file__).resolve().parents[1]

def apply(C):
 cfg=json.loads((R/'config/coliseum-facade-age-152.json').read_text())
 before=[p[:] for p in cfg['groups']['primary']['deposit_polygons'][4]]
 cfg['groups']['primary']['deposit_polygons'][4]=[[u-2.2,v] for u,v in before]
 group=shader_group(cfg);group.name='155 Reallocated spandrel age'
 copies={};rows=[]
 for ob in C.all_objects:
  if ob.type!='MESH':continue
  for index,slot in enumerate(ob.material_slots):
   old=slot.material
   if not old or not old.use_nodes:continue
   nodes=[n for n in old.node_tree.nodes if n.type=='GROUP' and n.label=='152 Connected facade age']
   if not nodes:continue
   if old.name not in copies:
    m=old.copy();m.name='155 Reallocated age '+old.name
    for n in m.node_tree.nodes:
     if n.type=='GROUP' and n.label=='152 Connected facade age':n.node_tree=group
    copies[old.name]=m
   slot.link='OBJECT';slot.material=copies[old.name]
   rows.append({'object':ob.name,'slot':index,'source_material':old.name,'material':copies[old.name].name})
 return {'source':'153 retained candidate','assignments':rows,'private_materials':len(copies),'changed_polygon_before':before,'changed_polygon_after':cfg['groups']['primary']['deposit_polygons'][4],'only_change':'Existing primary lobe moves2.2 original units left onto mapped lit spandrel; no strength, palette, noise or geometry changes','mapped_anchor_pixel':[1767,613],'mapped_anchor_uv':[-1.73,-3.44],'secondary_field_unchanged':True}
