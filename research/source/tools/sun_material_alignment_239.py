"""Align explicitly identified authored form-light vectors with the visible sun.
No blanket DOT replacement: pigment bands, geometric gates and sky remain fixed.
"""
import bpy
from mathutils import Vector
from collections import Counter
SUNWARD=tuple(Vector((.10937,.95030,.29150)).normalized())

def objects(scene):
 found=set(scene.objects);todo=list(found)
 while todo:
  o=todo.pop()
  if o.instance_collection:
   for q in o.instance_collection.all_objects:
    if q not in found:found.add(q);todo.append(q)
 return found

def active(nt):
 incoming={};outgoing={}
 for l in nt.links:
  incoming.setdefault(l.to_node,[]).append(l);outgoing.setdefault(l.from_node,[]).append(l)
 todo=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'and n.is_active_output];seen=set()
 while todo:
  n=todo.pop()
  if n in seen:continue
  seen.add(n);todo.extend(l.from_node for l in incoming.get(n,[]))
 return seen,incoming,outgoing

def near(v,w):return all(abs(a-b)<.00002 for a,b in zip(v,w))

def classify(n,inc,out,m):
 if n.type!='VECT_MATH'or n.operation!='DOT_PRODUCT':return None
 links=inc.get(n,[])
 if any(l.to_socket==n.inputs[1]for l in links):return None
 source=next((l for l in links if l.to_socket==n.inputs[0]),None)
 if not source:return None
 v=tuple(n.inputs[1].default_value);dest=out.get(n,[])
 direct=source.from_node.type=='NEW_GEOMETRY'and source.from_socket.name=='Normal'
 if direct and near(v,(.38,-.67,.64)):
  if n.label=='Broad form lighting':return '113 broad masonry form light'
  if any(l.to_node.label=='133 Broken-building shade families'for l in dest):return '133 broken-building form light'
  if '117 Exposed masonry core'in m.name:return '117 exposed core form light'
  if any(l.to_node.label=='Two broad painted light families'for l in dest):return '102 legacy city form light'
  if m.name.startswith('FAR077'):return '077 legacy distant form light'
 if direct and near(v,(.65,-.45,.61))and any(l.to_node.type=='VALTORGB'for l in dest):return '038 facade palette form light'
 if direct and near(v,(-.46,-.5,.735))and any(l.to_node.type=='MAP_RANGE'for l in dest):return '085 earth form light'
 if direct and near(v,(-.4348281919956207,-.4928053915500641,.7537024021148682))and any(l.to_node.type=='MATH'for l in dest):return '091 actual-sun-derived rock form light'
 # 128 macro compensation uses the same authored light vector on its normalized
 # cylindrical macro normal; 129 replaces the micro-normal by a joint-end normal.
 if near(v,(.38,-.67,.64))and source.from_node.type=='VECT_MATH'and source.from_node.operation=='NORMALIZE':
  if any(q.label=='Broad form lighting'for q in m.node_tree.nodes)and any(q.label=='128 Only outward-facing masonry receives broad fill'for q in m.node_tree.nodes):return '128/129 paired macro illumination'
 return None

def apply(scene):
 obs=objects(scene);users={}
 for o in obs:
  if o.hide_render:continue
  for i,s in enumerate(o.material_slots):
   if s.material:users.setdefault(s.material,[]).append((o,i))
 rows=[];bindings=[];excluded=Counter();group_nodes=0
 for old,uses in users.items():
  if not old.use_nodes or old.get('239 visible sun aligned'):continue
  seen,inc,out=active(old.node_tree);matches=[]
  for n in seen:
   if n.type=='GROUP':group_nodes+=1
   role=classify(n,inc,out,old)
   if role:matches.append((n.name,role,tuple(n.inputs[1].default_value)))
   elif n.type=='VECT_MATH'and n.operation=='DOT_PRODUCT':excluded[n.label or 'unlabeled non-matched math']+=1
  if not matches:continue
  m=old.copy();m.name='239 Sun-aligned | '+old.name;m['239 visible sun aligned']=True;m['239 source material']=old.name
  for name,role,before in matches:
   m.node_tree.nodes[name].inputs[1].default_value=SUNWARD
   rows.append({'source_material':old.name,'material':m.name,'node':name,'role':role,'before':before,'after':SUNWARD})
  for o,i in uses:o.material_slots[i].link='OBJECT';o.material_slots[i].material=m;bindings.append({'object':o.name,'slot':i,'source':old.name,'material':m.name})
 return {'sunward':SUNWARD,'materials':len(set(r['material']for r in rows)),'matched_sockets':len(rows),'changes':rows,'bindings':bindings,'excluded_dot_labels':dict(excluded),'active_group_nodes_not_recursively_changed':group_nodes,'geometry_camera_world_lights_unchanged':True,'palette_ramps_weathering_and_all_other_sockets_preserved':True,'approach':'Private material copies; explicit active-output-connected form-light signatures only.128 macro-normal compensation aligned as a pair. Pigment bands/coordinate dots/normal masks/sky remain unchanged.'}
