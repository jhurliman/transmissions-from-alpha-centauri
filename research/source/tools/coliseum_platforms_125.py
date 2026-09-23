"""Inset low masonry thresholds with projecting coping; five percent of each actual arch height."""
import bpy,bmesh,math,ast
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from coliseum_arch_ratio_125 import mapping
R=Path(__file__).resolve().parents[1]
def apply(C):
 if any(o.get('125 inset platform')for o in C.objects):return {'already_applied':True}
 original,world,unpack=mapping();F=dict(zip(world.__code__.co_freevars,[x.cell_contents for x in world.__closure__]))['F'];P=dict(zip(original.__code__.co_freevars,[x.cell_contents for x in original.__closure__]))['P']
 tree=ast.parse((R/'tools/coliseum_linked_116.py').read_text());factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='group');ns={'bpy':bpy,'math':math};exec(compile(ast.Module(body=[factory],type_ignores=[]),'<platform warp>','exec'),ns);group=ns['group']();group.name='125 Shared inset platform ring warp';ids={s.name:s.identifier for s in group.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'}
 tunnels={(int(o['tier']),int(o['bay'])):o for o in C.objects if o.type=='MESH'and'loadbearing arch tunnel'in o.name};masters={};rows=[];deps=bpy.context.evaluated_depsgraph_get()
 for (tier,bay),owner in sorted(tunnels.items()):
  nominal_base=2.73+tier*18.33+.35;base=nominal_base+(1.25 if tier else 0);half=75*math.tau/36*.34*(1-float(owner.get('125 arch width reduction',owner.get('124 arch reduction',0))));height=(18.33-2.184-.35)*(1-float(owner.get('125 arch height reduction',owner.get('124 arch reduction',0))))-(base-nominal_base);h=height*.05;ac=-math.pi+(bay+.5)*math.tau/36
  supports=[o for o in C.objects if o.type=='MESH'and(o.name==f'COL110 T{tier} B{bay:02d} sill'or(tier>0 and o.name.startswith(f'COL110 T{tier-1} band{bay:02d} profile')))];sv=[];sf=[]
  for floor in supports:
   ev=floor.evaluated_get(deps);sm=ev.to_mesh();off=len(sv);sv.extend(ev.matrix_world@v.co for v in sm.vertices);sf.extend(tuple(off+i for i in f.vertices)for f in sm.polygons);ev.to_mesh_clear()
  support=BVHTree.FromPolygons(sv,sf);checks=[]
  for rr in [67.2,70.8,74.80]:
   for u in [-half*.92,0,half*.92]:
    pt=world(rr,ac+u/75,base);up=(world(rr,ac+u/75,base+.5)-pt).normalized();hit=support.ray_cast(pt+up*.12,-up,.28);gap=(pt-hit[0]).length if hit[0]is not None else None;checks.append(gap)
  if any(x is None or x>.04 for x in checks):raise RuntimeError('Unsupported platform '+str((tier,bay,checks)))
  mat=next((m for m in owner.data.materials if m and m.get('role')=='wall'),owner.data.materials[0]);key=(tier,round(half,5),round(h,5),mat.name)
  if key not in masters:
   # One closed stepped section: body supports coping; front face recessed behind engaged shafts.
   profile=[(67.,base-.035),(74.95,base-.035),(74.95,base+h*.82),(75.24,base+h*.82),(75.24,base+h),(66.90,base+h),(66.90,base+h*.82),(67.,base+h*.82)];N=len(profile);S=8;vs=[]
   for k in range(S+1):
    a=(-half-.10+(2*half+.20)*k/S)/75
    for rr,z in profile:
     r=rr*(1-.055*z/78);vs.append((r*math.cos(a),r*math.sin(a),z))
   fs=[tuple(range(N-1,-1,-1)),tuple(range(S*N,(S+1)*N))]
   for k in range(S):
    for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
   me=bpy.data.meshes.new(f'125 Shared threshold T{tier}');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(me);bm.free()
   if bad or vol<=0:raise RuntimeError('Invalid platform master')
   me.materials.append(mat);masters[key]=(me,bad,vol)
  me,bad,vol=masters[key];ob=bpy.data.objects.new(f'COL125 T{tier} B{bay:02d} inset masonry platform',me);C.objects.link(ob);M=Matrix.Rotation(ac,4,'Z');mod=ob.modifiers.new('125 Shared platform curvature','NODES');mod.node_group=group
  for prefix,T in [('Auth',M),('Original',P@M),('Final',F)]:
   for k in range(3):getattr(mod.properties.inputs,ids[prefix+str(k)]).value=tuple(T[k][j]for j in range(3))
   getattr(mod.properties.inputs,ids[prefix+'T']).value=tuple(T.translation)
  ob['bay']=bay;ob['tier']=tier;ob['coliseum_role']='wall';ob['feature']='recessed masonry threshold with projecting coping';ob['125 inset platform']=True;ob['platform clear-height ratio']=.05;ob['platform authored height']=h
  rows.append({'object':ob.name,'height_authored_m':h,'visible_floor_authored_z':base,'nominal_sill_authored_z':nominal_base,'actual_clear_height_before_platform':height,'opening_width_authored_m':2*half,'floor_contact_max_gap_m':max(checks),'floor_samples':9,'below_visible_floor_overlap_authored_m':.035,'front_coping_radius':75.24,'body_radius':74.95,'nonmanifold_edges':bad,'master_positive_volume':vol,'damaged_original_size':not bool(owner.get('125 arch width reduction'))})
 if len(rows)!=54:raise RuntimeError('Expected54 supported platforms, got'+str(len(rows)))
 return {'reference':'user f06fc8f1 low recessed masonry platform with coping','platforms':rows,'new_objects':len(rows),'shared_meshes':len(masters),'native_geometry_nodes':True,'height_ratio':.05,'existing_geometry_materials_unchanged':True,'damaged_bay_policy':'Use actual retained opening dimensions when ratio edit was conservatively skipped','clearance':'Coping radius75.24 sits behind shaft front; side ends overlap jamb masonry0.10 authoredm; body seats0.035m into visible structural floor; upper tiers use preceding band top, not buried nominal sill'}
