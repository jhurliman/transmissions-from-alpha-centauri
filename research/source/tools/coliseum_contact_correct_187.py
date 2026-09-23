"""Certify and remove only173 contact intervals losing solid support in187.

Run only after the187 source-shape gate. No threshold tuning or cosmetic erasure.
"""
import bpy,json,sys,math,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import snapshot,digest,interpolate,run
from coliseum_contact_certificate_169 import certify
O=R/'art/studies/coliseum-187/contact';O.mkdir(parents=True,exist_ok=True)
inv=json.loads((O.parent/'contact-source/audit.json').read_text())

def solid_tree(obs,bounds=None):
 dg=bpy.context.evaluated_depsgraph_get();verts=[];tris=[];owners=[]
 for ob in obs:
  if ob.type!='MESH' or ob.hide_render or 'ink' in ob.name.lower():continue
  ev=ob.evaluated_get(dg);bb=[ev.matrix_world@Vector(v)for v in ev.bound_box]
  if bounds and any(max(v[k]for v in bb)<lo-.05 or min(v[k]for v in bb)>hi+.05 for k,(lo,hi)in enumerate(bounds)):continue
  me=ev.to_mesh();me.calc_loop_triangles();off=len(verts);verts.extend(ev.matrix_world@v.co for v in me.vertices);tris.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);owners.append(ob.name);ev.to_mesh_clear()
 assert verts
 return BVHTree.FromPolygons(verts,tris,all_triangles=True),verts,owners

bpy.ops.wm.open_mainfile(filepath=str(R/inv['source']))
gp=bpy.data.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy()
assert digest(old)==inv['source_drawing_digest']
oldtree,vs,_=solid_tree([bpy.data.objects[n]for n in inv['targets']])
BOX=[(min(v[k]for v in vs)-.05,max(v[k]for v in vs)+.05)for k in range(3)]
source=O.parent/'geometry/candidate.blend';bpy.ops.wm.open_mainfile(filepath=str(source))
C=bpy.data.collections['110 Coliseum detailed front ruin'];gp=bpy.data.objects['110 Landmark contact ink']
assert digest(snapshot(gp))==digest(old)
assert gp.matrix_world==M
newtree,_,owners=solid_tree(C.all_objects,BOX);changes=[]
for rec in old:
 for si,st in enumerate(rec['strokes']):
  vv=[M@Vector(p)for p in st['point']['position']]
  if len(vv)<2 or any(max(v[k]for v in vv)<lo or min(v[k]for v in vv)>hi for k,(lo,hi)in enumerate(BOX)):continue
  def p_at(t):return M@Vector(interpolate(st,t)['position'])
  def unsupported(t):
   p=p_at(t)
   return all(lo<=p[k]<=hi for k,(lo,hi)in enumerate(BOX)) and oldtree.find_nearest(p)[3]<.02 and newtree.find_nearest(p)[3]>.03
  samples=[0.]
  for i,(a,b)in enumerate(zip(vv,vv[1:])):
   if any(max(a[k],b[k])<lo or min(a[k],b[k])>hi for k,(lo,hi)in enumerate(BOX)):samples.append(float(i+1));continue
   n=max(1,math.ceil((a-b).length/.01));samples.extend(i+j/n for j in range(1,n+1))
  status=[unsupported(t)for t in samples]
  if not any(status):continue
  assert not st['curve'].get('cyclic',False),'Cyclic source needs separate interval topology'
  removed=[];start=0. if status[0]else None
  for i in range(1,len(samples)):
   if status[i]==status[i-1]:continue
   a,b=samples[i-1],samples[i];sa=status[i-1]
   for _ in range(24):
    m=(a+b)/2
    if unsupported(m)==sa:a=m
    else:b=m
   edge=(a+b)/2
   if status[i]:start=edge
   else:removed.append([start,edge]);start=None
  if start is not None:removed.append([start,float(len(vv)-1)])
  kept=[];p=0.
  for a,b in removed:
   if a-p>1e-7:kept.append([p,a])
   p=b
  if len(vv)-1-p>1e-7:kept.append([p,float(len(vv)-1)])
  changes.append({'layer':rec['layer'],'frame':rec['frame'],'stroke':si,'removed_parameter_intervals':removed,'retained_parameter_intervals':kept,'runs':[run(st,a,b)for a,b in kept]})
payload={'source':inv['source'],'source_digest':digest(old),'source_matrix_world':[list(row)for row in M],'support_comparison':str(source.relative_to(R)),'old_target_support_distance_max_m':.02,'candidate_solid_distance_screen_min_m':.03,'sample_step_max_m':.01,'changes':changes,'support_meshes':owners}
certificate=certify(payload,old,M,newtree)
(O/'clip-payload.json').write_text(json.dumps(payload,indent=2)+'\n')
(O/'continuous-support-certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
gp.data=gp.data.copy();expected_records=[]
def stored(v):
 if isinstance(v,list):return [stored(x)for x in v]
 return struct.unpack('f',struct.pack('f',v))[0] if isinstance(v,float) else v
for rec in old:
 edits=[r for r in changes if r['layer']==rec['layer'] and r['frame']==rec['frame']]
 if not edits:expected_records.append(rec);continue
 dr=gp.data.layers[rec['layer']].frames[rec['frame']].drawing;removed=sorted(r['stroke']for r in edits)
 kept=[st for i,st in enumerate(rec['strokes'])if i not in removed];runs=[st for r in edits for st in r['runs']]
 dr.remove_strokes(indices=removed);off=sum(len(st.points)for st in dr.strokes);curve_offset=len(dr.strokes)
 if runs:
  dr.add_strokes(sizes=[len(st['point']['position'])for st in runs])
  for j,st in enumerate(runs):
   for k,vv in st['point'].items():
    for i,v in enumerate(vv):setattr(dr.attributes[k].data[off+i],rec['schema'][k]['prop'],v)
   for k,v in st['curve'].items():setattr(dr.attributes[k].data[curve_offset+j],rec['schema'][k]['prop'],v)
   off+=len(st['point']['position'])
 expected_runs=[{'point':{k:stored(v)for k,v in st['point'].items()},'curve':st['curve']}for st in runs]
 expected_records.append(dict(rec,strokes=kept+expected_runs))
after=snapshot(gp)
assert after==expected_records,'Untouched attributes or reconstructed runs differ'
audit={'source_digest':digest(old),'after_digest':digest(after),'source_strokes':sum(len(r['strokes'])for r in old),'result_strokes':sum(len(r['strokes'])for r in after),'changed_source_strokes':len(changes),'changed_stroke_indices':[r['stroke']for r in changes],'removed_intervals':certificate['removed_intervals'],'minimum_certified_distance_m':certificate['minimum_certified_distance_m'],'unchanged_strokes_and_retained_run_attributes_exact':True,'no_geometry_material_light_camera_mutation':True,'scope':'Only source173 intervals formerly supported by the 187 course/sill/dentil meshes, continuously certified outside all nearby surviving non-ink landmark solids.','limits':'Source-support candidate selection is sampled; removals have a continuous1-Lipschitz absence-of-support certificate. No global ink certification is claimed.'}
(O/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'corrected-study.blend'))
print(json.dumps(audit),flush=True)
