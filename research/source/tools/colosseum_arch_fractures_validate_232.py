import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/colosseum-fractures-232';bpy.ops.wm.open_mainfile(filepath=str(O/'fractures-only.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];dg=bpy.context.evaluated_depsgraph_get();audit=json.loads((O/'audit.json').read_text());changed={r['object']for r in audit['targets']};vs=[[],[]];fs=[[],[]]
for ob in C.objects:
 if ob.type!='MESH'or ob.hide_render:continue
 ev=ob.evaluated_get(dg);now=ev.to_mesh();old=bpy.data.meshes.get('232 SOURCE '+ob.name)if ob.name in changed else now
 for k,me in enumerate([old,now]):
  assert me,ob.name;me.calc_loop_triangles();off=len(vs[k]);vs[k].extend(ob.matrix_world@v.co for v in me.vertices);fs[k].extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles)
 ev.to_mesh_clear()
trees=[BVHTree.FromPolygons(v,f,all_triangles=True)for v,f in zip(vs,fs)];cam=s.camera;origin=cam.matrix_world.translation;rot=cam.matrix_world.to_3x3();fr=cam.data.view_frame(scene=s);lx=min(p.x for p in fr);hx=max(p.x for p in fr);ly=min(p.y for p in fr);hy=max(p.y for p in fr);z=fr[0].z
rows=[]
for c in audit['cutters']:
 samples=[]
 for aa,bb in zip(c['path_native_4k'],c['path_native_4k'][1:]):
  for i in range(8):
   p=Vector(aa).lerp(Vector(bb),i/8);d=(rot@Vector((lx+(hx-lx)*p.x/3840,hy-(hy-ly)*p.y/2885,z))).normalized();hits=[t.ray_cast(origin,d,1000)for t in trees];before=hits[0][3];after=hits[1][3];change=(after-before)if before is not None and after is not None else(None if before is None else 1000);samples.append({'native_pixel':list(p),'before_m':before,'after_m':after,'recession_m':change})
 rows.append({'cutter':c['id'],'visible_recessed_samples':sum(r['recession_m']is not None and r['recession_m']>.03 for r in samples),'samples':samples})
ls=s.view_layers['215 Distant ink without atmospheric boundary'].freestyle_settings.linesets['232 New exposed masonry fracture edges'];out={'cut_paths':rows,'all_four_primary_paths_have_visible_actual_depth_change':all(next(r for r in rows if r['cutter']==q)['visible_recessed_samples']>0 for q in ['crown-trim0','left-branch0','central-open0','right-branch0']),'ink':{'collection':ls.collection.name,'selected_objects':len(ls.collection.objects),'edge_mark_only':ls.select_edge_mark and not ls.select_crease and not ls.select_contour,'new_cut_face_filter':ls.select_by_face_marks and ls.face_mark_condition=='ONE','visibility':ls.visibility},'geometry_gate':'Native actual landmark first-hit rays, excluding atmospheric volumes. This is a placement check, not an image/render acceptance.'};(O/'fresh-check.json').write_text(json.dumps(out,indent=2));assert out['all_four_primary_paths_have_visible_actual_depth_change'];print('232 FRESH',[(r['cutter'],r['visible_recessed_samples'])for r in rows],out['ink'],flush=True)
