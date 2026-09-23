"""Native packed-soil relief proof. Geometric deposition/compaction model, not a physics solver.
References: DP-08 layered infrastructure, US-01 dark-soil-detail, US-02 structural-road-grit.
Study: embedded aggregate, shallow gathered soil and compressed depressions, no painted texture.
"""
import sys,math,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/ground-088'
if '--render' not in sys.argv:
 import numpy as np
 sys.path.insert(0,str(R/'tools'));from ground_heightfield_087 import Field
 n=801;axis=np.linspace(-3,3,n);X,Y=np.meshgrid(axis,axis);step=6/(n-1);rng=np.random.default_rng(88031)
 # Preserve a representative C macro profile, recentered rather than adding ground mass.
 field=Field('C');baseline=field(X-2.8,Y-3.0);baseline-=baseline.mean();H=baseline.copy()
 def stamp(cx,cy,rx,ry,a,amp,power=2,mode='add',phase=0):
  radius=max(rx,ry)*1.2;i0=max(0,int((cx-radius+3)/step));i1=min(n,int((cx+radius+3)/step)+2);j0=max(0,int((cy-radius+3)/step));j1=min(n,int((cy+radius+3)/step)+2)
  if i1<=i0 or j1<=j0:return
  dx=X[j0:j1,i0:i1]-cx;dy=Y[j0:j1,i0:i1]-cy;u=(dx*np.cos(a)+dy*np.sin(a))/rx;v=(-dx*np.sin(a)+dy*np.cos(a))/ry;theta=np.arctan2(v,u)
  rad=np.sqrt(u*u+v*v)/(1+.10*np.sin(3*theta+phase)+.06*np.sin(5*theta-phase))
  if mode=='grain':
   sides=4+(int(phase)%3);ang=(theta+phase+np.pi/sides)%(2*np.pi/sides)-np.pi/sides;boundary=np.cos(np.pi/sides)/np.cos(ang);rad/=boundary
   # Truncated angular aggregate: a flattened top with finite bevel shoulders, embedded in matrix.
   q=np.clip((1-rad)/.38,0,1);q=q*q*(3-2*q);q*=np.clip(.86+.11*u-.08*v,.55,1.0)
  else:q=np.maximum(0,1-rad*rad)**power
  H[j0:j1,i0:i1]+=amp*q
 # Shallow overlapping compacted lenses: elongated wear pockets, not evenly scattered hillocks.
 for j in range(38):
  stamp(rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(.15,.48),rng.uniform(.35,.9),rng.uniform(-.3,.3),rng.uniform(-.014,-.004),2.8,phase=j)
 # Irregular low depositional ridges beside compacted paths, each broken into connected segments.
 for j in range(9):
  cx=rng.uniform(-2.8,2.8);cy=rng.uniform(-2.4,2.4)
  for k in range(8):
   if rng.random()<.5:continue
   stamp(cx+.1*np.sin(k*.7+j),cy+(k-3.5)*.15,.15+.025*np.sin(k),.26,.2,rng.uniform(.0005,.0017),.9,phase=j+k)
 # Connected compacted clods at 8–25 cm; embedded, flattened with shoulders.
 for j in range(220):
  cx=rng.uniform(-3,3);cy=rng.uniform(-3,3);density=.35+.65*(.5+.5*np.sin(cx*1.5+cy*.8))
  if rng.random()>density:continue
  stamp(cx,cy,rng.uniform(.025,.07),rng.uniform(.08,.23),rng.uniform(-3.14,3.14),rng.uniform(.001,.004),1.4,phase=j)
 # Broad merged compaction patches retain fine grain but reduce its relief.
 compaction=np.ones_like(H)
 for j,(cx,cy,rx,ry) in enumerate([(-1.6,-1.1,.7,1.5),(-1.3,.4,.55,1.3),(.8,1.4,.8,.9),(1.2,2.1,.7,1.1),(1.5,-1.6,.6,1.2),(-2.6,1.7,.7,.7)]):
  dx=X-cx;dy=Y-cy;rad=(dx/rx)**2+(dy/ry)**2;patch=np.maximum(0,1-rad/(1+.23*np.sin(dy*3+dx*2+j))**2)**2;compaction*=1-.68*patch
 beforegrit=H.copy()
 # Fine aggregate is integral to the height field; patch-varying packing, no rock objects.
 for j in range(27000):
  cx=rng.uniform(-3,3);cy=rng.uniform(-3,3);ix=min(n-1,max(0,int((cx+3)/step)));iy=min(n-1,max(0,int((cy+3)/step)));loose=float(compaction[iy,ix]);pocket=float(np.clip((baseline[iy,ix]-beforegrit[iy,ix])/.012,0,1));packing=np.clip(.15+.65*loose+.20*pocket,.2,.95)
  if rng.random()>packing:continue
  r=rng.uniform(.012,.030);stamp(cx,cy,r,r*rng.uniform(.45,2.3),rng.uniform(-3.14,3.14),rng.uniform(.001,.004)*min(1,r/.018),.75,mode="grain",phase=j)
 H=beforegrit+(H-beforegrit)*compaction
 # Small pore/collapse cavities among grains create broken shadow rather than a smooth sand skin.
 for j in range(2900):
  stamp(rng.uniform(-3,3),rng.uniform(-3,3),rng.uniform(.009,.03),rng.uniform(.01,.035),rng.uniform(-3,3),rng.uniform(-.0035,-.0008),1.5,phase=j)
 H-=H.mean();np.savez_compressed(O/'detail-height.npz',axis=axis,baseline=baseline,candidate=H)
 (O/'detail-review.json').write_text(json.dumps({'status':'unreviewed','references':['DP-08','US-01','US-02'],'method':'Native geometric deposition/compaction-inspired heightfield; not a physical simulation','size_m':[6,6],'spacing_m':step,'vertices':n*n,'candidate_height_range_m':[float(H.min()),float(H.max())],'fixed':'camera, neutral clay, illumination; no shader bump or separate rocks'},indent=2));print('HEIGHT READY',H.min(),H.max())
