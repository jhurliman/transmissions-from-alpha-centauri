# SPDX-FileCopyrightText: 2026 John Hurliman and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. This program is distributed WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. See LICENSES/GPL-3.0-or-later.txt for the full terms.
#
"""Repeat complete accepted alley assemblies; no generated skyscraper kit."""
import bpy,json
from mathutils import Matrix,Vector
SOURCES=['027 Reviewed architecture assembly','031 Distant large service infrastructure','033 Front left section architecture','034 Distinct right buildings','035 Service destinations and side architecture','073 wall fastenings','074 Side alley pipe relocation','133 Alley damage study','145 Placed panel Architecture | layout_broad.007','145 Placed panel Architecture | layout_access.008','145 Placed panel Architecture | layout_transition.010','145 Panel detail layers']
FILMS=['189 Fastener corrosion films','195 Plate rusty water']
def verts(o,T=None):
 T=(T or Matrix.Identity(4))@o.matrix_world
 if o.instance_type=='COLLECTION' and o.instance_collection:
  T=T@Matrix.Translation(-o.instance_collection.instance_offset)
  for q in o.instance_collection.objects:
   if not q.hide_render:yield from verts(q,T)
  for ch in o.instance_collection.children:
   for q in ch.all_objects:
    if not q.hide_render:yield from verts(q,T)
 elif o.type in ('MESH','CURVE'):
  for p in o.bound_box:yield T@Vector(p)
def visible_objects(c):
 if c.hide_render:return
 yield from c.objects
 for child in c.children:yield from visible_objects(child)
def bounds(obs):
 points=[v for o in obs for v in verts(o)]
 return [min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)]
def private_copy(C,label,state_cache):
 collections={};objects={}
 def cp(c):
  if c in collections:return collections[c]
  new=bpy.data.collections.new(label+' | '+c.name);new.use_fake_user=True;new.instance_offset=c.instance_offset;new.hide_render=c.hide_render;new.hide_viewport=c.hide_viewport;collections[c]=new
  for ob in c.objects:
   if ob in objects:q=objects[ob]
   else:
    q=ob.copy();assert q.data==state_cache[ob][1],ob.name;q.name=label+' | '+ob.name;q.parent=None;q.matrix_world=state_cache[ob][0];q['212 source object']=ob.name;objects[ob]=q
    if ob.instance_collection:q.instance_collection=cp(ob.instance_collection)
   new.objects.link(q)
  for ch in c.children:new.children.link(cp(ch))
  return new
 root=cp(C);return root,objects

def repeat_guard_pairs(scene):
 import architecture_ink_visibility_192 as g192,architecture_ink_visibility_205 as g205,architecture_ink_visibility_207 as g207
 groups=json.loads(scene.get('212 source name groups','[]'))
 for mod in(g192,g205,g207):
  initial=dict(mod.PAIRS)
  for mapping in groups:
   for name,targets in initial.items():
    if name in mapping and all(t in mapping for t in targets):mod.PAIRS[mapping[name]]=tuple(mapping[t]for t in targets)

