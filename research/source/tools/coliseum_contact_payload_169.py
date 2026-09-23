"""Build immutable native clip intervals from old-support versus new-solid distance."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import O,BOX,snapshot,digest,tree,run,interpolate,apply
oldnames=[r['object']for r in json.load(open(R/'art/studies/coliseum-167/geometry/audit.json'))['targets']]
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-166/scene.blend'));gp=bpy.data.objects['110 Landmark contact ink'];old=snapshot(gp);M=gp.matrix_world.copy();oldtree=tree(bpy.data.collections['110 Coliseum detailed front ruin'],oldnames)
path=R/'art/studies/coliseum-168/scene.blend';path=path if path.exists()else R/'art/studies/coliseum-167/geometry/scene.blend';bpy.ops.wm.open_mainfile(filepath=str(path));C=bpy.data.collections['110 Coliseum detailed front ruin'];newtree=tree(C);changes=[]
for rec in old:
 for si,st in enumerate(rec['strokes']):
  vv=[M@Vector(p)for p in st['point']['position']]
  if len(vv)<2 or any(max(v[k]for v in vv)<lo or min(v[k]for v in vv)>hi for k,(lo,hi)in enumerate(BOX)):continue
  def p_at(t):return M@Vector(interpolate(st,t)['position'])
  def unsupported(t):
   p=p_at(t)
   if any(not lo<=p[k]<=hi for k,(lo,hi)in enumerate(BOX)):return False
   return oldtree.find_nearest(p)[3]<.02 and newtree.find_nearest(p)[3]>.03
  samples=[0.]
  for i,(a,b)in enumerate(zip(vv,vv[1:])):
   if any(max(a[k],b[k])<lo or min(a[k],b[k])>hi for k,(lo,hi)in enumerate(BOX)):samples.append(float(i+1));continue
   n=max(1,math.ceil((a-b).length/.025));samples.extend(i+j/n for j in range(1,n+1))
  status=[unsupported(t)for t in samples]
  if not any(status):continue
  removed=[];start=0. if status[0]else None
  for i in range(1,len(samples)):
   if status[i]==status[i-1]:continue
   a,b=samples[i-1],samples[i];sa=status[i-1]
   for _ in range(22):
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
  evid=[]
  for a,b in removed:
   ts=[t for t in samples if a+1e-6<t<b-1e-6]
   ts.extend([a+(b-a)*.0001,(a+b)/2,b-(b-a)*.0001]);evid.extend(list(p_at(t))for t in ts)
  changes.append({'layer':rec['layer'],'frame':rec['frame'],'stroke':si,'removed_parameter_intervals':removed,'retained_parameter_intervals':kept,'runs':[run(st,a,b)for a,b in kept],'removal_samples_world':evid})
payload={'source_digest':digest(old),'source':'166','support_comparison':str(path.relative_to(R)),'old_target_support_distance_max_m':.02,'all_surviving_solid_support_distance_min_m':.03,'sample_spacing_max_m':.025,'transition_bisection_iterations':22,'changes':changes}
(O/'clip-payload.json').write_text(json.dumps(payload,indent=2));audit=apply(C);audit['support_scene']=str(path.relative_to(R));audit['removed_intervals']=sum(len(r['removed_parameter_intervals'])for r in changes);audit['new_runs']=sum(len(r['runs'])for r in changes);(O/'correction-audit.json').write_text(json.dumps(audit,indent=2));print(audit,flush=True)
# Isolated correction candidate, not a canonical scene write.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'corrected-study.blend'))
