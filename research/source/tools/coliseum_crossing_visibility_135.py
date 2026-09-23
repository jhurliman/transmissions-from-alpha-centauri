"""Read-only visible-surface triage of inherited within-component folds."""
import bpy,sys,json,time,types,math
from pathlib import Path
from mathutils import Vector,geometry
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_crown_repair_123 import strict_crossings
O=R/'art/studies/coliseum-135';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library)
volumes=[]
for ob in s.objects:
 if ob.type!='MESH':continue
 isvolume=any(slot.material and slot.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in slot.material.node_tree.nodes)for slot in ob.material_slots)
 if isvolume:ob.hide_set(True);volumes.append(ob.name)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();camera=s.camera.matrix_world.translation;rows=[];tested=0;column_overlap=0;t=time.time()
def project(p):
 q=world_to_camera_view(s,s.camera,p);return [q.x*3840,(1-q.y)*2885,q.z]
def intersection_points(A,B):
 points=[]
 for V,W in [(A,B),(B,A)]:
  for k in range(3):
   a,b=V[k],V[(k+1)%3];d=b-a
   if d.length<1e-8:continue
   hit=geometry.intersect_ray_tri(*W,d.normalized(),a,True)
   if hit is not None and -.00001<=(hit-a).dot(d.normalized())<=d.length+.00001 and all((hit-p).length>1e-5 for p in points):points.append(hit)
 return points
for ob in C.all_objects:
 if ob.type!='MESH':continue
 tested+=1;ev=ob.evaluated_get(dg);me=ev.to_mesh();pairs=strict_crossings(types.SimpleNamespace(data=me,matrix_world=ev.matrix_world),True)
 if not pairs:ev.to_mesh_clear();continue
 if 'engaged round column' in ob.name:
  column_overlap+=1;ev.to_mesh_clear();continue
 me.calc_loop_triangles();verts=[ev.matrix_world@v.co for v in me.vertices];visible=[];inside=0
 for ai,bi in pairs:
  A=[verts[i]for i in me.loop_triangles[ai].vertices];B=[verts[i]for i in me.loop_triangles[bi].vertices];pts=intersection_points(A,B)
  if len(pts)<2:continue
  a,b=max(((a,b)for a in pts for b in pts),key=lambda pair:(pair[0]-pair[1]).length_squared);pa,pb=project(a),project(b);length=math.hypot(pa[0]-pb[0],pa[1]-pb[1]);hits=[]
  for f in [.15,.5,.85]:
   p=a.lerp(b,f);pix=project(p)
   if not(0<=pix[0]<3840 and 0<=pix[1]<2885 and pix[2]>0):continue
   inside+=1;direction=p-camera;hit,loc,normal,face,owner,matrix=s.ray_cast(dg,camera,direction.normalized(),distance=direction.length+.01)
   if hit and abs((loc-camera).length-direction.length)<.006:hits.append({'pixel':pix[:2],'visible_owner':owner.name,'depth_error_m':(loc-camera).length-direction.length})
  if hits:visible.append({'triangles':[ai,bi],'segment_projected_length_px':length,'samples':hits,'segment_pixels':[pa[:2],pb[:2]]})
 rows.append({'object':ob.name,'strict_crossings':len(pairs),'screen_samples_tested':inside,'visible_segment_candidates':len(visible),'largest_visible_segment_px':max((v['segment_projected_length_px']for v in visible),default=0),'visible':visible});ev.to_mesh_clear()
rows.sort(key=lambda r:-r['largest_visible_segment_px']);out={'source':'135 scene','evaluated_meshes':tested,'intentional_column_component_overlaps':column_overlap,'remaining_noncolumn_crossing_objects':len(rows),'objects_with_visible_candidates':sum(bool(r['visible'])for r in rows),'volume_shells_omitted_from_occlusion':volumes,'rows':rows,'seconds':time.time()-t,'method':'Strict nonadjacent triangle penetrations, segment intersections projected at4K;3samples/segment raycast against current scene without volume shells;depth tolerance6mm. Known unchanged54column assembly component overlaps classified separately.','limits':['Visibility triage, not a clean geometry certificate','Hidden folds can still affect shadows; no claim they are harmless','Finite samples and tolerance can miss small crossings or classify nearby surface as visible','Coplanar and shared-vertex defects not tested by strict helper']};(O/'crossing-visibility.json').write_text(json.dumps(out,indent=2));print('DONE',len(rows),out['objects_with_visible_candidates'],out['seconds'],flush=True)
