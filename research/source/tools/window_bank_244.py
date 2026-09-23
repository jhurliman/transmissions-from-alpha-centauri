"""Instance-private weathering for the original rear-right 5x2 slider bank.
No edits to shared window masters or the warm building's windows.
"""
import bpy, json, random, hashlib, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from entrance_weathering_227 import Paint

def finish(base, axis, seed, role):
 m=base.copy();m.name=f'244 Bank {seed} {role} | '+base.name
 p=Paint(m);op=p.op;l=p.l
 em=next(n for n in p.n if n.type=='EMISSION')
 old=em.inputs['Color'].links[0].from_socket if em.inputs['Color'].is_linked else tuple(em.inputs['Color'].default_value)
 rng=random.Random(seed)
 tc=p.node('ShaderNodeTexCoord','244 original pane bounds');sep=p.node('ShaderNodeSeparateXYZ','244 pane axes');l.new(tc.outputs['Generated'],sep.inputs[0]);u,z=sep.outputs[axis],sep.outputs['Z']
 field=p.noise(p.vec(op('ADD',op('MULTIPLY',u,2.4),rng.uniform(0,20)),op('MULTIPLY',z,2.8),rng.uniform(0,20)),1,2.5)
 fine=p.noise(p.vec(op('MULTIPLY',u,34),op('MULTIPLY',z,48),rng.uniform(0,40)),1,2)
 rain=0;params=[]
 for k in range(3):
  center=(k+rng.uniform(.22,.78))/3;width=rng.uniform(.045,.085);length=rng.uniform(.52,.99);params.append([center,width,length])
  down=op('SUBTRACT',1,z);t=op('DIVIDE',down,length)
  drift=op('MULTIPLY',op('SUBTRACT',field,.5),.014)
  d=op('ABSOLUTE',op('SUBTRACT',u,op('ADD',center,drift)))
  w=op('MULTIPLY',width,p.remap(t,0,1,1,.2))
  body=p.remap(op('DIVIDE',d,w),.14,1,1,0)
  fade=p.remap(t,.2,1,1,0)
  rain=op('MAXIMUM',rain,op('MULTIPLY',body,fade))
 stain=p.remap(op('ADD',field,op('MULTIPLY',fine,.08)),.46,.66)
 basal=p.remap(z,.025,op('ADD',.13,op('MULTIPLY',field,.19)),1,0)
 if role=='glass':
  light=p.mix(1,old,(1.63,1.57,1.50,1),'244 subtle mineral light response','MULTIPLY')
  body=p.mix(op('MULTIPLY',stain,.40),old,light,'244 irregular translucent spec staining')
  dark=p.mix(1,old,(.35,.41,.50,1),'244 cool rain-channel value','MULTIPLY')
  body=p.mix(op('MULTIPLY',rain,.68),body,dark,'244 three unequal tapered rain traces')
  residue=op('MULTIPLY',basal,p.remap(fine,.18,.78,.35,.7))
  body=p.mix(residue,body,(.115,.124,.145,1),'244 ragged lower mineral deposit')
 else:
  dirt=p.mix(1,old,(.56,.59,.65,1),'244 cool weathered frame','MULTIPLY')
  body=p.mix(op('MULTIPLY',op('MAXIMUM',rain,basal),.34),old,dirt,'244 frame runoff and lower grit')
  body=p.mix(op('MULTIPLY',stain,.13),body,p.mix(1,old,(1.20,1.19,1.20,1),'244 frame mineral light','MULTIPLY'),'244 restrained irregular frame patina')
 l.new(body,em.inputs['Color']);m['244 private bank weathering']=True;m['244 seed']=seed;m['244 role']=role
 return m,params

def signature(m):
 return hashlib.sha256(repr(([(n.name,n.bl_idname,[(i.name,str(i.default_value))for i in n.inputs if hasattr(i,'default_value')])for n in m.node_tree.nodes],[(x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name)for x in m.node_tree.links])).encode()).hexdigest() if m and m.use_nodes else None

