import bpy,bmesh,json,sys,time,types,numpy as np,math
from pathlib import Path
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];sys.path[:0]=[str(R/'tools'),str(R/'art/studies/coliseum-174/native')]
from repair_174 import apply as repair174
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_continuation_154 import freeze_render_triangles
from coliseum_shoulder_failure_167 import health as legacy_health
def health(me,M):
 d=legacy_health(me,M);d["legacy_bmesh_zero_faces"]=d["zero_faces"];me.calc_loop_triangles();v=np.array([tuple(q.co)for q in me.vertices],dtype=np.float64);a=v[np.array([tuple(t.vertices)for t in me.loop_triangles])];areas=np.linalg.norm(np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]),axis=1)/2;d["zero_faces"]=int(np.sum(areas<1e-10));d["min_float64_triangle_area_local"]=float(areas.min());return d
O=R/'art/studies/coliseum-179/geometry'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];repair174(C);dg=bpy.context.evaluated_depsgraph_get();original,world,unpack=mapping();names=json.load(open(R/'config/coliseum-broad-crown-179.json'))['targets'];core=bpy.data.materials['165 Existing light on exposed masonry core']
# u is original facade arc length from U4L left extent. Near skin floor and
# rear depth vary coherently, rather than a radial cylinder cut.
sections=[(.45,71.65,73.45),(2.0,70.45,72.70),(4.40,70.65,71.70),(6.20,71.50,72.80),(8.95,71.50,72.80),(10.65,70.85,71.85),(12.85,72.60,72.70),(13.15,74.20,73.90),(14.75,74.20,73.90),(15.35,70.65,72.10),(17.65,69.80,71.50),(18.20,70.45,72.60)]
# Each strip is a four-corner cross-section. Rear floor rises modestly into
# retained masonry, making a broad sloped break face instead of horizontal shelf.
rows=[];payload=[];protectedmap={};start=time.time()
for name in names:
 ob=C.objects[name];src=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);M=ob.matrix_world.copy();iv=M.inverted();src=freeze_render_triangles(src);src.calc_loop_triangles();verts=[v.co.copy()for v in src.vertices];tri=[tuple(t.vertices)for t in src.loop_triangles];tree=BVHTree.FromPolygons(verts,tri,all_triangles=True);coords={tuple(v.co):v.index for v in src.vertices};keys={tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices)):p.index for p in src.polygons};norms={(key,tuple(src.vertices[src.loops[k].vertex_index].co)):src.corner_normals[k].vector.copy()for key,pi in keys.items()for k in src.polygons[pi].loop_indices};pos=[a.vector.copy()for a in src.attributes['115 Original world position'].data];before=health(src,M)
 row={'object':name,'before':before};rows.append(row)
 if before['crossings']or before['nonmanifold']or before['zero_faces']:row['held']='Source topology';continue
 def protected(p):
  aa=[unpack(M@verts[i])for i in p.vertices]
  if max(q[2]for q in aa)<67.8:return True
  if 'aperture head'in name and max(q[2]for q in aa)<71.15:return True
  # Protect actual high peak faces plus substantial near-side shoulder, not all rear surfaces.
  return any(-2.263<=a<=-2.243 and z>=71.6 for r,a,z in aa)
 exceptions={'COL110 U4 fractured upper wall R':[5042,5054,5055,5058],'COL110 U5 fractured upper wall L':[1393,1396,1401]}.get(name,[]);protectedids=[p.index for p in src.polygons if protected(p)and p.index not in exceptions];anchorids=[i for i,p in enumerate(verts)if -2.263<=unpack(M@p)[1]<=-2.243 and unpack(M@p)[2]>=71.6];row['permitted_rear_core_split_faces']=exceptions;protectedmap[name]={'faces':protectedids,'source_polygons':len(src.polygons),'matrix':list(map(list,M)),'rules':'Lower source below67.8; headbearing below71.15; actual source triangles touching principal high peak/near shoulder sector. Records explicit triangles before Boolean.'}
 (O/'protected-faces.json').write_text(json.dumps(protectedmap,indent=2))
 vv=[]
 for u,z,rear in sections:
  a=-2.439+u/75
  for r,zz in [(rear,z+.35),(79,z),(79,79),(rear,79)]:vv.append(iv@world(r,a,zz))
 ff=[(3,2,1,0),tuple(range((len(sections)-1)*4,len(sections)*4))]
 for j in range(len(sections)-1):
  for k in range(4):ff.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
 cm=bpy.data.meshes.new('179 variable-depth negative solid');cm.from_pydata(vv,[],ff);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();cut=bpy.data.objects.new('179 temporary negative solid',cm);C.objects.link(cut);ctree=BVHTree.FromPolygons([v.co.copy()for v in cm.vertices],[tuple(p.vertices)for p in cm.polygons]);tmp=bpy.data.objects.new('179 temporary target',src.copy());C.objects.link(tmp);mod=tmp.modifiers.new('179 subtractive compound crown','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=tmp;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);me=tmp.data;me.update()
 # One bounded triangulation correction of NEW large cut polygons only.
 # Blender's default32-gon tessellation crosses a near-collinear boundary24um.
 new_ngons=[p.index for p in me.polygons if len(p.vertices)>4 and tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices))not in keys]
 if new_ngons:
  bm=bmesh.new();bm.from_mesh(me);bm.faces.ensure_lookup_table();bmesh.ops.triangulate(bm,faces=[bm.faces[i]for i in new_ngons],ngon_method='BEAUTY');bm.to_mesh(me);bm.free();me.update()
 row['new_ngons_beauty_triangulated']=new_ngons
 after=health(me,M);row['after']=after;row['removed_volume_m3']=before['volume']-after['volume'];newkeys={tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices)):p.index for p in me.polygons};missing=[pi for pi in protectedids if tuple(sorted(tuple(src.vertices[i].co)for i in src.polygons[pi].vertices))not in newkeys];row['protected_missing']=missing;row['missing_peak_anchor_vertices']=[i for i in anchorids if tuple(verts[i])not in {tuple(v.co)for v in me.vertices}]
 if after['crossings']or after['nonmanifold']or after['zero_faces']or after['components']!=before['components']or row['removed_volume_m3']<=0 or missing or row['missing_peak_anchor_vertices']:row['held']='Topology, volume or protected-face gate';bpy.data.objects.remove(tmp,do_unlink=True);continue
 # Restore original coordinates and all surviving source-face assignments.
 pa=me.attributes['115 Original world position'];me.materials.append(core);ci=len(me.materials)-1;tag=me.attributes.new('179 Exposed crown core','FLOAT','FACE');custom=[n.vector.copy()for n in me.corner_normals];corecount=0;retainedcount=0
 for v in me.vertices:
  if tuple(v.co)in coords:pa.data[v.index].vector=pos[coords[tuple(v.co)]]
  else:
   hit=tree.find_nearest(v.co);tt=tri[hit[2]];pa.data[v.index].vector=geometry.barycentric_transform(v.co,*[verts[i]for i in tt],*[pos[i]for i in tt])
 for p in me.polygons:
  key=tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices));hit=tree.find_nearest(p.center);iscore=hit[3]>1e-4 and all(ctree.find_nearest(me.vertices[i].co)[3]<.0002 for i in p.vertices);tag.data[p.index].value=float(iscore)
  if iscore:p.material_index=ci;corecount+=1
  elif hit[3]<1e-4:p.material_index=src.polygons[src.loop_triangles[hit[2]].polygon_index].material_index
  if key in keys:retainedcount+=1
  for li in p.loop_indices:
   xyz=tuple(me.vertices[me.loops[li].vertex_index].co)
   if(key,xyz)in norms:custom[li]=norms[(key,xyz)]
   elif iscore:custom[li]=p.normal.copy()
   else:
    h=hit if hit[3]<1e-4 else tree.find_nearest(Vector(xyz));tt=tri[h[2]];sp=src.polygons[src.loop_triangles[h[2]].polygon_index];custom[li]=geometry.barycentric_transform(Vector(xyz),*[verts[i]for i in tt],*[src.corner_normals[k].vector for k in sp.loop_indices]).normalized()
 # Explicitly preserve authored attributes on exact surviving source vertices/faces.
 for attr in src.attributes:
  if attr.name.startswith('.')or attr.name in {'position','custom_normal','sharp_edge'}:continue
  dst=me.attributes.get(attr.name)
  if not dst:continue
  prop=next((q for q in ['vector','color','value']if len(attr.data)and hasattr(attr.data[0],q)),None)
  if not prop:continue
  if attr.domain=='POINT':
   for v in me.vertices:
    if tuple(v.co)in coords:setattr(dst.data[v.index],prop,getattr(attr.data[coords[tuple(v.co)]],prop))
  elif attr.domain=='FACE':
   for key,ni in newkeys.items():
    if key in keys:setattr(dst.data[ni],prop,getattr(attr.data[keys[key]],prop))
 me.normals_split_custom_set(custom);row['new_core_faces']=corecount;row['retained_exact_triangles']=retainedcount;row['max_retained_normal_delta']=max(((me.corner_normals[li].vector-norms[(key,tuple(me.vertices[me.loops[li].vertex_index].co))]).length for key,pi in newkeys.items()if key in keys for li in me.polygons[pi].loop_indices),default=0)
 # Sign against closest oriented source surface; record uncertain near-surface cases.
 me.calc_loop_triangles();samples=[v.co.copy()for v in me.vertices if tuple(v.co)not in coords]+[sum((me.vertices[i].co for i in t.vertices),Vector())/3 for t in me.loop_triangles if tuple(sorted(tuple(me.vertices[i].co)for i in t.vertices))not in keys];outside=[]
 for p in samples:
  h=tree.find_nearest(p)
  if h[3]>1e-5 and(p-h[0]).dot(h[1])>1e-4:outside.append(float((p-h[0]).dot(h[1])))
 row['source_envelope_max_outward_local']=max(outside,default=0);row['envelope_samples']=len(samples)
 if outside:
  from bpy_extras.object_utils import world_to_camera_view
  arr=np.array([[tuple(verts[i])for i in t]for t in tri],dtype=np.float64);cert=[];unresolved=[]
  for p in samples:
   h=tree.find_nearest(p)
   if h[3]<=1e-5 or(p-h[0]).dot(h[1])<=1e-4:continue
   abc=arr-np.array(tuple(p));lens=np.linalg.norm(abc,axis=2);numer=np.einsum('ij,ij->i',abc[:,0],np.cross(abc[:,1],abc[:,2]));den=lens.prod(axis=1)+np.einsum('ij,ij->i',abc[:,0],abc[:,1])*lens[:,2]+np.einsum('ij,ij->i',abc[:,1],abc[:,2])*lens[:,0]+np.einsum('ij,ij->i',abc[:,2],abc[:,0])*lens[:,1];winding=float(np.sum(2*np.arctan2(numer,den))/(4*np.pi));dist=(M@p-M@h[0]).length;ap=world_to_camera_view(s,s.camera,M@p);bp=world_to_camera_view(s,s.camera,M@h[0]);px=((ap.x-bp.x)**2*3840**2+(ap.y-bp.y)**2*2885**2)**.5;rowc={'point_local':list(p),'winding':winding,'nearest_world_m':dist,'projected_px':px,'inside':abs(winding)>.5,'inherited154_numerical_budget':dist<=.0005 and px<=.02};cert.append(rowc)
   if not rowc['inside']and not rowc['inherited154_numerical_budget']:unresolved.append(rowc)
  row['source_envelope_exception_certificate']=cert;row['source_containment_unresolved']=len(unresolved)
  if unresolved:row['held']='Outside source beyond established154 numeric residual budget'
 row['retained_small_source_triangles']=[{'face':p.index,'exact':tuple(sorted(tuple(src.vertices[i].co)for i in p.vertices))in newkeys}for p in src.polygons if float(np.linalg.norm(np.cross(np.array(verts[p.vertices[1]])-np.array(verts[p.vertices[0]]),np.array(verts[p.vertices[2]])-np.array(verts[p.vertices[0]])))/2)<1e-7];payload.append((ob,me));bpy.data.objects.remove(tmp,do_unlink=True)
 (O/'audit-partial.json').write_text(json.dumps({'targets':rows},indent=2));print(name,row,flush=True)
audit={'source':'173 +174','sections_u_frontfloor_reardepth':sections,'targets':rows,'accepted_cpu':not any('held'in r for r in rows)and len(payload)==4,'seconds':time.time()-start,'normal_preservation':'Quantified after Blender custom-normal storage; not claimed bit-exact.'};(O/'audit.json').write_text(json.dumps(audit,indent=2))
if audit['accepted_cpu']:
 for ob,me in payload:
  slots=[(sl.link,sl.material)for sl in ob.material_slots];ob.data=me
  for sl,(link,mat)in zip(ob.material_slots,slots):sl.link=link;sl.material=mat
  for mod in list(ob.modifiers):ob.modifiers.remove(mod)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'))
print('179 FINAL',json.dumps(audit),flush=True)
