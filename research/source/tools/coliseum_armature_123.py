"""UCL user exposed armature: anchored bent framing on Tower10's broken right shoulder."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def apply(C):
 if any(o.get('123 exposed armature') for o in C.objects):return {'already_applied':True}
 anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
 anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P
 def p(rr,u,z):
  rr=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
  if rr<outer:rr=outer+.55*(rr-outer)
  a=-math.pi/2+.68*(-math.pi+10*math.tau/36+u/75+math.pi/2);return F@Vector((rr*math.cos(a),rr*math.sin(a),z))
 vs=[];fs=[]
 for o in C.objects:
  if o.type=='MESH' and o.name.startswith('COL110 Tower10 core'):
   off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in f.vertices)for f in o.data.polygons)
 tree=BVHTree.FromPolygons(vs,fs);mats=[]
 for label,h in [('steel','403b46'),('worn warm edge','75625f'),('dark return','292631')]:
  m=bpy.data.materials.new('123 Armature '+label);m.use_nodes=True;n=m.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');dif=n.new('ShaderNodeBsdfDiffuse');mix=n.new('ShaderNodeMixShader');col=tuple((int(h[i:i+2],16)/255)**2.2 for i in(0,2,4))+(1,);em.inputs['Color'].default_value=col;dif.inputs['Color'].default_value=col;mix.inputs[0].default_value=.16;m.node_tree.links.new(em.outputs[0],mix.inputs[1]);m.node_tree.links.new(dif.outputs[0],mix.inputs[2]);m.node_tree.links.new(mix.outputs[0],out.inputs['Surface']);mats.append(m)
 made=[];records=[]
 def tube(label,points,radius=.069):
  points=[Vector(v)for v in points];vv=[];N=6
  for k,pt in enumerate(points):
   t=(points[min(k+1,len(points)-1)]-points[max(0,k-1)]).normalized();axis=Vector((1,0,0));axis=(axis-t*axis.dot(t)).normalized();other=t.cross(axis).normalized()
   vv.extend(pt+radius*(math.cos(math.tau*j/N)*axis+math.sin(math.tau*j/N)*other)for j in range(N))
  faces=[tuple(range(N-1,-1,-1)),tuple(range((len(points)-1)*N,len(points)*N))]
  for k in range(len(points)-1):
   for j in range(N):faces.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
  me=bpy.data.meshes.new('123 '+label);me.from_pydata(vv,[],faces);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new('COL123 Tower10 '+label,me);C.objects.link(ob)
  for m in mats:me.materials.append(m)
  light=Vector((-.45,-.7,1)).normalized()
  for f in me.polygons:f.material_index=1 if f.normal.dot(light)>.64 else(2 if f.normal.dot(light)<-.25 else 0)
  ob['bay']=10;ob['tier']=3;ob['coliseum_role']='detail';ob['feature']='embedded exposed bent metal frame';ob['123 exposed armature']=True;made.append(ob);return ob
 # Four unequal survivors around two sides of the missing corner, with bent ends.
 specs=[(77.65,.45,4.25,-.18,.05),(77.65,1.27,3.5,.12,-.03),(77.55,2.12,4.55,-.22,-.08),(75.95,2.02,3.55,.18,.20)]
 tops=[];ties=[]
 for k,(rr,u,h,du,dr)in enumerate(specs):
  start=p(rr,u,80);end=p(rr,u,65);up=(start-end).normalized();hit=tree.ray_cast(start,-up,(start-end).length)
  if hit[0] is None:raise RuntimeError('No masonry anchor for armature '+str(k))
  base=hit[0];z=(F.inverted()@base).z
  if not 71.4<z<73.2:raise RuntimeError('Armature hit wrong crown level '+str(z))
  path=[base-up*.30,p(rr,u,z+h*.55),p(rr+dr,u+du*.4,z+h*.83),p(rr+dr,u+du,z+h)]
  tube('bent upright'+str(k),path);tops.append(path[-1]);ties.append(path[-2].lerp(path[-1],.22));records.append({'upright':k,'anchor_world':list(base),'anchor_authored_z':z,'embedded_world_m':.30,'tip_world':list(path[-1])})
 # Sagged surviving ties connect the framing; one section is deliberately missing.
 for a,b in [(0,1),(1,2),(2,3)]:
  left=ties[a];right=ties[b];mid=left.lerp(right,.54)+Vector((.05,0,-.16));tube('buckled tie'+str(a),[left,mid,right],.060)
 return {'target':'COL110 Tower10 core; exposed front-right broken shoulder','reference':'user462c891c exposed metal crown crop','new_objects':len(made),'anchors':records,'existing_geometry_unchanged':True,'local_silhouette_addition':'Four bent survivors and three sagged ties, below existing tall left spine','native_meshes':True}
