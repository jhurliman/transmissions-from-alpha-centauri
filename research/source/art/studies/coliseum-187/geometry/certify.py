import bpy,json,sys,hashlib,array,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-187/geometry'
text=(R/'tools/scene_integration_138.py').read_text();exec(text[text.index('def objects('):text.index("if 'render' not in sys.argv:")])
names=json.load(open(R/'config/coliseum-left-course-187.json'))['targets'];source={}
def value(d):
 for q in ['vector','color','value']:
  if hasattr(d,q):
   v=getattr(d,q)
   try:return tuple(v)
   except TypeError:return v

def capture(ob,dg):
 ev=ob.evaluated_get(dg);me=ev.to_mesh();me.calc_loop_triangles();vs=[tuple(v.co)for v in me.vertices];ts={tuple(sorted(vs[i]for i in t.vertices)):{'material':ob.material_slots[me.polygons[t.polygon_index].material_index].material.name,'normals':{vs[me.loops[l].vertex_index]:tuple(me.corner_normals[l].vector)for l in t.loops},'face':t.polygon_index}for t in me.loop_triangles};attrs={a.name:{'domain':a.domain,'values':[value(d)for d in a.data]}for a in me.attributes if not a.name.startswith('.')and a.name not in ['position','custom_normal','sharp_edge']and a.domain in ['POINT','FACE']};h=hashlib.sha256(json.dumps({'verts':vs,'triangles':sorted(ts)},sort_keys=True).encode()).hexdigest();d={'verts':vs,'triangles':ts,'attributes':attrs,'hash':h,'matrix':list(map(list,ob.matrix_world)),'slots':[sl.material.name if sl.material else None for sl in ob.material_slots],'mesh_name':me.name};ev.to_mesh_clear();return d
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot();dg=bpy.context.evaluated_depsgraph_get()
for n in names:source[n]=capture(bpy.data.objects[n],dg)
bpy.ops.wm.open_mainfile(filepath=str(O/'fixed-shape-technical.blend'));s=bpy.context.scene;after=fingerprint(s);mats2=material_snapshot();outside=[n for n in set(before)|set(after)if n not in names and before.get(n)!=after.get(n)];materialdiff=[n for n in mats if mats[n]!=mats2.get(n)];rows=[];dg=bpy.context.evaluated_depsgraph_get();payload={}
for n in names:
 src=source[n];ob=bpy.data.objects[n];dst=capture(ob,dg);keys=set(src['triangles'])&set(dst['triangles']);badmat=[];normal=0;attrbad=[];vc={p:i for i,p in enumerate(src['verts'])}
 for k in keys:
  a,b=src['triangles'][k],dst['triangles'][k]
  if a['material']!=b['material']:badmat.append([a['face'],b['face']])
  for xyz,no in a['normals'].items():normal=max(normal,(Vector(no)-Vector(b['normals'][xyz])).length)
 for an,av in src['attributes'].items():
  bv=dst['attributes'].get(an)
  if not bv:attrbad.append([an,'missing']);continue
  if av['domain']=='POINT':
   bad=sum(bv['values'][i]!=av['values'][vc[p]]for i,p in enumerate(dst['verts'])if p in vc)
  else:bad=sum(bv['values'][dst['triangles'][k]['face']]!=av['values'][src['triangles'][k]['face']]for k in keys)
  if bad:attrbad.append([an,bad])
 rows.append({'object':n,'retained_exact_triangles':len(keys),'material_mismatches':badmat,'attribute_mismatches':attrbad,'max_retained_normal_delta':normal,'unchanged_transform':src['matrix']==dst['matrix'],'source_hash':src['hash'],'candidate_hash':dst['hash']});payload[n]={'source_hash':src['hash'],'candidate_hash':dst['hash'],'matrix':dst['matrix'],'slots':dst['slots'],'mesh_name':ob.data.name}
base=json.load(open(O/'audit.json'));double=json.load(open(O/'envelope-double.json'));exactzero=0;minarea=1
for n in names:
 me=bpy.data.objects[n].data;me.calc_loop_triangles();v=np.array([tuple(v.co)for v in me.vertices]);t=v[np.array([tuple(t.vertices)for t in me.loop_triangles])];areas=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)/2;exactzero+=int(sum(areas==0));minarea=min(minarea,float(areas.min()))
passed=not outside and not materialdiff and exactzero==0 and all(not r['material_mismatches']and not r['attribute_mismatches']and r['unchanged_transform']for r in rows)and all(r['new_crossing_pair_count']==0 and r['after']['nonmanifold']==0 and not r['protected_missing']for r in base['targets'])and max(r.get('double_nearest_m',0)for r in double)<1e-5
report={'accepted_cpu':passed,'outside_changed':outside,'source_inventory_entries':len(before),'old_material_graph_differences':materialdiff,'targets':rows,'exact_zero_area_triangles':exactzero,'smallest_nonzero_triangle_area_local':minarea,'envelope_double_max_m':max(r.get('double_nearest_m',0)for r in double),'envelope_limit':'Vertex/triangle-center and float64 nearest-source certificate; finite sampling, not analytic whole-surface proof. No vertex movement to address inaccurate float32 BVH distances.','inherited_crossing_pairs':sum(r['inherited_pair_count_retained']for r in base['targets']),'new_crossing_pairs':0,'normal_storage':'Blender normalized custom-normal quantization disclosed; no bit-exact normal claim.'}
(O/'certified-audit.json').write_text(json.dumps(report,indent=2));(O/'payload.json').write_text(json.dumps(payload,indent=2));print('CERTIFIED',passed,report)
if passed:
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));bpy.data.libraries.write(str(O/'payload.blend'),{bpy.data.objects[n].data for n in names})