else:
 import bpy,numpy as np
 from mathutils import Vector
 data=np.load(O/'detail-height.npz');a=data['axis'];X,Y=np.meshgrid(a,a);n=len(a);ids=np.arange(n*n).reshape(n,n);faces=np.column_stack([ids[:-1,:-1].ravel(),ids[:-1,1:].ravel(),ids[1:,1:].ravel(),ids[1:,:-1].ravel()])
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1600;s.render.resolution_y=1100;s.render.resolution_percentage=100
 mat=bpy.data.materials.new('Neutral matte geometry only');mat.diffuse_color=(.32,.32,.32,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.92
 w=bpy.data.worlds.new('Neutral studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1);w.node_tree.nodes['Background'].inputs[1].default_value=.45;s.world=w
 bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=2.3;sun.rotation_euler=(math.radians(63),math.radians(-12),math.radians(-35));sun.data.angle=.08
 bpy.ops.object.camera_add(location=(4,-5.6,4.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.5;s.camera=cam
 s.view_settings.view_transform='AgX'
 mesh=bpy.data.meshes.new('Native 7.5mm sampled packed soil');mesh.from_pydata(np.column_stack([X.ravel(),Y.ravel(),data['baseline'].ravel()]),[],faces.tolist());mesh.update();ob=bpy.data.objects.new('Continuous soil height surface',mesh);s.collection.objects.link(ob);ob.data.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=True
 for label in ['baseline','candidate']:
  co=np.column_stack([X.ravel(),Y.ravel(),data[label].ravel()]);mesh.vertices.foreach_set('co',co.ravel());mesh.update();s.render.filepath=str(O/f'detail-{label}.png');bpy.ops.render.render(write_still=True)
 cam.location=(1.3,-2.1,1.8);cam.rotation_euler=(Vector((.1,-.2,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.3;s.render.filepath=str(O/'detail-close.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'detail-scene.blend'));bpy.ops.render.render(write_still=True)
