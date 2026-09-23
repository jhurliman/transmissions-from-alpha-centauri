"""Warm/violet core on151's new subtractive faces; existing surfaces immutable."""
from coliseum_core_tone_148 import COLORS
NAMES=['COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L']
def apply(C):
 copies={};rows=[]
 for name in NAMES:
  ob=C.objects[name];me=ob.data;tag=me.attributes['151 Exposed crown core'];faces=[p for p in me.polygons if tag.data[p.index].value>.5];slots={p.material_index for p in faces}
  for index in slots:
   old=ob.material_slots[index].material
   assert old and old.name.startswith('117 Exposed masonry core'),old.name if old else None
   if old.name not in copies:
    m=old.copy();m.name='151 Warm violet exposed masonry core';m['151 crown core']=True
    ramps=[q for q in m.node_tree.nodes if q.type=='VALTORGB' and len(q.color_ramp.elements)==4];assert len(ramps)==1
    for e,c in zip(ramps[0].color_ramp.elements,COLORS):e.color=c
    copies[old.name]=m
   me.materials.append(copies[old.name]);new=len(me.materials)-1;count=0
   for p in faces:
    if p.material_index==index:p.material_index=new;count+=1
   rows.append({'object':name,'source_material':old.name,'material':copies[old.name].name,'face_count':count})
 return {'assignments':rows,'new_core_faces_only':True,'existing_material_graphs_unchanged':True,'lighting_AO_grain_retained':True,'palette_linear_rgba':COLORS}
