"""Small, unequal native chips on retained broken crown contours."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from colosseum_arch_fractures_232 import subtract,clip_contacts,bbox,mesh_tree

def apply(scene):
 assert not scene.get('roofline242_applied')
 names=['COL110 U2 fractured upper wall R','COL110 U6 fractured upper wall R','COL110 U7 fractured upper wall R','COL110 U8 fractured upper wall L','COL110 U11 fractured upper wall L']
 cam=scene.camera;origin=cam.matrix_world.translation;rot=cam.matrix_world.to_3x3();frame=cam.data.view_frame(scene=scene);lx=min(v.x for v in frame);hx=max(v.x for v in frame);ly=min(v.y for v in frame);hy=max(v.y for v in frame);z=frame[0].z
 def ray(x,y):return(rot@Vector((lx+(hx-lx)*x/3840,hy-(hy-ly)*y/2885,z))).normalized()
 from bpy_extras.object_utils import world_to_camera_view
 dg=bpy.context.evaluated_depsgraph_get();prepared=[];cuts=[]
 for ni,name in enumerate(names):
  ob=bpy.data.objects[name];src=bpy.data.meshes.new_from_object(ob.evaluated_get(dg),depsgraph=dg);M=ob.matrix_world.copy();tree=mesh_tree(src,M);pp=[world_to_camera_view(scene,cam,M@v.co)for v in src.vertices];xlo=min(v.x for v in pp)*3840;xhi=max(v.x for v in pp)*3840;ytop=(1-max(v.y for v in pp))*2885;ybot=(1-min(v.y for v in pp))*2885;cc=[]
  for ci,f in enumerate(([.32,.72]if ni%2==0 else[.49])):
   x=xlo+(xhi-xlo)*f;hit=None
   for yy in range(math.floor(ytop),math.ceil(ybot)):
    h=tree.ray_cast(origin,ray(x,yy),1000)
    if h[0]is not None:hit=h;break
   if hit is None:continue
   center=hit[0];normal=(origin-center).normalized();normal.z=0;normal.normalize()
   def point(px,py):
    d=ray(px,py);return origin+d*((center-origin).dot(normal)/d.dot(normal))
   # Unequal stepped V notches: 2–5 native pixels depth, quiet spans between.
   w=[4.8,6.2,3.9,5.6,4.4,6.8][ni];dep=[3.2,4.3,2.6,3.8,4.7,3.1][ni]
   poly=[(x-w,yy-9),(x+w,yy-9),(x+w*.6,yy+.4),(x+w*.12,yy+dep*.65),(x-w*.23,yy+dep),(x-w*.68,yy+.6)]
   N=len(poly);vs=[point(a,b)+normal*d for d in(3,-12)for a,b in poly];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)]
   me=bpy.data.meshes.new('242 chipped roof negative solid');me.from_pydata(vs,[],fs);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
   c={'id':f'roof-{ni}-{ci}','mesh':me,'tree':mesh_tree(me,Matrix.Identity(4)),'box':bbox(vs),'native_pixel_anchor':[x,yy],'native_depth_pixels':dep};cuts.append(c);cc.append(c)
  if cc:prepared.append((ob,src,M,cc))
 work=bpy.data.scenes.new('242 isolated roof chip workspace');C=bpy.data.collections.new('242 temporary chips');work.collection.children.link(C);bpy.context.window.scene=work;rows=[];owners=[]
 try:
  for ob,src,M,cc in prepared:
   result=subtract(ob,cc,C,src,M)
   if result:row,owner=result;rows.append(row);owners.append(owner)
 finally:
  bpy.context.window.scene=scene;bpy.data.scenes.remove(work);bpy.data.collections.remove(C)
 ink=clip_contacts(scene,owners,cuts)
 scene['roofline242_applied']=True
 return {'targets':rows,'cuts':[{k:v for k,v in c.items()if k not in('mesh','tree')}for c in cuts],'contact_cleanup':ink,'method':'subtractive stepped micro-chips; original world-position attributes interpolated by proven232 subtract; native normals and unaffected source triangles retained','status':'Geometry validated; actual integrated render required'}
