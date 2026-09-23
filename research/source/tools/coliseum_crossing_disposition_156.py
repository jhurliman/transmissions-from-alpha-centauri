"""Bounded float64 disposition and current visibility of inherited crossing candidates."""
import bpy,json,sys,time,types,numpy as np
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_continuation_154 import robust_crossings
from coliseum_crown_repair_123 import strict_crossings
O=R/'art/studies/coliseum-156/preflight';a=json.loads((O/'audit.json').read_text());names=list(dict.fromkeys([r['object']for r in a['crossing_issues']]+a['freshly_checked_changed_or_new']))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH' and (ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation;rows=[];t0=time.time()
def intersection_segment(tris):
 A,B=[np.array(x)for x in tris];pts=[]
 for V,W in [(A,B),(B,A)]:
  e0=W[1]-W[0];e1=W[2]-W[0];n=np.cross(e0,e1);ln=np.linalg.norm(n)
  if ln<1e-12:continue
  n/=ln
  for i in range(3):
   p,q=V[i],V[(i+1)%3];d0=np.dot(p-W[0],n);d1=np.dot(q-W[0],n)
   if d0*d1>0 or abs(d0-d1)<1e-20:continue
   x=p+(q-p)*(d0/(d0-d1));v=x-W[0];aa=e0@e0;bb=e0@e1;cc=e1@e1;dd=v@e0;ee=v@e1;den=aa*cc-bb*bb
   if abs(den)<1e-20:continue
   u=(cc*dd-bb*ee)/den;w=(aa*ee-bb*dd)/den
   if min(u,w,1-u-w)>-1e-7:pts.append(x)
 if len(pts)<2:return None
 return max(((p,q)for p in pts for q in pts),key=lambda pq:np.linalg.norm(pq[0]-pq[1]))
for name in names:
 ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();M=ev.matrix_world.copy();proxy=types.SimpleNamespace(data=me,matrix_world=M);old=set(map(tuple,strict_crossings(proxy,True)));rob=robust_crossings(proxy,True);new={tuple(r['pair'])for r in rob};vis=[];penetr=[]
 for r in rob:
  penetr.append(min(abs(v)for v in r['plane_endpoint_signed_distances_world']));seg=intersection_segment(r['triangles_world'])
  if seg is None:continue
  p,q=[Vector(x)for x in seg];pp=world_to_camera_view(s,s.camera,p);qq=world_to_camera_view(s,s.camera,q);pixels=[(pp.x*3840,(1-pp.y)*2885),(qq.x*3840,(1-qq.y)*2885)];length=((pixels[0][0]-pixels[1][0])**2+(pixels[0][1]-pixels[1][1])**2)**.5;hits=[]
  for frac in [.15,.5,.85]:
   point=p.lerp(q,frac);uv=world_to_camera_view(s,s.camera,point)
   if not(0<=uv.x<=1 and 0<=uv.y<=1 and uv.z>0):continue
   direction=point-origin;ok,loc,normal,face,owner,mat=s.ray_cast(dg,origin,direction.normalized(),distance=direction.length+.006)
   if ok and owner.name==name and abs((loc-origin).length-direction.length)<.006:hits.append({'pixel':[uv.x*3840,(1-uv.y)*2885],'depth_error_m':abs((loc-origin).length-direction.length),'receiver':owner.name})
  if hits:vis.append({'pair':r['pair'],'projected_segment_length_px':length,'segment_pixels':pixels,'samples':hits})
 row={'object':name,'legacy_float32_count':len(old),'float64_count':len(new),'confirmed_by_both':len(old&new),'legacy_only_pairs':len(old-new),'float64_only_pairs':len(new-old),'max_min_endpoint_penetration_m':max(penetr,default=0),'current_visible_candidates':vis,'max_visible_segment_px':max((v['projected_segment_length_px']for v in vis),default=0),'disposition':'Actual unintended nonadjacent return/crown folds persist'if new else'Legacy crossing report not confirmed by float64 predicate at original tolerances','robust_pairs':[r['pair']for r in rob]};rows.append(row);ev.to_mesh_clear();print(name,len(old),'->',len(new),'visible',len(vis),flush=True)
d={'source':'152','seconds':time.time()-t0,'scope':'34 legacy crossing objects plus9 changed candidates;54 assembled columns excluded, no claim that untested old-clean meshes are float64-clean.','method':'Original evaluated mesh and exact copied matrix passed via SimpleNamespace; no temporary Blender transform decomposition. Same float64 predicate/tolerances as154, with float32 BVH broadphase. Current camera segment samples use6mm tolerance and actual same-object occlusion.','rows':rows,'limits':['Float64 narrowphase still uses float32 BVH broadphase, so this is a useful stricter classification, not an exact arithmetic proof.','Shared-vertex and coplanar overlaps excluded by predicate.','Visible candidates use finite3-point sampling and6mm depth tolerance; subpixel results may not produce visible defects.','No mutations saved or GPU renders.']};(O/'crossing-disposition-v2.json').write_text(json.dumps(d,indent=2));print('DONE',d['seconds'])
