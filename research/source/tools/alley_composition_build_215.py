import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-composition-215';sys.path.insert(0,str(R/'tools'))
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/colosseum-scale-210/70/scene.blend'));s=bpy.context.scene
from landmark_contact_visibility_210 import external_tree,restore_unclipped,apply as reclip
from colosseum_scale_metrics_210 import collect
C,members,dg,rows,P,T,E=collect(s);landmark=BVHTree.FromPolygons([Vector(p)for p in P],[tuple(t)for t in T],all_triangles=True)
ext,owners,inventory=external_tree(s);print('215 BASELINE TREES READY',flush=True)
frame=s.camera.data.view_frame(scene=s);frame=[-p/p.z for p in frame];minx=min(p.x for p in frame);maxx=max(p.x for p in frame);miny=min(p.y for p in frame);maxy=max(p.y for p in frame);M=s.camera.matrix_world.copy();origin=M.translation.copy();rays=[];regioncounts={}
for py in range(110,1230,12):
 for px in range(1180,2690,12):
  local=Vector((minx+(maxx-minx)*px/3840,miny+(maxy-miny)*(1-py/2885),-1));direction=(M.to_3x3()@local).normalized();hit=landmark.ray_cast(origin,direction)
  if hit[0]is None:continue
  if ext.ray_cast(origin,direction,max(0,hit[3]-.02))[0]is not None:continue
  h='left'if px<1680 else'center'if px<2180 else'right';v='crown'if py<460 else'upper_arcade'if py<730 else'middle_arcade'if py<950 else'lower_arcade';region=h+'_'+v;rays.append((px,py,list(direction),hit[3],region));regioncounts[region]=regioncounts.get(region,0)+1
fullprobes=[]
for py in range(12,2885,24):
 for px in range(12,3840,24):
  local=Vector((minx+(maxx-minx)*px/3840,miny+(maxy-miny)*(1-py/2885),-1));direction=(M.to_3x3()@local).normalized();hit=landmark.ray_cast(origin,direction)
  if hit[0]is not None and ext.ray_cast(origin,direction,max(0,hit[3]-.02))[0]is None:fullprobes.append([px,py])
coverage={'fullframe_probe_step_px':24,'visible_samples':len(fullprobes),'visible_bbox':[[min(p[k]for p in fullprobes)for k in range(2)],[max(p[k]for p in fullprobes)for k in range(2)]],'outside_fine_roi':[p for p in fullprobes if not(1180<=p[0]<=2690 and 110<=p[1]<=1230)]}
(O/'baseline-projected-bound-check.json').write_text(json.dumps(coverage,indent=2));assert not coverage['outside_fine_roi'],coverage
print('215 BASELINE EXPOSED',len(rays),regioncounts,flush=True)
del ext,owners,landmark,P,T,E
before={o.name:(o,o.matrix_world.copy(),o.data,o.hide_render)for o in s.objects}
from recess_scuffs_213 import apply as scuffs
if not any(m.name.startswith('213 Dense floor scuffs')for m in bpy.data.materials):a213=scuffs(s);(O/'recess-213-audit.json').write_text(json.dumps(a213,indent=2))
from alley_composition_215 import apply
a=apply(s);s.view_layers.update();print('215 ASSEMBLIES READY',flush=True)
roots=set(bpy.data.collections['215 Short alley composition'].objects);dg=bpy.context.evaluated_depsgraph_get();vs=[];ts=[];names=[]
for ins in dg.object_instances:
 if not ins.parent or ins.parent.original not in roots or ins.object.type not in('MESH','CURVE'):continue
 me=ins.object.to_mesh();me.calc_loop_triangles();off=len(vs);vs.extend(ins.matrix_world@v.co for v in me.vertices);ts.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);names.extend([ins.object.original.name]*len(me.loop_triangles));ins.object.to_mesh_clear()
assert ts,'No newbuildinggeometry in exposure tree';tree=BVHTree.FromPolygons(vs,ts,all_triangles=True);regions={r:{'baseline_visible_samples':n,'blocked_by_new_buildings':0}for r,n in regioncounts.items()};blocked=[]
for px,py,d,distance,region in rays:
 hit=tree.ray_cast(origin,Vector(d),distance-.02)
 if hit[0]is not None:regions[region]['blocked_by_new_buildings']+=1;blocked.append({'pixel':[px,py],'region':region,'occluder':names[hit[2]]})
for v in regions.values():v['retained_fraction']=1-v['blocked_by_new_buildings']/v['baseline_visible_samples']
framing={'baseline':'210/70 selected native scene','sampling':'12px uniform native4K raygrid overlandmark aperture; actual landmark and evaluatedopaque foreground BVH; tests retentionofbaselinevisiblelandmark samples','regions':regions,'total_baseline_visible':len(rays),'blocked':blocked,'new_building_triangles':len(ts),'retained_fraction':1-len(blocked)/len(rays)}
(O/'framing-audit.json').write_text(json.dumps(framing,indent=2));print('215 FRAMING',json.dumps(regions),flush=True)
# Keep the construction inspectable even if the framing gate needs a bounded adjustment.
assert all(v['retained_fraction']>=.97 for v in regions.values()if v['baseline_visible_samples']>=10),framing
restore=restore_unclipped(s,'84e3787b91152c4f17587b201a6808531ae69a1e5a96d71e8eda62c2e5da8358');(O/'contact-restoration.json').write_text(json.dumps(restore,indent=2));print('215 CONTACT SOURCE RESTORED',flush=True)
ink=reclip(s,O/'landmark-contact-visibility.json');print('215 CONTACT RECLIPPED',flush=True)
allowed=set(a['hidden_oldcity'])|{'101 A city contacts'}
for name,(ob,m,data,hidden)in before.items():
 assert max(abs(x-y)for p,q in zip(m,ob.matrix_world)for x,y in zip(p,q))<1e-6,name
 assert ob.data==data or name=='110 Landmark contact ink',name
 assert ob.hide_render==hidden or name in allowed,name
a['preservation']={'original_scene_object_transforms_unchanged':len(before),'original_geometry_datablocks_unchanged_except_GP_private_drawing':True,'oldcity_hidden_count':len(a['hidden_oldcity']),'near_material_change':'213 private14floorbindings only'};a['framing']=framing['regions'];(O/'audit.json').write_text(json.dumps(a,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('215_BUILD_DONE',flush=True)
