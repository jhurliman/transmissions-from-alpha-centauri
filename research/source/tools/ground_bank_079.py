"""Sparse native bank losses on existing soil crack boundaries only."""
import bpy,bmesh,random,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/bank-079'
def apply(scene):
 ground=bpy.data.objects['Street foundation']
 if ground.get('bank079'):return {}
 rng=random.Random(79019);C=ground.users_collection[0];ma=ground.data.materials[0];inner=ground.data.materials[1]
 bm=bmesh.new();bm.from_mesh(ground.data);candidates=[]
 for e in bm.edges:
  if len(e.link_faces)!=2 or {f.material_index for f in e.link_faces}!={0,1}:continue
  if any(abs(v.co.z+.04)>.001 for v in e.verts):continue
  p=(e.verts[0].co+e.verts[1].co)/2
  if not(-8<p.y<6 and abs(p.x)<6.7):continue
  d=e.verts[1].co-e.verts[0].co
  if d.length<.025:continue
  candidates.append((p.copy(),d.normalized()))
 bm.free();rng.shuffle(candidates);chosen=[]
 for p,d in candidates:
  if all((p-q[0]).length>.9 for q in chosen):chosen.append((p,d))
  if len(chosen)>=14:break
 bpy.context.view_layer.objects.active=ground
 for j,(p,d) in enumerate(chosen):
  r=rng.uniform(.16,.28);N=7;vs=[];side=Vector((-d.y,d.x,0))
  profile=[(-1,-.12),(-.7,-.30),(.2,-.25),(1,0),(.6,.24),(-.1,.40),(-.8,.16)]
  for along,out in profile:
   q=p+d*(along*r)+side*(out*r);vs.append((q.x,q.y,-.02))
  q=p+side*r*.03;vs.append((q.x,q.y,-.072));fs=[tuple(range(N-1,-1,-1))]+[(i,(i+1)%N,N) for i in range(N)]
  me=bpy.data.meshes.new('079 bank loss cutter');me.from_pydata(vs,[],fs);me.materials.append(ma);me.materials.append(inner)
  for f in me.polygons:f.material_index=1
  bb=bmesh.new();bb.from_mesh(me);bmesh.ops.recalc_face_normals(bb,faces=list(bb.faces));bb.to_mesh(me);bb.free();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob);mod=ground.modifiers.new('079 sparse chipped bank','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=ob;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(ob,do_unlink=True)
  # Few nearby grains share soil pigment and remain excluded from ink.
  for k in range(rng.randint(1,3)):
   off=Vector((-d.y,d.x,0))*rng.choice([-1,1])*rng.uniform(r*1.15,r*2.2);q=p+off+d*rng.uniform(-r,r);size=rng.uniform(.017,.035);verts=[(q.x+math.cos(a)*size,q.y+math.sin(a)*size,-.041) for a in [0,2.1,4.3]]+[(q.x+size*.25,q.y,-.04+size*.5)];mesh=bpy.data.meshes.new('079 earth bank grit');mesh.from_pydata(verts,[],[(0,2,1),(0,1,3),(1,2,3),(2,0,3)]);mesh.materials.append(inner);o=bpy.data.objects.new(mesh.name,mesh);C.objects.link(o)
 bb=bmesh.new();bb.from_mesh(ground.data);bmesh.ops.triangulate(bb,faces=list(bb.faces));bmesh.ops.recalc_face_normals(bb,faces=list(bb.faces));bb.to_mesh(ground.data);bb.free();ground['bank079']=True
 return {'boundary_candidates':len(candidates),'bank_losses':len(chosen),'seed':79019,'network_unchanged':True}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-078/scene.blend'));s=bpy.context.scene;records=apply(s);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'render.png');(O/'audit.json').write_text(json.dumps(records,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
