"""Read-only152 native audit; reuse135 exact evaluated geometry certificates."""
import bpy,bmesh,json,sys,time,hashlib,array,types
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import strict_crossings
O=R/'art/studies/coliseum-156/preflight';O.mkdir(parents=True,exist_ok=True)
old=json.loads((R/'art/studies/coliseum-135/crossing-visibility.json').read_text());oldcross={r['object']:r['strict_crossings']for r in old['rows']}
def C():return next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin'and not c.library)
def sig(ob,me):
 h=hashlib.sha256();h.update(repr(tuple(tuple(r)for r in ob.matrix_world)).encode())
 for coll,key,size,code in [(me.vertices,'co',3,'f'),(me.loops,'vertex_index',1,'i'),(me.polygons,'loop_start',1,'i'),(me.polygons,'loop_total',1,'i')]:
  a=array.array(code,[0])*(len(coll)*size);coll.foreach_get(key,a);h.update(a.tobytes())
 return h.hexdigest()
t=time.time();bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-135/scene.blend'));dg=bpy.context.evaluated_depsgraph_get();baseline={}
for ob in C().all_objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();baseline[ob.name]=sig(ev,me);ev.to_mesh_clear()
print('BASELINE',len(baseline),flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-152/scene.blend'));dg=bpy.context.evaluated_depsgraph_get();rows=[];health=[];columns=[];changed=[]
for ob in C().all_objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();h=sig(ev,me);same=baseline.get(ob.name)==h
 if 'engaged round column'in ob.name:
  columns.append({'object':ob.name,'exactly_unchanged_since135':same});ev.to_mesh_clear();continue
 if same:cross=oldcross.get(ob.name,0);method='Exact135 evaluated vertices/topology/world transform hash; reuse exhaustive strict audit'
 else:
  print('CHECK',ob.name,flush=True);cross=strict_crossings(types.SimpleNamespace(data=me,matrix_world=ev.matrix_world));method='Fresh strict evaluated check';changed.append(ob.name)
 rows.append({'object':ob.name,'crossings':cross,'method':method,'evaluated_geometry_world_sha256':h});ev.to_mesh_clear()
 bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();bm.faces.index_update();zero=[f for f in bm.faces if f.calc_area()<1e-10]
 if zero:
  ids=[f.index for f in zero];areas=[f.calc_area()for f in zero];before={'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)}
  record={'object':ob.name,'near_zero_faces_below1e10':len(zero),'strict_zero_below1e14':sum(a<1e-14 for a in areas),'min_area':min(areas),'max_area':max(areas),'face_ids':ids,'before':before}
  bmesh.ops.delete(bm,geom=zero,context='FACES_ONLY');record['after_face_only_delete']={'boundary':sum(e.is_boundary for e in bm.edges),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)};record['safe_face_only_cleanup_demonstrated']=False;record['interpretation']='Deleting faces alone can open topology or leave wires; numerical area threshold is not proof of visually/topologically safe removal. No source edit.';health.append(record)
 bm.free()
report={'source':'art/studies/coliseum-152/scene.blend','baseline_audit':'art/studies/coliseum-135/crossing-visibility.json','seconds':time.time()-t,'mesh_objects':len(rows)+len(columns),'excluded_intentional_assembled_columns':columns,'exactly_reused_noncolumn_objects':sum(r['method'].startswith('Exact')for r in rows),'freshly_checked_changed_or_new':changed,'remaining_noncolumn_crossing_objects':sum(r['crossings']>0 for r in rows),'remaining_strict_crossing_pairs':sum(r['crossings']for r in rows),'crossing_issues':[r for r in rows if r['crossings']],'all_crossing_checks':rows,'near_zero_issue_objects':health,'near_zero_total':sum(r['near_zero_faces_below1e10']for r in health),'limitations':['Strict crossing helper excludes shared-vertex, coplanar, near-parallel triangle intersections and tiny numerical penetrations.','No global inter-object overlap/contact/support certificate;54 intentional assembled columns excluded.','135 screen visibility triage is not refreshed or inherited as current visibility: only geometric crossing certificates reused.','Raw area threshold is1e-10 square local units; not by itself a cleanup criterion.','No scene writes and no GPU renders.']}
(O/'audit.json').write_text(json.dumps(report,indent=2));print('DONE',report['remaining_noncolumn_crossing_objects'],report['remaining_strict_crossing_pairs'],report['near_zero_total'],report['seconds'],flush=True)
