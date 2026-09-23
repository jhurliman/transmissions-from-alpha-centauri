"""One isolated connected Tower7 facing/course loss. No primary writes."""
import bpy,bmesh,sys,json,types,time
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_crown_continuation_154 import robust_crossings,freeze_render_triangles
O=R/'art/studies/coliseum-167/geometry'
PROFILE=[(-13.25,44.1),(-11.85,44.1),(-11.82,42.8),(-10.75,42.78),(-10.72,41.75),(-10.3,41.65),(-10.55,40.3),(-11.25,40.2),(-11.4,38.8),(-11.9,38.55),(-12.1,36.7),(-12.8,36.8),(-12.95,38.0),(-13.25,39.0)]
def health(me,M):
 bm=bmesh.new();bm.from_mesh(me);pending=set(bm.verts);components=0
 while pending:
  components+=1;todo=[pending.pop()]
  while todo:
   v=todo.pop()
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in pending:pending.remove(w);todo.append(w)
 d={'nonmanifold':sum(not e.is_manifold for e in bm.edges),'zero_faces':sum(f.calc_area()<1e-10 for f in bm.faces),'components':components,'volume':abs(bm.calc_volume())*abs(M.to_3x3().determinant()),'crossings':len(robust_crossings(types.SimpleNamespace(data=me,matrix_world=M)))};bm.free();return d

