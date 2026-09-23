"""Two whole-assembly native perspective experiments, reference UCL-01.
Camera and all non-landmark systems unchanged. Distinct from haze studies.
"""
import bpy,math,json,time,os,sys
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-perspective-115';O.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-114/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];cam=s.camera.matrix_world.copy()
lean=Matrix.Rotation(math.radians(2),4,'X');step=math.tau/36;anchor=next(o for o in C.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name);auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*step,4,'Z');delta=anchor.matrix_world@auth.inverted()
def p(a,z):
 rr=75*(1-.055*z/78);v=lean@Vector((rr*math.cos(a),rr*math.sin(a),z));return delta@Vector((v.x,347+v.y,v.z))
def project(v):
 q=world_to_camera_view(s,s.camera,v);return(q.x*1440,(1-q.y)*1082)
angles=[math.radians(-175+i*.5)for i in range(341)];top=[p(a,57.72)for a in angles];mid=[p(a,39.39)for a in angles];origin=p(-math.pi/2,39.39)
def measure(M,points=top,visible=True):
 xy=[project(M@v)for v in points];left=min(range(len(xy)),key=lambda i:xy[i][0]);right=max(range(len(xy)),key=lambda i:xy[i][0]);xy=xy[left:right+1]
 if visible:xy=[q for q in xy if 550<=q[0]<=930]
 lo=min(range(len(xy)),key=lambda i:xy[i][1]);width=xy[-1][0]-xy[0][0]
 return {'left_rise':(xy[0][1]-xy[lo][1])/width,'right_descent':(xy[-1][1]-xy[lo][1])/width,'apex_fraction':(xy[lo][0]-xy[0][0])/width,'span_px':width,'apex_xy':xy[lo],'points':[xy[round(i*(len(xy)-1)/8)]for i in range(9)]}
base=measure(Matrix.Identity(4));base_mid=measure(Matrix.Identity(4),mid);base_raw=measure(Matrix.Identity(4),visible=False)
def fit(M):
 for _ in range(3):
  q=measure(M,visible=False);sx=base_raw['span_px']/q['span_px'];P=Matrix.Identity(4);P[0][0]=sx;P[0][3]=origin.x*(1-sx);M=P@M
  q=measure(M,visible=False);dx=720-(q['points'][0][0]+q['points'][-1][0])/2;dy=base_raw['apex_xy'][1]-q['apex_xy'][1]
  v=M@p(-math.pi/2,57.72);c=project(v);jx=project(v+Vector((1,0,0)))[0]-c[0];jz=project(v+Vector((0,0,1)))[1]-c[1];M=Matrix.Translation(Vector((dx/jx,0,dy/jz)))@M
 front_base=p(-math.pi/2,0);rise=(M@front_base).z-front_base.z
 if rise>0:M=Matrix.Translation(Vector((0,0,-rise)))@M
 return M
def score(M):
 q=measure(M);return((q['left_rise']-.0523)**2+(q['right_descent']-.1634)**2)*12+(q['apex_fraction']-.327)**2
