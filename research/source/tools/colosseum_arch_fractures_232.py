"""232 native subtractive arch fractures. Applies LAST, preserving current GP visibility."""
import bpy,bmesh,math,json,time,struct,types
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
from coliseum_crown_continuation_154 import freeze_render_triangles,robust_crossings
from coliseum_contact_clip_169 import snapshot,digest,interpolate,run
R=Path(__file__).resolve().parents[1]

# Native camera coordinates locate the requested construction details; the
# resulting cut solids are ordinary editable world-space meshes, never shaders.
SPECS=[{'anchor': [2062, 280],
  'bay': None,
  'id': 'crown-trim',
  'paths': [([[2061.0, 269], [2061.6, 275], [2060.9, 280], [2062.2, 287], [2063, 293]], [1.5, 2.5, 2.0, 1.8, 0.7], 6.0)]},
 {'anchor': [1627, 477],
  'bay': 6,
  'id': 'left-branch',
  'paths': [([[1628, 487], [1627, 477], [1630, 468], [1626, 461], [1628, 449]], [1.6, 2.5, 2.8, 2.0, 0.8], 4.5),
            ([[1629, 469], [1619, 466], [1615, 457]], [1.9, 1.3, 0.35], 2.5)]},
 {'anchor': [1963, 464],
  'bay': 8,
  'id': 'central-open',
  'paths': [([[1961, 481], [1965, 472], [1961, 463], [1967, 455], [1964, 447], [1968, 435]],
             [3.5, 5.2, 7.0, 5.4, 4.1, 1.8],
             32.0),
            ([[1962, 463], [1949, 460], [1942, 453], [1934, 450]], [3.2, 4.8, 2.7, 0.6], 7.0),
            ([[1965, 470], [1980, 478], [1989, 478], [1999, 489]], [2.7, 4.0, 2.3, 0.5], 6.0)]},
 {'anchor': [2109, 477],
  'bay': 9,
  'id': 'right-branch',
  'paths': [([[2108, 490], [2110, 482], [2106, 475], [2112, 467], [2108, 460], [2109, 452]], [1.2, 2.5, 3.1, 2.0, 1.9, 0.5], 4.5),
            ([[2106, 475], [2096, 473], [2091, 467]], [2.1, 1.5, 0.35], 2.8)]}]

