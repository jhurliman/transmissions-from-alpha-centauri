import bpy,math,json,time
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin']
anchorname=next(o.name for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name)
with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=[anchorname]
anchor=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_basis@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(anchor)
A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P;Fi=F.inverted();j=8;ac=-math.pi+(j+.5)*math.tau/36;zones=[(3.55,65.0,2.0,2.1),(4.65,62.9,1.0,1.8)];new=[];changed=[];audit=[]
mats={}
for instance in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=instance.object
 if ob.hide_render or any(w in ob.name.lower() for w in ['dust volume','cloud','sky']):continue
 if ob.type=='MESH' and ob.get('coliseum_role')not in mats:mats[ob.get('coliseum_role')]=list(ob.data.materials)
def p(rr,u,z):
 r=rr*(1-.055*z/78);outer=75*(1-.055*z/78)
 if r<outer:r=outer+.55*(r-outer)
 a=-math.pi/2+.68*(ac+u/75+math.pi/2);return F@Vector((r*math.cos(a),r*math.sin(a),z))
vs=[];fs=[];names=[]
for instance in bpy.context.evaluated_depsgraph_get().object_instances:
 ob=instance.object
 if ob.hide_render or any(w in ob.name.lower() for w in ['dust volume','cloud','sky']):continue
 if ob.type!='MESH':continue
 off=len(vs);vs.extend(instance.matrix_world@v.co for v in ob.data.vertices);fs.extend(tuple(off+i for i in f.vertices)for f in ob.data.polygons);names.extend([ob.name]*len(ob.data.polygons))
tree=BVHTree.FromPolygons(vs,fs);cam=bpy.context.scene.camera.matrix_world.translation;rows=[]
for u in [2.8,3.55,4.2]:
 for z in [64.3,65,65.6]:
  target=p(75,u,z);d=(target-cam).normalized();at=cam.copy();hits=[]
  for k in range(8):
   hit=tree.ray_cast(at,d)
   if hit[0]is None:break
   q=Fi@hit[0];hits.append({'object':names[hit[2]],'author_z':q.z,'world':list(hit[0])});at=hit[0]+d*.002
  rows.append({'u':u,'z':z,'hits':hits})
print(json.dumps(rows,indent=2));(R/'art/studies/coliseum-119/breach-fullscene-rays.json').write_text(json.dumps(rows,indent=2))