world_bounds=[o.matrix_world@Vector(v)for o in C.objects if o.type=='MESH'for v in o.bound_box]
# Actual XY convex hull avoids impossible extrema from loose rotated bounding-box corners.
points=sorted(set((round(w.x,5),round(w.y,5))for o in C.objects if o.type=='MESH'for v in o.data.vertices for w in [o.matrix_world@v.co]))
def cross(o,a,b):return(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
lower=[]
for q in points:
 while len(lower)>=2 and cross(lower[-2],lower[-1],q)<=0:lower.pop()
 lower.append(q)
upper=[]
for q in reversed(points):
 while len(upper)>=2 and cross(upper[-2],upper[-1],q)<=0:upper.pop()
 upper.append(q)
hull=lower[:-1]+upper[:-1]
def nearest(M):
 if abs(M[1][2])<.000001:return min(M[1][0]*x+M[1][1]*y+M[1][3]for x,y in hull)
 return min((M@v).y for v in world_bounds)
solutions=[]
for sy in [2,2.5,3,3.5,4,4.5,5,5.5,6]:
 for shear in [.25,.5,.75,1,1.25,1.5,1.75,2]:
  M=Matrix.Identity(4);M[1][1]=sy;M[1][0]=shear;M[1][3]=origin.y*(1-sy)-origin.x*shear;M=fit(M);penalty=100 if nearest(M)<176 else 0;solutions.append((score(M)+penalty,'A',{'depth_scale':sy,'depth_shear':shear},M))
for pitch in [-6,-10,-14,-18,-22,-26]:
 for roll in [2,4,6,8,10,12]:
  M=Matrix.Translation(origin)@Matrix.Rotation(math.radians(roll),4,'Y')@Matrix.Rotation(math.radians(pitch),4,'X')@Matrix.Translation(-origin);M=fit(M);penalty=100 if nearest(M)<176 else 0;solutions.append((score(M)+penalty,'B',{'pitch_degrees':pitch,'right_down_tilt_degrees':roll},M))
chosen=[min((x for x in solutions if x[1]==label),key=lambda x:x[0])for label in ['A','B']]
audit={'reference':{'id':'UCL-01','top_band_points_crop_px':[[100,400],[300,350],[600,320],[850,333],[1100,373],[1300,430],[1500,500],[1630,570]],'left_rise_fraction':.0523,'right_descent_fraction':.1634,'apex_fraction':.327},'visible_band_fit_window_px':[550,930],'baseline_top':base,'baseline_middle':base_mid,'variants':[]}
for error,label,settings,M in chosen:
 q=measure(M);qm=measure(M,mid);entry={'label':label,'settings':settings,'fit_error':error,'nearest_world_y':nearest(M),'front_base_z_before':p(-math.pi/2,0).z,'front_base_z_after':(M@p(-math.pi/2,0)).z,'matrix':[list(row)for row in M],'top':q,'middle':qm,'tower_screen_lean':[]}
 for a in [math.radians(-120),math.radians(-90),math.radians(-60)]:
  bot=project(M@p(a,10));tip=project(M@p(a,75));entry['tower_screen_lean'].append(math.degrees(math.atan2(tip[0]-bot[0],bot[1]-tip[1])))
 audit['variants'].append(entry)
(O/'measurements.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if os.environ.get('PERSPECTIVE_RENDER')=='1':
 sys.path.insert(0,str(R/'tools'))
 from coliseum_haze_115 import apply_haze
 from coliseum_materials_115 import apply_materials
 apply_haze(3,19);apply_materials(C)
 oldink=bpy.data.objects.get('110 Landmark contact ink')
 if oldink:oldink.hide_render=True
 original={o.name:o.matrix_world.copy()for o in C.objects}
 import numpy as np
 parents=[]
 for name in ['115 Assembly left rotation','115 Assembly stretch','115 Assembly right rotation']:
  ob=bpy.data.objects.new(name,None);s.collection.objects.link(ob);parents.append(ob)
 parents[1].parent=parents[0];parents[2].parent=parents[1]
 for q in parents:q.matrix_parent_inverse=Matrix.Identity(4)
 def exact_affine(M):
  U,S,V=np.linalg.svd(np.array([list(row)[:3]for row in M][:3]))
  if np.linalg.det(U)<0:U[:,-1]*=-1;S[-1]*=-1
  if np.linalg.det(V)<0:V[-1,:]*=-1;S[-1]*=-1
  left=Matrix(U.tolist()).to_4x4();left.translation=M.translation
  parents[0].matrix_basis=left;parents[1].matrix_basis=Matrix.Diagonal((float(S[0]),float(S[1]),float(S[2]),1));parents[2].matrix_basis=Matrix(V.tolist()).to_4x4()
  for o in C.objects:o.parent=parents[2];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=original[o.name]
  bpy.context.view_layer.update()
  error=0
  for o in C.objects:
   if o.type!='MESH' or not o.data.vertices:continue
   for v in [o.data.vertices[0],o.data.vertices[len(o.data.vertices)//2],o.data.vertices[-1]]:error=max(error,((o.matrix_world@v.co)-(M@original[o.name]@v.co)).length)
  return error
 def anchor_weathering(M):
  inv=M.inverted();materials={m for o in C.objects if o.type=='MESH' for m in o.data.materials}
  for mat in materials:
   if not mat.use_nodes:continue
   n=mat.node_tree.nodes;l=mat.node_tree.links;unscale=next((q for q in n if q.label=='Preserve authored weathering scale'),None)
   if not unscale:continue
   geo=next(q for q in n if q.bl_idname=='ShaderNodeNewGeometry');combine=n.get('115 Inverse assembly coordinates')
   if not combine:
    combine=n.new('ShaderNodeCombineXYZ');combine.name='115 Inverse assembly coordinates'
    for k in range(3):
     dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.name=f'115 Inverse row{k}';l.new(geo.outputs['Position'],dot.inputs[0]);offset=n.new('ShaderNodeMath');offset.operation='ADD';offset.name=f'115 Inverse offset{k}';l.new(dot.outputs['Value'],offset.inputs[0]);l.new(offset.outputs[0],combine.inputs[k])
    l.new(combine.outputs[0],unscale.inputs[0])
   for k in range(3):n[f'115 Inverse row{k}'].inputs[1].default_value=tuple(inv[k][j]for j in range(3));n[f'115 Inverse offset{k}'].inputs[1].default_value=inv[k][3]
 for error,label,settings,M in chosen:
  anchor_weathering(M)
  error_exact=exact_affine(M)
  for o in C.objects:
   if o.type not in ['MESH','LIGHT']:o.hide_render=True
  entry=next(q for q in audit['variants']if q['label']==label);entry['affine_max_sample_error_m']=error_exact;entry['affine_representation']='three-parent SVD hierarchy, linked meshes preserved';(O/'measurements.json').write_text(json.dumps(audit,indent=2));assert error_exact<.002,error_exact
  bpy.context.view_layer.update();assert s.camera.matrix_world==cam
  folder=O/label;folder.mkdir(exist_ok=True);s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(folder/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'));bpy.ops.render.render(write_still=True)