def mesh_tree(me,M):
 me.calc_loop_triangles();return BVHTree.FromPolygons([M@v.co for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True)
def bbox(vs):return [(min(p[k]for p in vs),max(p[k]for p in vs))for k in range(3)]
def overlaps(a,b):return all(x1>=y0-1e-5 and y1>=x0-1e-5 for(x0,x1),(y0,y1)in zip(a,b))
def health(me):
 bm=bmesh.new();bm.from_mesh(me);out={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume_local':abs(bm.calc_volume()),'vertices':len(me.vertices),'faces':len(me.polygons)};bm.free();return out

def cutters(scene,C):
 cam=scene.camera;origin=cam.matrix_world.translation.copy();rot=cam.matrix_world.to_3x3();frame=cam.data.view_frame(scene=scene);lx=min(v.x for v in frame);hx=max(v.x for v in frame);ly=min(v.y for v in frame);hy=max(v.y for v in frame);z=frame[0].z;dg=bpy.context.evaluated_depsgraph_get();result=[]
 def ray(pixel):return(rot@Vector((lx+(hx-lx)*pixel[0]/3840,hy-(hy-ly)*pixel[1]/2885,z))).normalized()
 for spec in SPECS:
  obs=[C.objects['COL121 bay9 field0 upper course']]if spec['bay']is None else[o for o in C.objects if o.get('tier')==2 and o.get('bay')==spec['bay']and o.get('coliseum_role')=='arch_molding'and not o.hide_render]
  vv=[];ff=[]
  for ob in obs:
   ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();off=len(vv);vv.extend(ev.matrix_world@v.co for v in me.vertices);ff.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);ev.to_mesh_clear()
  tree=BVHTree.FromPolygons(vv,ff,all_triangles=True);hit=tree.ray_cast(origin,ray(spec['anchor']),1000);assert hit[0]is not None,(spec['id'],'anchor missed')
  center=hit[0];normal=hit[1].normalized()
  if spec['bay']is not None:
   wall=C.objects['COL127 T2 continuous arcade wall'];ev=wall.evaluated_get(dg);wm=ev.to_mesh();wt=mesh_tree(wm,ev.matrix_world);wh=wt.ray_cast(origin,ray(spec['paths'][0][0][-1]),1000);ev.to_mesh_clear()
   if wh[0]is not None and abs(wh[1].z)<.3:normal=wh[1].normalized()
   else:normal=(origin-center).normalized()
  # Fractures advance inward through the vertical facade, not down a bevel.
  normal.z=0;normal.normalize()
  if normal.dot(origin-center)<0:normal=-normal
  # The actual stone front face defines a physically fixed construction plane.
  def point(px):
   d=ray(px);return origin+d*((center-origin).dot(normal)/d.dot(normal))
  for pi,(path,widths,depth)in enumerate(spec['paths']):
   pts=[]
   for i,p in enumerate(path):
    before=Vector(path[max(0,i-1)]);after=Vector(path[min(len(path)-1,i+1)]);d=(after-before).normalized();side=Vector((-d.y,d.x));pts.append((Vector(p)+side*widths[i]/2,Vector(p)-side*widths[i]/2))
   poly=[x[0]for x in pts]+[x[1]for x in pts[::-1]];N=len(poly);vs=[point(p)+normal*dd for dd in(1.8,-depth)for p in poly];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
   me=bpy.data.meshes.new('232 negative solid '+spec['id']+str(pi));me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(me);bm.free();me.update()
   result.append({'id':spec['id']+str(pi),'bay':spec['bay'],'mesh':me,'tree':mesh_tree(me,VectorMatrix()),'box':bbox(vs),'vertices':[list(v)for v in vs],'faces':[list(p.vertices)for p in me.polygons],'path_native_4k':path,'widths_native_4k':widths,'inward_depth_m':depth,'inward_direction_world':list(-normal)})
 return result

def VectorMatrix():
 from mathutils import Matrix
 return Matrix.Identity(4)

def subtract(ob,cuts,C,src,M):
 src=freeze_render_triangles(src);iv=M.inverted();src.calc_loop_triangles();verts=[v.co.copy()for v in src.vertices];tri=[tuple(t.vertices)for t in src.loop_triangles];tree=BVHTree.FromPolygons(verts,tri,all_triangles=True);keys={tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices)):p.index for p in src.polygons};norms={(key,tuple(src.vertices[src.loops[li].vertex_index].co)):src.corner_normals[li].vector.copy()for key,pi in keys.items()for li in src.polygons[pi].loop_indices};coords={tuple(v):i for i,v in enumerate(verts)};before=health(src)
 tmp=bpy.data.objects.new('232 temporary working solid',src.copy());C.objects.link(tmp);ctrees=[];used=[]
 for cut in cuts:
  cm=cut['mesh'].copy();cm.transform(iv);co=bpy.data.objects.new('232 temporary fracture cutter',cm);C.objects.link(co);ctrees.append(mesh_tree(cm,VectorMatrix()));mod=tmp.modifiers.new('232 Physical fracture DIFFERENCE','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True);used.append(cut['id'])
 me=tmp.data;me.update();after=health(me);removed=(before['volume_local']-after['volume_local'])*abs(M.to_3x3().determinant())
 if removed<1e-7:
  bpy.data.objects.remove(tmp,do_unlink=True);return None
 # Only new cut-face ngons are retessellated; source render triangles stay exact.
 ng=[p.index for p in me.polygons if len(p.vertices)>4 and tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices))not in keys]
 if ng:
  bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bmesh.ops.triangulate(bm,faces=[bm.faces[i]for i in ng],ngon_method='BEAUTY');bm.to_mesh(me);bm.free();me.update()
 after=health(me);assert after['nonmanifold']<=before['nonmanifold'],(ob.name,'new nonmanifold',before,after)
 if not me.vertices:raise RuntimeError('Entire source stone removed: '+ob.name)
 core=bpy.data.materials.get('165 Existing light on exposed masonry core')or bpy.data.materials['151 Warm violet exposed masonry core'];me.materials.append(core);slot=len(me.materials)-1;tag=me.attributes.get('232 Exposed fracture interior')or me.attributes.new('232 Exposed fracture interior','FLOAT','FACE');srcpos=src.attributes.get('115 Original world position');pa=me.attributes.get('115 Original world position');custom=[n.vector.copy()for n in me.corner_normals];corecount=0
 if srcpos and pa:
  for v in me.vertices:
   if tuple(v.co)in coords:pa.data[v.index].vector=srcpos.data[coords[tuple(v.co)]].vector
   else:
    h=tree.find_nearest(v.co);ids=tri[h[2]];pa.data[v.index].vector=geometry.barycentric_transform(h[0],*[verts[i]for i in ids],*[srcpos.data[i].vector for i in ids])
 newkeys={tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices)):p.index for p in me.polygons}
 for p in me.polygons:
  key=tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices));h=tree.find_nearest(p.center);iscore=h[3]>1e-4 and min(t.find_nearest(p.center)[3]for t in ctrees)<.0003;tag.data[p.index].value=float(iscore)
  if iscore:p.material_index=slot;corecount+=1
  elif h[3]<.001:p.material_index=src.polygons[src.loop_triangles[h[2]].polygon_index].material_index
  for li in p.loop_indices:
   xyz=tuple(me.vertices[me.loops[li].vertex_index].co)
   if(key,xyz)in norms:custom[li]=norms[(key,xyz)]
   elif iscore:custom[li]=p.normal.copy()
   else:
    hh=tree.find_nearest(Vector(xyz));tr=src.loop_triangles[hh[2]];custom[li]=geometry.barycentric_transform(hh[0],*[verts[i]for i in tr.vertices],*[src.corner_normals[k].vector for k in tr.loops]).normalized()
 for attr in src.attributes:
  if attr.name.startswith('.')or attr.name in {'position','custom_normal','sharp_edge'}:continue
  dst=me.attributes.get(attr.name)
  prop=next((q for q in ['vector','color','value']if len(attr.data)and hasattr(attr.data[0],q)),None)
  if not dst or not prop:continue
  if attr.domain=='POINT':
   for v in me.vertices:
    if tuple(v.co)in coords:setattr(dst.data[v.index],prop,getattr(attr.data[coords[tuple(v.co)]],prop))
  elif attr.domain=='FACE':
   for key,i in newkeys.items():
    if key in keys:setattr(dst.data[i],prop,getattr(attr.data[keys[key]],prop))
 me.normals_split_custom_set(custom)
 # Bool subtraction may split a stone into islands; each remains a closed solid.
 # Verify that every source triangle outside all cutter boxes survives exactly.
 protected=[key for key in keys if not any(overlaps(bbox([M@Vector(v)for v in key]),c['box'])for c in cuts)]
 missing=[key for key in protected if key not in newkeys];assert not missing,(ob.name,'lost protected triangles',len(missing))
 def pairs(mesh):
  mesh.calc_loop_triangles();return {tuple(sorted(tuple(sorted(tuple(mesh.vertices[v].co)for v in mesh.loop_triangles[i].vertices))for i in pair))for pair in robust_crossings(types.SimpleNamespace(data=mesh,matrix_world=M))}
 oldpairs=pairs(src);newpairs=pairs(me);extra=newpairs-oldpairs;assert not extra,(ob.name,'new physical crossings',len(extra))
 # Mark just boundary edges between newly exposed core and old masonry.
 bm=bmesh.new();bm.from_mesh(me);bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table();marks=[]
 for e in bm.edges:
  if len(e.link_faces)==2 and (e.link_faces[0].material_index==slot)!=(e.link_faces[1].material_index==slot):marks.append(e.index)
 bm.free()
 edgeattr=me.attributes.get('freestyle_edge')or me.attributes.new('freestyle_edge','BOOLEAN','EDGE');inherited_marks=sum(d.value for d in edgeattr.data)
 for i in marks:edgeattr.data[i].value=True
 faceattr=me.attributes.get('freestyle_face')or me.attributes.new('freestyle_face','BOOLEAN','FACE')
 for p in me.polygons:faceattr.data[p.index].value=(p.material_index==slot)
 row={'protected_triangles_exact':len(protected),'missing_protected_triangles':0,'new_crossing_pairs':0,'inherited_crossing_pairs':len(oldpairs),'inherited_marked_edges':inherited_marks,'new_fracture_boundary_edges':len(marks),'object':ob.name,'cutters':used,'before':before,'after':after,'removed_volume_world_m3':removed,'new_core_faces':corecount,'retained_exact_source_triangles':len(keys.keys()&newkeys.keys()),'source_triangles':len(keys),'new_ngons_triangulated':len(ng)}
 oldworld=[M@v for v in verts];oldtree=BVHTree.FromPolygons(oldworld,tri,all_triangles=True)
 src.use_fake_user=True;src.name='232 SOURCE '+ob.name;me.name='232 fractured '+ob.name;ob.data=me
 for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 for sl in ob.material_slots:sl.link='DATA'
 ob['232 native fracture']=used;bpy.data.objects.remove(tmp,do_unlink=True)
 return row,(oldtree,mesh_tree(me,M),bbox(oldworld))