def apply(scene):
 source=[];bycol={}
 for name in SOURCES:
  c=bpy.data.collections.get(name)
  if not c or c.hide_render:continue
  rows=[o for o in visible_objects(c) if not o.hide_render and (o.type in ('MESH','CURVE') or o.instance_type=='COLLECTION')]
  source.extend(rows);bycol[name]=len(rows)
 source=sorted(set(source),key=lambda o:o.name);assert source
 #Read every source transform before any clone/collection mutation invalidates the dependency graph.
 all_source=set(source);visited=set()
 def gather(c):
  if c in visited:return
  visited.add(c)
  for o in c.objects:
   all_source.add(o)
   if o.instance_collection:gather(o.instance_collection)
  for child in c.children:gather(child)
 for o in source:
  if o.instance_collection:gather(o.instance_collection)
 state_cache={o:(o.matrix_world.copy(),o.data)for o in all_source}
 root_points={o:list(verts(o))for o in source}
 def cached_bounds(obs):
  points=[p for o in obs for p in root_points[o]]
  return [min(p[i]for p in points)for i in range(3)],[max(p[i]for p in points)for i in range(3)]
 print('212 SOURCE TRANSFORMS CACHED',len(state_cache),flush=True)
 full=bpy.data.collections.new('212 Accepted alley strip source');full.use_fake_user=True
 for o in source:full.objects.link(o)
 lo,hi=cached_bounds(source)
 frontobjs=[]
 for o in source:
  vv=root_points[o]
  if vv and max(v.y for v in vv)<=3.0 and min(v.y for v in vv)>=-10:frontobjs.append(o)
 front=bpy.data.collections.new('212 Accepted front pair source');front.use_fake_user=True
 for o in frontobjs:front.objects.link(o)
 flo,fhi=cached_bounds(frontobjs)
 middleobjs=[o for o in source if (vv:=root_points[o]) and max(v.y for v in vv)<=20.3]
 middle=bpy.data.collections.new('212 Accepted front and middle pairs source');middle.use_fake_user=True
 for o in middleobjs:middle.objects.link(o)
 mlo,mhi=cached_bounds(middleobjs)
 #Stop short of the actual low landmark surfaces crossing this alley's footprint.
 landmark=[]
 for o in bpy.data.collections['110 Coliseum detailed front ruin'].all_objects:
  if o.hide_render or o.type!='MESH':continue
  vv=[o.matrix_world@Vector(p)for p in o.bound_box]
  if min(p.z for p in vv)>hi[2] or max(p.x for p in vv)<lo[0] or min(p.x for p in vv)>hi[0]:continue
  landmark.extend(p.y for p in vv)
 stop=min(landmark)-4.0;C=bpy.data.collections.new('212 Accepted alley continuation');scene.collection.children.link(C);placements=[];inkgroups=[];namegroups=[];allfar=set()
 excluded_source=set()
 for vl in scene.view_layers:
  if vl.use_freestyle:
   ls=vl.freestyle_settings.linesets.get('Selective geometry contours')
   if ls and ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':excluded_source.update(ls.collection.all_objects)
 print('212 SOURCES AND CLEARANCE READY',len(source),stop,flush=True)
 for dy in (48,88,128,168,208,248):
  master=full if hi[1]+dy<=stop else (middle if mhi[1]+dy<=stop else (front if fhi[1]+dy<=stop else None))
  if not master:break
  print('212 COPYING DEPTH',dy,flush=True)
  copied,mapping=private_copy(master,'212 D'+str(dy),state_cache);namegroups.append({o.name:q.name for o,q in mapping.items()})
  filtercol=bpy.data.collections.new('212 Ink depth '+str(dy));filtercol.use_fake_user=True
  for oldob,newob in mapping.items():
   if newob.type in ('MESH','CURVE'):
    allfar.add(newob)
    if oldob not in excluded_source:filtercol.objects.link(newob)
  inkgroups.append((dy,filtercol))
  q=bpy.data.objects.new('212 Alley repeat '+str(dy),None);q.instance_type='COLLECTION';q.instance_collection=copied;q.location=(0,dy,0);C.objects.link(q)
  usehi=hi if master==full else (mhi if master==middle else fhi);uselo=lo if master==full else (mlo if master==middle else flo)
  placements.append({'translation_y_m':dy,'source':master.name,'world_bounds':[[uselo[0],uselo[1]+dy,uselo[2]],[usehi[0],usehi[1]+dy,usehi[2]]],'uniform_scale':1.0})
  if master!=full:break
 scene['212 source name groups']=json.dumps(namegroups)
 #Private far IDs prevent distant line adjustments from changing the accepted near alley.
 newobjects=allfar;unions={}
 for vl in scene.view_layers:
  if not vl.use_freestyle:continue
  for ls in vl.freestyle_settings.linesets:
   if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
    old=ls.collection
    if old.name not in unions:
     u=bpy.data.collections.new('212 Far exclusion union | '+old.name);u.use_fake_user=True
     for o in set(old.all_objects)|newobjects:u.objects.link(o)
     unions[old.name]=u
    ls.collection=unions[old.name]
  for index,(dy,c)in enumerate(inkgroups):
   ls=vl.freestyle_settings.linesets.new('212 Far architecture '+str(dy));ls.select_by_collection=True;ls.collection=c;ls.collection_negation='INCLUSIVE';ls.select_by_edge_types=True
   for prop in ('select_ridge_valley','select_suggestive_contour','select_material_boundary','select_contour','select_external_contour'):setattr(ls,prop,False)
   ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_edge_mark=True;ls.linestyle.thickness=(.35,.25,.18,.15,.13)[min(index,4)];ls.linestyle.color=(.027,.024,.035);ls.linestyle.alpha=.86
 #Render pigment films only in beauty; they never enter the native ink view map.
 pigment=bpy.data.collections.new('212 Repeated pigment beauty only');scene.collection.children.link(pigment);film_sources=[]
 for name in FILMS:
  c=bpy.data.collections.get(name)
  if c and not c.hide_render:film_sources.extend(o for o in c.all_objects if not o.hide_render)
 fm=bpy.data.collections.new('212 Accepted pigment source');fm.use_fake_user=True
 for o in set(film_sources):fm.objects.link(o)
 for row in placements:
  if row['source']!=full.name:continue #Combined original films cannot be cropped without inventing new contact detail.
  q=bpy.data.objects.new('212 Pigment repeat '+str(row['translation_y_m']),None);q.instance_type='COLLECTION';q.instance_collection=fm;q.location.y=row['translation_y_m'];pigment.objects.link(q)
 def find(lc):
  if lc.collection==pigment:return lc
  for ch in lc.children:
   v=find(ch)
   if v:return v
 for vl in scene.view_layers:
  if vl.use_freestyle:
   node=find(vl.layer_collection)
   if node:node.exclude=True
 # Dedicated101 city-only contact companion is owned by the replaced family.
 old_city_gp=bpy.data.objects.get('101 A city contacts')
 if old_city_gp:old_city_gp.hide_render=True
 hidden=[]
 for o in list(bpy.data.collections['101 Original city layout study'].all_objects):
  if o.get('reference_mass') and not o.hide_render:o.hide_render=True;hidden.append(o.name)
 return {'source_scene':'209 plus213 material-only scuffs if applied by caller','source_collections':bycol,'source_objects':len(source),'private_far_objects':sum(len(g)for g in namegroups),'far_ink_depth_groups':[dy for dy,_ in inkgroups],'source_native_bounds':[lo,hi],'front_pair_objects':len(frontobjs),'front_pair_bounds':[flo,fhi],'front_middle_objects':len(middleobjs),'front_middle_bounds':[mlo,mhi],'placements':placements,'landmark_nearest_surface_y':min(landmark),'stop_y_with4m_clearance':stop,'original_city_hidden':hidden,'no_original_geometry_material_or_transform_changes':True,'preserved':['near alley','landmark','road and rocks','middle rubble and ruined walls','sky and native202volume'],'excluded':['all GP/contact ink bakes','hidden cutters','old hidden facade systems','terrain','cameras/lights'],'film_rule':'Original189+195 films repeated in beauty only for full strips; final partial pair relies on original shader wear and omits combined films instead of copying unrelated marks.'}

def install_far_guard_callbacks(scene):
 """Apply existing proven source/receiver tests to private far line styles too."""
 import parameter_editor
 from types import SimpleNamespace
 original=list(parameter_editor.callbacks_modifiers_post)
 guards=[f for f in original if any(getattr(f,'_guard'+str(n),False)for n in(192,205,207))]
 def callback(scene,layer,ls):
  if not ls.name.startswith('212 Far architecture '):return[]
  proxy=SimpleNamespace(name='Selective geometry contours')
  return[shader for f in guards for shader in f(scene,layer,proxy)]
 callback._guard212=True
 parameter_editor.callbacks_modifiers_post[:]=[f for f in original if not getattr(f,'_guard212',False)]
 parameter_editor.callbacks_modifiers_post.append(callback)
 return {'styles':'212 Far architecture *','existing_receiver_rules':[192,205,207],'source_callback_count':len(guards),'near_callbacks_unchanged':True}
