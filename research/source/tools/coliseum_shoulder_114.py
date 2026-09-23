"""114 replace ambiguous cavity shelf by a rough attached shoulder; UCL-01.
Only tower10 front-right termination changes. Its tall left spine/rear stump stay intact.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix

def simplify_shoulder(collection):
 rad=75.;cy=347.;H=78.;step=math.tau/36;lean=Matrix.Rotation(math.radians(2),4,'X')
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 auth=Matrix.Translation(Vector((0,cy,0)))@lean@Matrix.Rotation(-math.pi+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted();aa=-math.pi+10*step
 def p(rr,u,z):
  a=aa+u/rad;b=1-.055*z/H;v=lean@Vector((rr*b*math.cos(a),rr*b*math.sin(a),z));return delta@Vector((v.x,cy+v.y,v.z))
 us=[-.12,.20,.62,1.03,1.44,1.86,2.28,2.70,3.2,4.8];rs=[73.85,74.50,75.15,75.80,76.45,77.10,77.75,78.40,79.20,81.0];W=len(us);D=len(rs);N=W*D
 # True nonplanar fracture across both axes. This removes the inclined plate silhouette.
 vs=[]
 for top in [False,True]:
  for k,r in enumerate(rs):
   for j,u in enumerate(us):
    z=82 if top else 72.25 + .16*math.sin(j*2.7+k*1.3)+.12*math.cos(j*1.2-k*2.3)
    vs.append(p(r,u,z))
 fs=[]
 for k in range(D-1):
  for j in range(W-1):
   i=k*W+j;fs.extend([(i,i+1,i+W+1),(i,i+W+1,i+W),(N+i,N+i+W+1,N+i+1),(N+i,N+i+W,N+i+W+1)])
 for j in range(W-1):fs.extend([(j,N+j,N+j+1,j+1),((D-1)*W+j,(D-1)*W+j+1,N+(D-1)*W+j+1,N+(D-1)*W+j)])
 for k in range(D-1):
  i=k*W;fs.append((i,i+W,N+i+W,N+i));i=k*W+W-1;fs.append((i,N+i,N+i+W,i+W))
 me=bpy.data.meshes.new('COL114 rough shoulder cutter');me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();cut=bpy.data.objects.new('COL114 rough shoulder cutter',me);collection.objects.link(cut)
 records=[];ca=[cut.matrix_world@Vector(v)for v in cut.bound_box]
 for ob in list(collection.objects):
  if ob.type!='MESH' or ob.get('bay')!=10 or 'Tower10' not in ob.name:continue
  oa=[ob.matrix_world@Vector(v)for v in ob.bound_box]
  if any(max(v[k]for v in ca)<min(v[k]for v in oa)or max(v[k]for v in oa)<min(v[k]for v in ca)for k in range(3)):continue
  old=ob.data;before=len(old.vertices);ob.data=old.copy();mod=ob.modifiers.new('114 remove shelf and form rough shoulder','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();after=len(bm.verts)
  if bad or (after and vol<=0):ob.data=old;bm.free();records.append({'object':ob.name,'rejected':True,'nonmanifold':bad});continue
  if not after or vol<.04:
   records.append({'object':ob.name,'removed_small_remnant':True});bm.free();bpy.data.objects.remove(ob,do_unlink=True);continue
  if after==before:ob.data=old;bm.free();continue
  bm.to_mesh(ob.data);bm.free();ob['localized_breakage']='114 attached rough masonry shoulder';records.append({'object':ob.name,'vertices':after,'nonmanifold':bad,'positive_volume':True})
 bpy.data.objects.remove(cut,do_unlink=True)
 return {'reference_ids':['UCL-01','DP-03','UX-01'],'changed':records,'target':'front-right core cavity floor and upper rib tip only','shoulder_height_authored_m':[71.97,72.53],'preserved':'left collapsed spine and taller rear stump; locked camera and all other geometry','native_geometry_only':True}