def clip_contacts(scene,owners,cuts):
 gp=scene.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy();changes=[]
 def unsupported(p):
  for before,after,box in owners:
   if all(a-.02<=p[k]<=b+.02 for k,(a,b)in enumerate(box))and before.find_nearest(p)[3]<.018 and after.find_nearest(p)[3]>.022:return True
  return False
 for rec in old:
  for si,st in enumerate(rec['strokes']):
   vv=[M@Vector(p)for p in st['point']['position']]
   if len(vv)<2 or not any(overlaps(bbox(vv),o[2])for o in owners):continue
   ts=[0.]
   for i,(a,b)in enumerate(zip(vv,vv[1:])):
    if not any(overlaps(bbox([a,b]),c['box'])for c in cuts):ts.append(float(i+1));continue
    n=max(1,math.ceil((a-b).length/.015));ts.extend(i+j/n for j in range(1,n+1))
   def state(t):return unsupported(M@Vector(interpolate(st,t)['position']))
   status=[state(t)for t in ts]
   if not any(status):continue
   assert not st['curve'].get('cyclic',False),'232 cyclic cut contacts require explicit run handling'
   removed=[];start=0. if status[0]else None
   for i in range(1,len(ts)):
    if status[i]==status[i-1]:continue
    a,b=ts[i-1],ts[i]
    for _ in range(20):
     mid=(a+b)/2
     if state(mid)==status[i-1]:a=mid
     else:b=mid
    edge=(a+b)/2
    if status[i]:start=edge
    else:removed.append([start,edge]);start=None
   if start is not None:removed.append([start,float(len(vv)-1)])
   kept=[];p=0.
   for a,b in removed:
    if a-p>1e-7:kept.append([p,a])
    p=b
   if len(vv)-1-p>1e-7:kept.append([p,float(len(vv)-1)])
   changes.append({'layer':rec['layer'],'frame':rec['frame'],'stroke':si,'removed':removed,'runs':[run(st,a,b)for a,b in kept]})
 if not changes:return {'changed_strokes':0,'unaffected_attributes_exact':True,'restored_external_clips':False}
 gp.data=gp.data.copy();gp.data.name='232 Only newly unsupported fracture contacts clipped'
 for rec in old:
  edits=[r for r in changes if r['layer']==rec['layer']and r['frame']==rec['frame']]
  if not edits:continue
  dr=gp.data.layers[rec['layer']].frames[rec['frame']].drawing;ids=sorted(r['stroke']for r in edits);dr.remove_strokes(indices=ids);off=sum(len(st.points)for st in dr.strokes);coff=len(dr.strokes);runs=[st for r in edits for st in r['runs']]
  if runs:
   dr.add_strokes(sizes=[len(st['point']['position'])for st in runs])
   for j,st in enumerate(runs):
    for k,vals in st['point'].items():
     for i,v in enumerate(vals):setattr(dr.attributes[k].data[off+i],rec['schema'][k]['prop'],v)
    for k,v in st['curve'].items():setattr(dr.attributes[k].data[coff+j],rec['schema'][k]['prop'],v)
    off+=len(st['point']['position'])
 after=snapshot(gp)
 for rec in old:
  ids={r['stroke']for r in changes if r['layer']==rec['layer']and r['frame']==rec['frame']};expected=[st for i,st in enumerate(rec['strokes'])if i not in ids];actual=next(r for r in after if r['layer']==rec['layer']and r['frame']==rec['frame'])['strokes'];assert actual[:len(expected)]==expected
 return {'changed_strokes':len(changes),'removed_intervals':sum(len(r['removed'])for r in changes),'unaffected_attributes_exact':True,'restored_external_clips':False,'source_digest':digest(old),'result_digest':digest(after),'old_owner_max_distance_m':.018,'new_owner_min_distance_m':.022,'world_sample_spacing_m':.015,'changes':[{k:v for k,v in r.items()if k!='runs'}for r in changes]}

