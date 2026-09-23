"""134 bounded layered native fracture cap. UCL01/UCL02/DP03.
One existing exposed crown only; connected height-field topology, no pasted fragments.
"""
import bpy,bmesh,math,random,time,json
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology,strict_crossings
TARGET='COL110 U9 fractured upper wall L'
def evaluated_topology(ob,unpack=None):
 dg=bpy.context.evaluated_depsgraph_get();e=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(e,depsgraph=dg);tmp=bpy.data.objects.new('134 evaluated validation',me);tmp.matrix_world=e.matrix_world;d=topology(tmp);
 if d['strict_crossings']:
  pairs=strict_crossings(tmp,True);me.calc_loop_triangles();rows=[{'pair':p,'vertices':[[list(tmp.matrix_world@me.vertices[i].co)for i in me.loop_triangles[k].vertices]for k in p],'faces':[me.loop_triangles[k].polygon_index for k in p],'raw':[[list(unpack(ob.matrix_world@ob.data.vertices[i].co))if unpack else list(ob.data.vertices[i].co)for i in me.loop_triangles[k].vertices]for k in p]}for p in pairs];(Path(__file__).resolve().parents[1]/'art/studies/coliseum-134/fracture/evaluated-rejected.json').write_text(json.dumps(rows,indent=2))
 bpy.data.objects.remove(tmp);bpy.data.meshes.remove(me);return d