def apply(C):
 start=time.time();dg=bpy.context.evaluated_depsgraph_get();rows=[];payload=[];
 core=bpy.data.materials.get('165 Existing light on exposed masonry core')
 if core is None:
  with bpy.data.libraries.load(str(R/'art/studies/coliseum-166/scene.blend'),link=False)as(lib,dst):
   core_name=next(n for n in lib.materials if n.startswith('165 Existing light on exposed masonry core'));dst.materials=[core_name]
  core=dst.materials[0]
 assert core is not None and not core.library
 removals=[]
 names=['COL127 T2 continuous arcade wall','COL110 U7 sill wall']+[f'COL110 T2 band07 profile{i}'for i in range(4)]+[f'COL111 Tower7 tier2 stepped belt{i}'for i in range(5)]+['COL111 Tower7 tier2 rib shoulder1','COL111 Tower7 tier2 projecting shaft rib1']
 names += [o.name for o in C.objects if o.name.startswith('COL120 bay7 ')and ('arcade2 dentil'in o.name or 'Tower7 tier2'in o.name)]
 for name in names:
  ob=C.objects.get(name)
  if not ob:continue
  ev=ob.evaluated_get(dg);src=bpy.data.meshes.new_from_object(ev,depsgraph=dg);M=ob.matrix_world.copy();iv=M.inverted();world=[M@v.co for v in src.vertices]
  profile=PROFILE
  isrib=name in ['COL111 Tower7 tier2 rib shoulder1','COL111 Tower7 tier2 projecting shaft rib1']
  if isrib:profile=[(-14.,38.2),(-12.,38.2),(-12.,40.),(-14.,40.)]
  elif name=='COL111 Tower7 tier2 stepped belt2':profile=[(-10.+.75*(x+10.),z)for x,z in PROFILE]
  xmin=min(x for x,z in profile);xmax=max(x for x,z in profile);zmin=min(z for x,z in profile);zmax=max(z for x,z in profile)
  if not world or max(v.x for v in world)<xmin or min(v.x for v in world)>xmax or max(v.z for v in world)<zmin or min(v.z for v in world)>zmax or min(v.y for v in world)>199.4:continue
  before=health(src,M);row={'object':name,'before':before};rows.append(row)
  if before['crossings']or before['nonmanifold']or before['zero_faces']:row['held']='Inherited source fails topology gate';continue
  # Work in target LOCAL space at identity to avoid matrix shear decomposition.
  src=freeze_render_triangles(src);src.calc_loop_triangles();tris=[tuple(t.vertices)for t in src.loop_triangles];srcverts=[v.co.copy()for v in src.vertices];tree=BVHTree.FromPolygons(srcverts,tris,all_triangles=True);oldpos=[v.vector.copy()for v in src.attributes['115 Original world position'].data]if src.attributes.get('115 Original world position')else None
  normals={(tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices)),tuple(src.vertices[src.loops[k].vertex_index].co)):src.corner_normals[k].vector.copy()for p in src.polygons for k in p.loop_indices};oldkeys={tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices))for p in src.polygons};oldcoords={tuple(v.co):v.index for v in src.vertices}
  tmp=bpy.data.objects.new('167 temporary '+name,src.copy());C.objects.link(tmp)
  levels=[(175.,1.),(198.6,1.)]if isrib else[(175.,1.),(188.8,1.),(188.8,.90),(194.,.90),(194.,.80),(198.6,.80)]
  cx=sum(x for x,z in profile)/len(profile);cz=sum(z for x,z in profile)/len(profile)
  vv=[iv@Vector((cx+(x-cx)*scale,yy,cz+(z-cz)*scale))for yy,scale in levels for x,z in profile];n=len(profile);ff=[tuple(range(n-1,-1,-1)),tuple(range((len(levels)-1)*n,len(levels)*n))]
  for j in range(len(levels)-1):ff.extend((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)for i in range(n))
  cm=bpy.data.meshes.new('167 connected facing cutter');cm.from_pydata(vv,[],ff);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();co=bpy.data.objects.new('167 cutter',cm);C.objects.link(co)
  mod=tmp.modifiers.new('167 bounded missing masonry facing','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;bpy.ops.object.modifier_apply(modifier=mod.name);cuttertree=BVHTree.FromPolygons([v.co.copy()for v in cm.vertices],[tuple(p.vertices)for p in cm.polygons]);bpy.data.objects.remove(co,do_unlink=True);me=tmp.data;me.update()
  if not len(me.vertices):
   def inside(p):
    hit=False
    for j,(x,z)in enumerate(profile):
     xx,zz=profile[j-1]
     if (z>p.z)!=(zz>p.z)and p.x<(xx-x)*(p.z-z)/(zz-z)+x:hit=not hit
    return hit and 175<p.y<198.6
   contained=all(inside(p)for p in world);row.update(removed_entire=True,all_source_vertices_inside_negative_volume=contained,source_vertices=len(world),removed_volume_m3=before['volume'])
   if contained and (name.startswith('COL120 bay7 ')or name=='COL111 Tower7 tier2 rib shoulder1'):removals.append(ob);row['disposition']='Entire dentil lies within the same removed masonry volume; remove rather than leave floating decoration.'
   else:row['held']='Whole component removal not certified as scoped dentil loss'
   bpy.data.objects.remove(tmp,do_unlink=True);continue
  after=health(me,M);row['after']=after;row['removed_volume_m3']=before['volume']-after['volume']
  if after['crossings']or after['nonmanifold']or after['zero_faces']or after['components']>before['components']or after['volume']>before['volume']+1e-6:
   row['held']='Candidate topology/closed-component/subtractive-volume gate failed';bpy.data.objects.remove(tmp,do_unlink=True);continue
  if row['removed_volume_m3']<1e-7:row['unchanged']=True;bpy.data.objects.remove(tmp,do_unlink=True);continue
  # Keep exact coordinates/attributes on retained vertices; interpolate only new cuts.
  pa=me.attributes.get('115 Original world position');tag=me.attributes.get('167 Exposed shoulder core')or me.attributes.new('167 Exposed shoulder core','FLOAT','FACE');me.materials.append(core);coreidx=len(me.materials)-1;custom=[v.vector.copy()for v in me.corner_normals];exposed=0;unchanged=0;outside_loss=0
  for v in me.vertices:
   if oldpos and pa:
    if tuple(v.co)in oldcoords:pa.data[v.index].vector=oldpos[oldcoords[tuple(v.co)]]
    else:
     hit=tree.find_nearest(v.co);t=tris[hit[2]];pa.data[v.index].vector=geometry.barycentric_transform(v.co,*[srcverts[i]for i in t],*[oldpos[i]for i in t])
  for p in me.polygons:
   key=tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices));hit=tree.find_nearest(p.center);in_cut_bounds=all(xmin-.002<=(M@me.vertices[i].co).x<=xmax+.002 and 174.998<=(M@me.vertices[i].co).y<=198.602 and zmin-.002<=(M@me.vertices[i].co).z<=zmax+.002 for i in p.vertices);on_cutter=all(cuttertree.find_nearest(me.vertices[i].co)[3]<.0002 for i in p.vertices);iscore=bool(hit and hit[3]>1e-4 and in_cut_bounds and on_cutter);tag.data[p.index].value=float(iscore)
   if iscore:p.material_index=coreidx;exposed+=1
   if key in oldkeys:unchanged+=1
   for k in p.loop_indices:
    coo=tuple(me.vertices[me.loops[k].vertex_index].co)
    if (key,coo)in normals:custom[k]=normals[(key,coo)]
    elif iscore:custom[k]=p.normal.copy()
    else:
     nh=tree.find_nearest(me.vertices[me.loops[k].vertex_index].co);t=tris[nh[2]];sp=src.polygons[src.loop_triangles[nh[2]].polygon_index];ns=[src.corner_normals[i].vector for i in sp.loop_indices];custom[k]=geometry.barycentric_transform(me.vertices[me.loops[k].vertex_index].co,*[srcverts[i]for i in t],*ns).normalized()
  me.normals_split_custom_set(custom);source_material_mismatches=[]
  for p in me.polygons:
   hit=tree.find_nearest(p.center)
   if hit and hit[3]<1e-4:
    old_index=src.polygons[src.loop_triangles[hit[2]].polygon_index].material_index
    if p.material_index!=old_index:source_material_mismatches.append(p.index)
  row['surviving_surface_material_mismatches']=source_material_mismatches
  if source_material_mismatches:row['held']='Surviving source face material mismatch'
  newkeys={tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices))for p in me.polygons}
  for p in src.polygons:
   pts=[M@src.vertices[i].co for i in p.vertices]
   if all(v.x<xmin or v.x>xmax or v.z<zmin or v.z>zmax or v.y>198.6 or v.y<175 for v in pts):
    # A face entirely beyond one same coordinate halfspace is definitely protected.
    if any(all(v[k]<lo for v in pts)or all(v[k]>hi for v in pts)for k,lo,hi in [(0,xmin,xmax),(1,175,198.6),(2,zmin,zmax)]):
     if tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices))not in newkeys:outside_loss+=1
  from bpy_extras.object_utils import world_to_camera_view
  coreverts={i for p in me.polygons if tag.data[p.index].value>.5 for i in p.vertices};uv=[world_to_camera_view(bpy.context.scene,bpy.context.scene.camera,M@me.vertices[i].co)for i in coreverts]
  normerr=max(((me.corner_normals[k].vector-normals[(tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices)),tuple(me.vertices[me.loops[k].vertex_index].co))]).length for p in me.polygons if tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices))in oldkeys for k in p.loop_indices),default=0)
  row.update(exposed_faces=exposed,retained_exact_triangles=unchanged,protected_outside_triangle_loss=outside_loss,max_retained_corner_normal_delta=normerr,new_core_material=core.name,new_core_projected_bbox=([min(v.x for v in uv)*3840,min(1-v.y for v in uv)*2885,max(v.x for v in uv)*3840,max(1-v.y for v in uv)*2885]if uv else None))
  if outside_loss:row['held']='Protected outside triangle retriangulation';bpy.data.objects.remove(tmp,do_unlink=True);continue
  slots=[(s.link,s.material)for s in ob.material_slots];payload.append((ob,me,slots));bpy.data.objects.remove(tmp,do_unlink=True)
 held=[r for r in rows if 'held'in r];audit={'source':'163','references':['UCL-01','UCL-02','DP-03'],'profile_world_xz':PROFILE,'depth':'Two explicit transverse depth steps atY188.8 and194; rear198.6. Main facing upper edge offset by masonry steps. Broad belt2 retained longer; projecting rib ends shortened toZ38.2.','targets':rows,'accepted_cpu':not held and bool(payload),'protected':'Tower7 core/silhouette, all arches and round columns remain untouched; only facing/collar/continuous-wall/sill targets listed.','seconds':time.time()-start}
 if not held:
  for ob in removals:bpy.data.objects.remove(ob,do_unlink=True)
  for ob,me,slots in payload:
   ob.data=me
   for s,(link,mat)in zip(ob.material_slots,slots):s.link=link;s.material=mat
   for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 else:
  audit['disposition']='Whole study held; no partial target installation.'
 return audit
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));audit=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit),flush=True)
 if audit['accepted_cpu']:bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