def apply(scene):
 assert not scene.get('window_bank244_applied')
 root=scene.objects['right_horizontal_utility'];original=root.instance_collection
 prior={m.name:signature(m) for m in bpy.data.materials}
 bindings={o:tuple(s.material for s in o.material_slots)for o in bpy.data.objects if o.type=='MESH'}
 matrices={o:tuple(v for row in o.matrix_world for v in row)for o in bpy.data.objects}
 rows=[];copied=[];assemblies=[]
 # Every path is copied separately: repeated prefab leaves get independent seeded material IDs.
 def clone(c,seed):
  out=bpy.data.collections.new(f'244 Private window path {seed} | '+c.name);out.instance_offset=c.instance_offset;out.use_fake_user=True
  for i,o in enumerate(c.objects):
   role='glass' if o.type=='MESH' and any(sl.material and ('smoked blue' in sl.material.name or 'glass' in sl.material.name.lower()) for sl in o.material_slots) else ('frame' if o.type=='MESH' and o.name.startswith(('Flush perimeter frame','Sliding leaf frame','Continuous sliding track')) else None)
   if o.instance_collection:
    q=o.copy();q.name='244 Bank path | '+o.name;q.instance_collection=clone(o.instance_collection,seed+31+i);out.objects.link(q);copied.append((o,q))
   elif role:
    q=o.copy();q.name=f'244 Window {seed} | '+o.name;out.objects.link(q);copied.append((o,q))
    bounds=[max(v.co[k]for v in o.data.vertices)-min(v.co[k]for v in o.data.vertices)for k in range(3)];axis='X' if bounds[0]>bounds[1] else 'Y'
    for j,sl in enumerate(q.material_slots):
     old=sl.material
     if not old or not old.use_nodes or not any(n.type=='EMISSION'for n in old.node_tree.nodes):continue
     m,params=finish(old,axis,seed*109+i*7+j,role);sl.link='OBJECT';sl.material=m
     rows.append({'source':o.name,'private':q.name,'material':m.name,'role':role,'seed':m['244 seed'],'axis':axis,'rain_parameters':params})
   else:out.objects.link(o)
  for child in c.children:out.children.link(child)
  return out
 private=bpy.data.collections.new('244 Right horizontal utility window isolation');private.instance_offset=original.instance_offset;private.use_fake_user=True
 for i,o in enumerate(original.objects):
  if o.instance_collection and ('window_' in o.name):
   q=o.copy();q.name='244 Bank assembly | '+o.name;q.instance_collection=clone(o.instance_collection,24400+i*101);private.objects.link(q);copied.append((o,q));assemblies.append(o.name)
  else:private.objects.link(o)
 for c in original.children:private.children.link(c)
 assert len(assemblies)==10,assemblies
 root.instance_collection=private
 # Preserve collection-based Freestyle semantics of copied paths/leaves exactly.
 for vl in scene.view_layers:
  for ls in vl.freestyle_settings.linesets:
   if not(ls.select_by_collection and ls.collection):continue
   for old,q in copied:
    if old.name in ls.collection.all_objects and q.name not in ls.collection.all_objects:ls.collection.objects.link(q)
 assert all(signature(bpy.data.materials[n])==v for n,v in prior.items()),'Original material edited'
 assert all(tuple(s.material for s in o.material_slots)==v for o,v in bindings.items()),'Original bindings edited'
 assert all(tuple(v for row in o.matrix_world for v in row)==v for o,v in matrices.items()),'Original transforms edited'
 scene['window_bank244_applied']=True;bpy.context.view_layer.update()
 return {'scope':'Only rear-right original right_horizontal_utility 5x2 bank','assemblies':assemblies,'bindings':rows,'new_glass_instances':sum(r['role']=='glass'for r in rows),'new_frame_instances':sum(r['role']=='frame'for r in rows),'original_material_graphs_exact':True,'original_object_material_bindings_exact':True,'warm_building_unchanged':True,'original_transforms_exact':True,'mesh_geometry_shared_exact':all(q.type!='MESH' or q.data==o.data for o,q in copied),'actual_render_review':'Pending parent integration render','approved':False}

if __name__=='__main__':
 O=R/'art/studies/window-bank-244';O.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/footing-243/scene.blend'))
 audit=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print(json.dumps({k:v for k,v in audit.items()if k!='bindings'},indent=2))
