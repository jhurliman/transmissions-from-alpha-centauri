"""UCL01/UCL02/DP03: bounded convex negative chips on a clean volumetric R foundation."""
import bpy,bmesh,math,random,json,sys
from pathlib import Path
from mathutils import Matrix,Vector,geometry
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-127/fracture-solid-fine';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
from coliseum_fine_fracture_125 import tree
NAME='COL110 U8 fractured upper wall R'
def apply(C):
 ob=bpy.data.objects[NAME];base=ob.data;source_tree,source_vs,source_ts=tree(ob);base.calc_loop_triangles();source_faces=[t.polygon_index for t in base.loop_triangles];orig=[d.vector.copy()for d in base.attributes['115 Original world position'].data]
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-111/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=Y@A@P;ac=-math.pi+8.5*math.tau/36
 ctrl=json.loads((R/'art/studies/coliseum-126/fracture-seed/audit.json').read_text())['records'][1]['original_control_profile']
 def height(u):
  for(a,x),(b,y)in zip(ctrl,ctrl[1:]):
   if a<=u<=b:return x+(y-x)*(u-a)/(b-a)
  raise ValueError(u)
 def point(rr,u,z):
  outer=75*(1-.055*z/78);r=rr*(1-.055*z/78)
  if r<outer:r=outer+.55*(r-outer)
  a=-math.pi/2+.68*(ac+u/75+math.pi/2);return F@Vector((r*math.cos(a),r*math.sin(a),z))
 rng=random.Random(12780);candidates=[]
 for rr,us in [(67,[1.48,1.87,2.95,3.23,4.14,4.46,5.32,5.66,6.12]),(75,[1.66,3.09,4.27,5.48,6.22])]:
  for u in us:
   z=height(u);w=point(rr,u,z);hit=source_tree.find_nearest(w)
   if hit[3]>.24:continue
   tang=(point(rr,u+.015,z)-w).normalized();rad=(point(rr+.015,u,z)-w).normalized();up=(F.to_3x3()@Vector((0,0,1))).normalized();size=rng.uniform(.17,.31);candidates.append((hit[0],tang,rad,up,size,'crown'))
 # Sparse shallow recesses on the broad exposed crown core, not attached chips.
 for rr,u in [(70.4,4.92),(72.1,5.54),(71.0,3.95),(72.7,2.1)]:
  w=point(rr,u,height(u));hit=source_tree.find_nearest(w)
  if hit[3]>.20:continue
  n=hit[1];t=(point(rr,u+.02,height(u))-w).normalized();v=n.cross(t).normalized();candidates.append((hit[0]+n*.08,t,v,n,rng.uniform(.14,.22),'core'))
 rows=[];allvs=[];allfs=[];boxes=[]
 for index,(center,t,r,z,size,kind)in enumerate(candidates):
  # Irregular convex eight-corner chisel, oblique shoulders and unequal depth.
  coords=[]
  for a,b,c in [(-1,-1,-1),(-1,1,-1),(1,1,-1),(1,-1,-1),(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]:
   coords.append(center+t*a*size*rng.uniform(.65,1.2)+r*b*size*rng.uniform(.45,.85)+z*c*size*rng.uniform(.65,1.15))
  bm=bmesh.new();[bm.verts.new(v)for v in coords];bmesh.ops.convex_hull(bm,input=list(bm.verts));cm=bpy.data.meshes.new('127 convex cutter');bm.to_mesh(cm);bm.free();offset=len(allvs);allvs.extend(v.co.copy()for v in cm.vertices);allfs.extend(tuple(offset+i for i in f.vertices)for f in cm.polygons);boxes.append(([min(v[k]for v in coords)-.06 for k in range(3)],[max(v[k]for v in coords)+.06 for k in range(3)]));rows.append({'index':index,'kind':kind,'center':list(center),'size':size});bpy.data.meshes.remove(cm)
 cm=bpy.data.meshes.new('127 combined negative volumes');cm.from_pydata(allvs,[],allfs);cm.update();cut=bpy.data.objects.new('127 combined cutter',cm);C.objects.link(cut)
 bpy.context.view_layer.objects.active=cut;rm=cut.modifiers.new('127 unified cutter solid','REMESH');rm.mode='VOXEL';rm.voxel_size=.025;rm.adaptivity=0.;bpy.ops.object.modifier_apply(modifier=rm.name)
 ob.data=base.copy();bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('127 true negative volumes','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 # Intermediate Boolean polygons are not a deliverable. Reconstruct the resulting solid once.
 rm=ob.modifiers.new('127 final closed solid','REMESH');rm.mode='VOXEL';rm.voxel_size=.02;rm.adaptivity=0.;rm.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=rm.name);check=topology(ob)
 if check['nonmanifold']or check['strict_crossings']or check['volume']<=0:ob.data=base;raise RuntimeError('Invalid final solid '+str(check))
 print('FINAL_SOLID',check,flush=True)
 finaltree,_,_=tree(ob);outside=max((finaltree.find_nearest(v)[3]for v in source_vs if not any(all(lo[k]<=v[k]<=hi[k]for k in range(3))for lo,hi in boxes)),default=0)
 if outside>.08:print('HOLD outside reconstruction requires visual review',outside,flush=True)
 m=ob.data;attr=m.attributes.get('115 Original world position')or m.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
 for v in m.vertices:
  hit=source_tree.find_nearest(ob.matrix_world@v.co);tri=source_ts[hit[2]];attr.data[v.index].vector=geometry.barycentric_transform(hit[0],*[source_vs[i]for i in tri],*[orig[i]for i in tri])
 core=m.attributes.get('117 Exposed core')or m.attributes.new('117 Exposed core','FLOAT','FACE');recess=m.attributes.get('118 Recess interior')or m.attributes.new('118 Recess interior','FLOAT','FACE');core_slot=next(i for i,ma in enumerate(m.materials)if ma and ma.name.startswith('117 Exposed masonry core'))
 for f in m.polygons:
  hit=source_tree.find_nearest(ob.matrix_world@f.center)
  index=source_faces[hit[2]];core.data[f.index].value=base.attributes['117 Exposed core'].data[index].value;recess.data[f.index].value=base.attributes['118 Recess interior'].data[index].value;f.material_index=base.polygons[index].material_index
  if hit[3]>.055:core.data[f.index].value=1.;recess.data[f.index].value=0.;f.material_index=core_slot
 ob['127 convex negative fracture']=len(rows)
 return {'references':['UCL-01','UCL-02','DP-03'],'method':'native bounded convex negative cuts on validated voxel foundation; no displaced surfaces','cuts':rows,'outside_reconstruction_max_m':outside,'voxel_tolerance':.02,'outside_numeric_guard_passed':outside<=.08,'final':topology(ob),'source_foundation':'126 volumetric; documented thin-surface removal remains pending visual review','production_integrated':False}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-126/volumetric/geometry.blend'));bpy.ops.wm.save_as_mainfile(filepath=str(O/'baseline.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print('COMPLETE',flush=True)
