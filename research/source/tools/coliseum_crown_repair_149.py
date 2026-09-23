"""Bounded return-only untangling study; fixed front strip, strict acceptance."""
import bpy,json,sys,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology,strict_crossings
from coliseum_arch_ratio_125 import mapping
TARGETS=['COL110 U9 aperture head','COL110 U9 fractured upper wall R']
def repair(o):
 dg=bpy.context.evaluated_depsgraph_get();me=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg);old=o.data;mods=list(o.modifiers);o.data=me
 for m in mods:m.show_viewport=False;m.show_render=False
 _,_,unpack=mapping();coords=[unpack(o.matrix_world@v.co)for v in me.vertices];fixed={i for i,c in enumerate(coords)if c[0]>74.65};src=[v.co.copy()for v in me.vertices];normals=[n.vector.copy()for n in me.corner_normals];neighbors=[set()for _ in me.vertices]
 for e in me.edges:a,b=e.vertices;neighbors[a].add(b);neighbors[b].add(a)
 limit=.32 if 'aperture head' in o.name else .16
 source_material_positions=[tuple(d.vector) for d in me.attributes['115 Original world position'].data]
 before=topology(o);history=[before['strict_crossings']];best=history[0];bestcoords=[v.co.copy()for v in me.vertices]
 for iteration in range(40):
  pairs=strict_crossings(o,True)
  if not pairs:break
  me.calc_loop_triangles();bad=set(v for pair in pairs for i in pair for v in me.loop_triangles[i].vertices)-fixed
  updates={}
  for i in bad:
   avg=sum((me.vertices[k].co for k in neighbors[i]),Vector())/len(neighbors[i]);p=me.vertices[i].co.lerp(avg,.25);delta=o.matrix_world.to_3x3()@(p-src[i])
   if delta.length>limit:p=src[i]+o.matrix_world.to_3x3().inverted()@(delta.normalized()*limit)
   updates[i]=p
  for i,p in updates.items():me.vertices[i].co=p
  me.update();count=strict_crossings(o);history.append(count)
  if count<best:best=count;bestcoords=[v.co.copy()for v in me.vertices]
  if iteration>10 and len(set(history[-8:]))==1:break
 for v,p in zip(me.vertices,bestcoords):v.co=p
 me.update();after=topology(o);moved=[i for i,v in enumerate(me.vertices)if(v.co-src[i]).length>1e-7];d={'object':o.name,'before_evaluated':before,'after_candidate':after,'crossing_history':history,'moved_vertices':len(moved),'max_world_displacement':max(((o.matrix_world.to_3x3()@(me.vertices[i].co-src[i])).length for i in moved),default=0),'fixed_front_vertices':len(fixed),'fixed_front_max_delta':max(((me.vertices[i].co-src[i]).length for i in fixed),default=0),'accepted':after['strict_crossings']==0 and after['nonmanifold']==0}
 if d['accepted']:
  newnorm=[n.vector.copy()for n in me.corner_normals]
  for li,l in enumerate(me.loops):
   if l.vertex_index in fixed:newnorm[li]=normals[li]
  me.normals_split_custom_set(newnorm)
  for m in mods:o.modifiers.remove(m)
  bpy.context.view_layer.update();checkme=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get());checkob=bpy.data.objects.new('149 validation',checkme);checkob.matrix_world=o.matrix_world;d['after_evaluated']=topology(checkob);bpy.data.objects.remove(checkob);bpy.data.meshes.remove(checkme)
  d['material_coordinate_change']=max((Vector(a)-d.vector).length for a,d in zip(source_material_positions,me.attributes['115 Original world position'].data));d['front_normals']='Exact evaluated source corner normals retained on fixed front strip';d['raw_topology_after']=topology(o)
 else:
  o.data=old
  for m in mods:m.show_viewport=True;m.show_render=True
 return d

def apply(C):
 return {'targets':[repair(next(o for o in C.objects if o.name==name))for name in TARGETS],'method':'Bounded smoothing of crossing return vertices only; front radial strip fixed; reject nonzero crossings.'}
if __name__=='__main__':
 O=R/'art/studies/coliseum-149/repair';O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-148/scene.blend'));C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library);d=apply(C);(O/'untangle-audit.json').write_text(json.dumps(d,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'));print('RESULT',json.dumps(d))
