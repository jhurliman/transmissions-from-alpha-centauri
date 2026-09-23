"""User126: double existing inset-platform heights, preserving floor seating and shared warp."""
import bpy,bmesh,math

def apply(C):
 targets=[o for o in C.objects if o.type=='MESH'and o.get('125 inset platform')]
 if len(targets)!=54:raise RuntimeError('Expected54 existing125 platforms')
 if all(o.get('126 doubled platform')for o in targets):return {'already_applied':True}
 if any(o.get('126 doubled platform')for o in targets):raise RuntimeError('Partial126 platform state')
 cache={};rows=[]
 for ob in targets:
  old=ob.data;tier=int(ob['tier']);base=2.73+tier*18.33+.35+(1.25 if tier else 0);before=float(ob['platform authored height']);key=old.as_pointer()
  if key not in cache:
   if abs(min(v.co.z for v in old.vertices)-(base-.035))>1e-4:raise RuntimeError('Unexpected platform floor coordinates '+ob.name)
   me=old.copy();me.name=old.name+'126 double height'
   for v in me.vertices:
    z=v.co.z
    if z<=base:continue
    zz=base+2*(z-base);ratio=(1-.055*zz/78)/(1-.055*z/78);v.co.x*=ratio;v.co.y*=ratio;v.co.z=zz
   me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free()
   if bad or vol<=0:raise RuntimeError('Invalid doubled platform mesh '+ob.name)
   cache[key]=(me,bad,vol)
  me,bad,vol=cache[key];ob.data=me;ob['126 doubled platform']=True;ob['platform authored height']=before*2;ob['platform clear-height ratio']=.10
  actual=max(v.co.z for v in me.vertices)-base
  if abs(actual-before*2)>1e-4:raise RuntimeError('Height mismatch '+ob.name)
  rows.append({'object':ob.name,'tier':tier,'bay':int(ob['bay']),'visible_floor_authored_z':base,'before_height_authored_m':before,'after_height_authored_m':actual,'ratio_before':.05,'ratio_after':.10,'floor_burial_unchanged_m':.035,'nonmanifold_edges':bad,'positive_master_volume':vol,'vertex_count_unchanged':len(me.vertices)==len(old.vertices),'face_count_unchanged':len(me.polygons)==len(old.polygons),'geometry_node_group':next(m.node_group.name for m in ob.modifiers if m.type=='NODES')})
 return {'changed_objects':len(rows),'new_shared_meshes':len(cache),'height_multiplier':2,'cap_fraction_preserved':True,'floor_positions_and_bottom_vertices_unchanged':True,'radial_batter_preserved':True,'existing_material_graphs_unchanged':True,'changes':rows,'order':'Apply to125platforms before126group transforms'}
