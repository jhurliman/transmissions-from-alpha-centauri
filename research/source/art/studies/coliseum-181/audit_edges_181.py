"""Read-only short fracture-edge visibility inventory on retained173."""
import bpy,sys,json,math,collections,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-181';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];names=[f'COL110 T2 band10 profile{i}'for i in range(4)]+[f'COL110 T2 band07 profile{i}'for i in range(4)]+['COL111 Tower7 tier2 stepped belt2','COL110 U4 fractured upper wall R','COL110 U5 fractured upper wall L'];settings=[]
for vl in s.view_layers:
 fs=vl.freestyle_settings
 settings.append({'view_layer':vl.name,'crease_angle_radians':fs.crease_angle,'mode':fs.mode,'linesets':[{'name':ls.name,'edge_types':{a:getattr(ls,a)for a in ['select_silhouette','select_border','select_crease','select_edge_mark','select_material_boundary','select_external_contour']},'visibility':ls.visibility}for ls in fs.linesets]})
for ob in s.objects:
 if ob.hide_render or(ob.type=='MESH'and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation;out=[];t0=time.time()
for name in names:
 ob=bpy.data.objects.get(name)
 if not ob:continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();M=ob.matrix_world;N=M.to_3x3().inverted().transposed();v=[M@x.co for x in me.vertices];uv=[world_to_camera_view(s,s.camera,p)for p in v];px=[Vector((p.x*3840,(1-p.y)*2885))for p in uv];adj=collections.defaultdict(list)
 for f in me.polygons:
  for key in f.edge_keys:adj[tuple(sorted(key))].append(f.index)
 edges=[];classes=collections.Counter()
 for e in me.edges:
  a,b=e.vertices;q=(px[a]+px[b])*.5
  roi=(1450<=q.x<1625 and 455<=q.y<605)or(1725<=q.x<1800 and 550<=q.y<660)or(2120<=q.x<2210 and 590<=q.y<675)
  if not roi:continue
  faceids=adj[tuple(sorted((a,b)))];nn=[(N@me.polygons[i].normal).normalized()for i in faceids];angle=math.degrees(nn[0].angle(nn[1]))if len(nn)==2 else 180.;length=(px[a]-px[b]).length;classes['all_roi_edges']+=1
  if angle<1:classes['coplanar_lt1deg']+=1
  if not(.3<=length<=12 and angle>=15):continue
  midpoint=(v[a]+v[b])*.5;direction=(midpoint-origin).normalized();hit,p,normal,fi,receiver,_=s.ray_cast(dg,origin,direction,distance=(midpoint-origin).length+.2);gap=(midpoint-origin).length-(p-origin).length if hit else None;visible=bool(hit and abs(gap)<.02)
  edges.append({'edge':e.index,'vertices':list(e.vertices),'world':[list(v[a]),list(v[b])],'pixels':[list(px[a]),list(px[b])],'midpoint_px':list(q),'projected_length_px':length,'dihedral_degrees':angle,'faces':faceids,'materials':[ob.material_slots[me.polygons[i].material_index].material.name if ob.material_slots[me.polygons[i].material_index].material else None for i in faceids],'first_receiver':receiver.name if hit else None,'midpoint_behind_first_world_m':gap,'visible_midpoint_2cm':visible})
 out.append({'object':name,'vertices':len(me.vertices),'faces':len(me.polygons),'classes':dict(classes),'selected_short_crease_edges':len(edges),'midpoint_visible':sum(e['visible_midpoint_2cm']for e in edges),'edges':edges});ev.to_mesh_clear()
(O/'native-edge-inventory.json').write_text(json.dumps({'source':'173','settings':settings,'objects':out,'seconds':time.time()-t0,'scope':'Read-only evaluated solid edges; geometric dihedral candidate inventory, not a Freestyle stroke-emission proof. Visibility sampled atmidpoint only, never deletion authorization.'},indent=2));print('DONE',[(r['object'],r['selected_short_crease_edges'],r['midpoint_visible'])for r in out],flush=True)
