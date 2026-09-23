import bpy,bmesh,random,math
from mathutils import Vector
def apply(s):
 rng=random.Random(7804);g=bpy.data.objects['Street foundation'];C=bpy.data.collections['077 Soil fractures and mineral scatter'];ma=g.data.materials[0];inside=g.data.materials[1]
 for j,(x,ya,yb) in enumerate([(-3.7,-9,3.5),(2.4,-4.5,11),(-1.5,10,24.2),(4,14.5,30)]):
  pts=[];steps=int((yb-ya)/.32)
  for k in range(steps+1):
   t=k/steps;pts.append(Vector((x+.25*math.sin(t*6+j)+rng.uniform(-.025,.025),ya+(yb-ya)*t)))
  vs=[];fs=[]
  for k,p in enumerate(pts):
   d=pts[min(k+1,steps)]-pts[max(k-1,0)];d.normalize();side=Vector((-d.y,d.x));w=rng.uniform(.018,.05)*(.4+.6*abs(math.sin(k*.31+j)))
   vs.extend([(p.x-side.x*w,p.y-side.y*w,.025),(p.x+side.x*w,p.y+side.y*w,.025),(p.x,p.y,-.04-rng.uniform(.025,.05))])
  fs=[(2,1,0),(steps*3,steps*3+1,steps*3+2)]
  for k in range(steps):
   for t in range(3):fs.append((k*3+t,k*3+(t+1)%3,(k+1)*3+(t+1)%3,(k+1)*3+t))
  me=bpy.data.meshes.new('078 connecting earth cutter');me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(ma);me.materials.append(inside)
  for f in me.polygons:f.material_index=1
  o=bpy.data.objects.new(me.name,me);C.objects.link(o);bpy.context.view_layer.objects.active=g;m=g.modifiers.new('078 connecting rill','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=o;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(o,do_unlink=True);bm=bmesh.new();bm.from_mesh(g.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(g.data);bm.free()
 return 4