def apply(scene):
 assert not scene.get('arch_fractures232_applied');C=bpy.data.collections['110 Coliseum detailed front ruin'];cuts=cutters(scene,C);dg=bpy.context.evaluated_depsgraph_get();todo=[]
 for ob in list(C.objects):
  if ob.type!='MESH'or ob.hide_render:continue
  eligible=ob.name=='COL121 bay9 field0 upper course'or ob.name=='COL127 T2 continuous arcade wall'or ob.get('tier')==2 and ob.get('bay')in(6,8,9)and ob.get('coliseum_role')in('arch_molding','band','pier')
  if not eligible:continue
  ev=ob.evaluated_get(dg);box=bbox([ev.matrix_world@Vector(v)for v in ev.bound_box]);cc=[c for c in cuts if (c['bay']is None)==(ob.name=='COL121 bay9 field0 upper course')and(c['bay']==ob.get('bay')or'continuous arcade'in ob.name or c['bay']is None)and overlaps(box,c['box'])]
  if cc:todo.append((ob,cc))
 prepared=[(ob,cc,bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg),ob.matrix_world.copy())for ob,cc in todo]
 print('232 PREPARED',len(prepared),flush=True)
 work=bpy.data.scenes.new('232 isolated Boolean workspace');workC=bpy.data.collections.new('232 temporary solids');work.collection.children.link(workC);bpy.context.window.scene=work
 rows=[];owners=[]
 try:
  for ob,cc,src,M in prepared:
   print('232 CUT',ob.name,[c['id']for c in cc],flush=True);result=subtract(ob,cc,workC,src,M)
   if result:row,owner=result;rows.append(row);owners.append(owner);print('232 RESULT',row,flush=True)
 finally:
  bpy.context.window.scene=scene;bpy.data.scenes.remove(work);bpy.data.collections.remove(workC)
 assert any(r['object']=='COL121 bay9 field0 upper course'for r in rows),'Crown trim not cut'
 for bay in(6,8,9):assert any(f'B{bay:02d} archivolt'in r['object']for r in rows),bay
 ink=clip_contacts(scene,owners,cuts)
 inkC=bpy.data.collections.new('232 New physical fracture boundaries');inkC.use_fake_user=True
 for row in rows:inkC.objects.link(bpy.data.objects[row['object']])
 vl=scene.view_layers['215 Distant ink without atmospheric boundary'];fs=vl.freestyle_settings;source=fs.linesets['215 Distant component architecture'];ls=fs.linesets.new('232 New exposed masonry fracture edges');ls.linestyle=source.linestyle.copy();ls.linestyle.name='232 Fine native cut boundaries';ls.linestyle.thickness=.7;ls.linestyle.color=(.10,.075,.10);ls.select_by_collection=True;ls.collection=inkC;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_by_edge_types=True
 for prop in ['select_silhouette','select_border','select_crease','select_ridge_valley','select_suggestive_contour','select_material_boundary','select_contour','select_external_contour']:setattr(ls,prop,False)
 ls.select_edge_mark=True;ls.edge_type_combination='OR';ls.select_by_face_marks=True;ls.face_mark_condition='ONE';ls.face_mark_negation='INCLUSIVE';scene['arch_fractures232_applied']=True
 return {'source':'231','targets':rows,'changed_objects':len(rows),'cutters':[{k:v for k,v in c.items()if k not in('mesh','tree')}for c in cuts],'contact_cleanup':ink,'new_material_graphs':0,'new_overlay_geometry':0,'changed_ornaments':[r['object']for r in rows if r['object'].startswith('COL231')],'native_ink':'232 New exposed masonry fracture edges in existing215 atmosphere-free viewlayer; marked actual cut boundaries only; no callback required','crown_crop_4k':[2015,210,2130,355],'arch_crop_4k':[1530,410,2340,720],'status':'CPU candidate; actual native visual proof pending'}