def apply(C):
 start=time.time();ob=next(o for o in C.objects if o.name==TARGET);source_data=ob.data;evaluated_before=evaluated_topology(ob);dg=bpy.context.evaluated_depsgraph_get();ev=ob.evaluated_get(dg);baked=bpy.data.meshes.new_from_object(ev,depsgraph=dg);old_mods=list(ob.modifiers);modflags=[(m,m.show_viewport,m.show_render)for m in old_mods];ob.data=baked
 for m in old_mods:m.show_viewport=False;m.show_render=False
 bpy.context.view_layer.update();old=ob.data;before=topology(ob);original,world,unpack=mapping();iv=ob.matrix_world.inverted();ac=-math.pi+9.5*math.tau/36
 coords=[unpack(ob.matrix_world@v.co)for v in old.vertices]
 eligible=[f for f in old.polygons if len(f.vertices)>6 and max(coords[i][2]for i in f.vertices)-min(coords[i][2]for i in f.vertices)<.005 and min(coords[i][2]for i in f.vertices)>73 and max(coords[i][0]for i in f.vertices)-min(coords[i][0]for i in f.vertices)>7]
 if len(eligible)!=1:raise RuntimeError('Unexpected existing crown topology')
 f=eligible[0];amin=min(coords[i][1]for i in f.vertices);amax=max(coords[i][1]for i in f.vertices)
 def local_u(a):return -6.5456+(a-amin)/(amax-amin)*5.49785
 cap_indices=set(f.vertices);original_coords=[v.co.copy()for v in old.vertices]
 old_positions={tuple(round(x,6)for x in v.co)for v in old.vertices};old_normal_faces={tuple(sorted(tuple(round(x,6)for x in old.vertices[i].co)for i in p.vertices)):[old.corner_normals[j].vector.copy()for j in p.loop_indices]for p in old.polygons}
 bm=bmesh.new();bm.from_mesh(old);bm.faces.ensure_lookup_table();layer=bm.faces.layers.int.new('134 fracture cap');bm.faces.ensure_lookup_table();cap=bm.faces[f.index];cap[layer]=1
 # Split a narrow upper strip before withdrawing the broken front edge; lower wall stays exact.
 po=world(75,ac,72.10);wn=(world(76,ac,72.10)-po).cross(world(75,ac+.001,72.10)-po).normalized();ln=(ob.matrix_world.to_3x3().transposed()@wn).normalized()
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.000001,plane_co=iv@po,plane_no=ln,clear_inner=False,clear_outer=False)
 cap=next(q for q in bm.faces if q[layer])
 bmesh.ops.triangulate(bm,faces=[cap],quad_method='BEAUTY',ngon_method='BEAUTY');selected=[q for q in bm.faces if q[layer]];edges=list({e for q in selected for e in q.edges});bmesh.ops.subdivide_edges(bm,edges=edges,cuts=5,use_grid_fill=True)
 selected=[q for q in bm.faces if q[layer]];vertices={v for q in selected for v in q.verts};capverts=set(vertices);vertices.update(v for v in bm.verts if unpack(ob.matrix_world@v.co)[2]>72.099);changed=[]
 def smooth(a,b,x):
  t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
 for v in vertices:
  r,a,z=unpack(ob.matrix_world@v.co);u=local_u(a)
  # End interfaces remain exact; the three depth courses share every boundary vertex.
  end=smooth(-6.545,-5.98,u)*(1-smooth(-1.62,-1.047,u));end*=1-smooth(-4.95,-4.70,u)*(1-smooth(-3.60,-3.35,u))
  if end<1e-6:continue
  offset=.11*math.sin(u*2.7)+.06*math.sin(u*6.9)
  rr=r+offset
  drop=.18+.68*(1-smooth(72.9,73.55,rr))-.43*(1-smooth(69.8,70.4,rr))
  # Irregular short facets interrupt long planes; no displacement of intact wall interiors.
  grain=.052*math.sin(u*13.4+r*7.1)+.034*math.sin(u*23.7-r*5.4)
  drop=max(.045,drop+.06*math.sin(u*1.7)+grain)*end if v in capverts else 0.
  inset=(.61+.10*math.sin(u*4.2)+.05*math.sin(u*12.3))*end*smooth(72.10,73.20,z)*smooth(73.75,75.,r)
  v.co=iv@world(r-inset,a,z-drop);changed.append({'original':list(original(r,a,z)),'new_original':list(original(r,a,z-drop)),'drop_m':drop})
 for q in bm.faces:
  ps=[unpack(ob.matrix_world@v.co)for v in q.verts]
  if min(p[2]for p in ps)>72.08 and any(73.9<p[0]<74.9 for p in ps):q[layer]=1
 bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method='BEAUTY',ngon_method='BEAUTY');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));me=old.copy();me.name=old.name+' layered crown134';bm.to_mesh(me);bm.free();ob.data=me;me.update()
 attr=me.attributes.get('115 Original world position')or me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
 # BMesh interpolates the existing attached original-position attribute onto new vertices.
 core=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');mask=me.attributes['134 fracture cap'];core_slot=next((i for i,s in enumerate(ob.material_slots)if s.material and ('Exposed masonry core'in s.material.name or s.material.get('role')=='fracture')),None)
 if core_slot is None:
  # No guessed relabel of existing facades; reuse this actual cap's existing masonry material.
  core_slot=f.material_index
 for p in me.polygons:
  if mask.data[p.index].value:p.material_index=core_slot;core.data[p.index].value=1.;p.use_smooth=False
 # Interpolate the existing split normals only on unchanged/front/back planes.
 old.calc_loop_triangles();ts=list(old.loop_triangles);vs=[v.co.copy()for v in old.vertices];tree=BVHTree.FromPolygons(vs,[tuple(t.vertices)for t in ts],all_triangles=True);cn=[q.vector.copy()for q in old.corner_normals];normals=[q.vector.copy()for q in me.corner_normals];restored=0
 for p in me.polygons:
  if mask.data[p.index].value:continue
  for li in p.loop_indices:
   pos=me.vertices[me.loops[li].vertex_index].co;hit=tree.find_nearest(pos)
   if hit[3]>.001:continue
   t=ts[hit[2]];norm=geometry.barycentric_transform(hit[0],*[vs[i]for i in t.vertices],*[cn[i]for i in t.loops]);normals[li]=norm.normalized();restored+=1
 me.normals_split_custom_set(normals)
 after=topology(ob);bpy.context.view_layer.update();evaluated_after=evaluated_topology(ob,unpack)
 if evaluated_after['strict_crossings']>evaluated_before['strict_crossings']:ob.data=old;raise RuntimeError('Evaluated crossing increase '+str(evaluated_after))
 if after['nonmanifold']or after['strict_crossings']>before['strict_crossings']or after['volume']<=0:
  pairs=strict_crossings(ob,True);me.calc_loop_triangles();diagnostic=[{'pair':pair,'coords':[[list(unpack(ob.matrix_world@me.vertices[i].co))for i in me.loop_triangles[k].vertices]for k in pair],'faces':[me.loop_triangles[k].polygon_index for k in pair]}for pair in pairs];(Path(__file__).resolve().parents[1]/'art/studies/coliseum-134/fracture/rejected-crossings.json').write_text(json.dumps(diagnostic,indent=2));ob.data=old;raise RuntimeError('Rejected topology '+str(after))
 unchanged_old=sum(tuple(round(x,6)for x in v.co)in {tuple(round(x,6)for x in q.co)for q in me.vertices}for v in old.vertices)
 for m in old_mods:ob.modifiers.remove(m)
 ob['134 damage feature']='Three connected course-depth offsets on existing U9L crown cap';ob['damage_region']='134 U9L crown only'
 return {'target':ob.name,'layout_materialized_for_target_only':['127 Equal edge-clearance layout'],'original_source_mesh':source_data.name,'references':['UCL-01','UCL-02','DP-03'],'before':before,'after':after,'evaluated_before':evaluated_before,'evaluated_after':evaluated_after,'source_cap_face':f.index,'cap_faces':sum(bool(d.value)for d in mask.data),'moved_cap_vertices':len(changed),'maximum_drop_authored_m':max(x['drop_m']for x in changed),'unchanged_original_vertices':unchanged_old,'original_vertices':len(old.vertices),'new_detached_objects':0,'scope':'Existing exposed cap and immediate shared crown edge only; exact end interfaces, all other objects unchanged. No old wall import, hole, pose or arch change.','normals':{'new_cap':'Actual flat fracture normals','retained_noncap_corner_normals':restored},'seconds':time.time()-start}
