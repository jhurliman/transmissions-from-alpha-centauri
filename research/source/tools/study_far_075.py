"""Editable fixed-camera distant city kit; study only, accepted alley untouched."""
import bpy, math, random, json, bmesh
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/studies/far-075';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-074/scene.blend'));s=bpy.context.scene;rng=random.Random(7519)
C=bpy.data.collections.new('075 Distant architecture study');s.collection.children.link(C)
hidden=[]
for o in bpy.data.collections['013 Long ruined city - depth layers'].objects:
 if 'collapsed rubble' not in o.name:o.hide_render=True;hidden.append(o.name)
def lin(h):
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in [int(h[i:i+2],16)/255 for i in (0,2,4)])
def material(name,col,shade=.72):
 m=bpy.data.materials.new('FAR075 '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();n=nt.nodes;l=nt.links
 out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs['Surface'])
 geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.38,-.67,.64);l.new(geo.outputs['Normal'],dot.inputs[0])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT';c=lin(col);ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=tuple(v*shade for v in c)+(1,);ramp.color_ramp.elements[1].position=.55;ramp.color_ramp.elements[1].color=(*c,1);l.new(dot.outputs['Value'],ramp.inputs[0]);l.new(ramp.outputs[0],em.inputs[0]);return m
palette=[('3f485f','484058','71544d'),('505367','605162','806159'),('686175','776170','947364'),('7c6e7d','836f7b','9d7e6e')]
materials=[]
for layer in range(4):
 materials.append([material(f'layer{layer} family{k}',c,.68+layer*.045) for k,c in enumerate(palette[layer])]+[material(f'layer{layer} recess',['262d42','3f3e53','58485e','6d5d6b'][layer]),material(f'layer{layer} seam',['485064','605869','756476','87717e'][layer]),material(f'layer{layer} highlight',['9397a4','9c94a0','a99ba3','b1a1a5'][layer])])
# Carry approved material language into the near distant blocks; keep detailed graphs out of the farthest layers.
for index in [0,1]:
 for family,key in enumerate(['left_middle','left_rear','right_front']):
  old=bpy.data.materials.get('042 Street coating | '+key)
  if old:
   copied=old.copy();copied.name='FAR075 approved finish '+str(index)+' '+key;materials[index][family]=copied
metal_src=next((m for m in bpy.data.materials if m.name.startswith('PIP |') and 'body' in m.name.lower()),None)
if metal_src is None:metal_src=bpy.data.materials.get('DUCT | muted blue-gray sheet')
if metal_src:
 for index in [0,1]:
  copy=metal_src.copy();copy.name='FAR075 steel '+str(index);materials[index][5]=copy
def mesh(name,vs,fs,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();ob=bpy.data.objects.new('FAR075 '+name,me);C.objects.link(ob);return ob
def box(name,loc,dims,m):
 x,y,z=loc;a,b,c=[q/2 for q in dims];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m)
def prism(name,x,y,w,profile,m):
 N=len(profile);vs=[(x+u,y+v,z) for u in [-w/2,w/2] for v,z in profile];return mesh(name,vs,[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)],m)
def pipe(name,pts,r,m):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=r;cu.resolution_u=2;cu.bevel_resolution=1;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for v,p in zip(sp.points,pts):v.co=(*p,1)
 ob=bpy.data.objects.new('FAR075 '+name,cu);cu.materials.append(m);C.objects.link(ob)
audit=[]
def building(x,y,w,d,h,family,layer):
 first=set(C.objects);mats=materials[min(layer//2,3)];m=mats[family];recess,seam,hi=mats[3:];floor=3.2
 # Original three compatible profiles: rake-foot slab, stepped service tower, cantilevered gallery.
 if family==0:
  prism('raked slab',x,y,w,[(0,0),(d,0),(d,h),(.8,h),(.8,3.4),(-.7,1.8)],m);front=.8
 elif family==1:
  prof=[(-w/2,0),(w/2,0),(w/2,h-.85),(w/2-.85,h),(-w/2,h)];N=len(prof)
  mesh('chamfered service tower',[(x+u,y+v,z) for v in [0,d] for u,z in prof],[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)],m);front=0
  box('offset crown',(x+w*.16,y+d*.54,h+.6),(w*.68,d*.70,1.2),m)
  for xx in [x-w*.43,x+w*.31]:box('pier',(xx,y-.15,h*.47),(.38,.34,h*.94),seam)
 else:
  prism('gallery slab',x,y,w,[(.55,0),(d,0),(d,h),(-.6,h),(-.6,h*.43),(.55,h*.43-1.15)],m);front=-.6
 # Intentional panel and window groups, no tiny bolts or high-frequency surface noise.
 levels=max(1,int(h/floor));cols=max(1,int(w/2.6));bw=w/cols
 for row in range(1,levels):
  z=row*floor+.7
  if family==2 and z<h*.43:continue
  for col in range(cols):
   xx=x-w/2+(col+.5)*bw
   if (row*3+col+family)%7==0:continue
   ww=bw*.60;hh=1.5 if family!=2 else 1.05
   box('window recessed field',(xx,y+front-.028,z),(ww,.06,hh),recess)
   if layer<4:
    box('slider divider',(xx+ww*.05,y+front-.08,z),(.07,.08,hh),m)
    prism('sloping window kick',xx,y+front,ww,[(-.06,z-hh/2),(-.21,z-hh/2-.33),(.0,z-hh/2-.33)],m)
  if row%2==family%2 or family==2:
   box('story trim',(x,y+front-.14,z-1.0),(w+.12,.25,.15 if layer<4 else .23),hi)
 # Broad panel changes, never checkerboard small tiling.
 if family!=2:
  box('service panel',(x+w*.22,y+front-.06,h*.32),(w*.32,.08,h*.18),seam)
 if family==1 or (layer<3 and family==0):
  xx=x-w*.31;rad=max(.16,w*.038);z0=.8;z1=h*.88;off=front-.46
  pipe('closed service riser',[(xx,y+front+.08,z0),(xx,y+off,z0+.42),(xx,y+off,z1-.42),(xx,y+front+.08,z1)],rad,seam)
  if layer<4:
   for z in [h*.23,h*.56,h*.78]:box('service strap',(xx,y+off,z),(rad*2.6,.18,.14),hi)
 # Roof receivers and sloping cheeks preserve silhouette even after detail removal.
 if family!=1:
  box('roof receiver',(x-w*.22,y+d*.48,h+.45),(w*.26,d*.45,.9),seam)
 # Broad angled corner piers and offset facade strips; at distance these carry the alley language.
 if layer<4:
  for q,xx in enumerate([x-w*.47,x+w*.46]):
   prism('chamfered corner pier',xx,y,w*.09,[(front-.18,0),(front+.11,0),(front+.11,h*.96),(front-.18,h*.96),(front-.18,3.1),(front-.48,2.5),(front-.48,.4)],hi if q else seam)
  # Low-frequency vertical weathering shapes as actual relief-free veneer strips.
  for q in range(3):
   xx=x+rng.uniform(-w*.36,w*.36);zz=rng.uniform(1,h*.7)
   box('tonal service strip',(xx,y+front-.065,zz),(.10 if q else .20,.035,rng.uniform(.6,2.5)),seam)
 if layer<3:
  # Each receiver is deliberately connected to two-ended vertical service loops.
  for k in range(1 if family!=1 else 2):
   xx=x-w*.33+k*w*.26;zz=h*(.72+.05*k);offset=front-.45
   box('projecting receiver',(xx,y+front-.18,zz),(.42,.52,.60),seam)
   pipe('primary service loop',[(xx,y+front+.03,.5),(xx,y+offset,.8),(xx,y+offset,zz-.35),(xx,y+front-.35,zz-.1)],.09 if k else .14,hi)
  # A few large side apertures break a blank return; side face remains quieter than front.
  side=1 if x<0 else -1
  for zz in [h*.36,h*.71]:
   box('side window group',(x+side*(w/2+.025),y+d*.55,zz),(.065,d*.39,.65),recess)
 # combine per-building pieces by material into a compact editable object, curves stay editable separately.
 obs=list(set(C.objects)-first)
 turn=math.radians(rng.choice([-9,-4,7,12]))
 xf=Matrix.Translation((x,y,0))@Matrix.Rotation(turn,4,'Z')@Matrix.Translation((-x,-y,0))
 for ob in obs:
  ob['far_family']=family;ob['far_layer']=layer;ob.matrix_world=xf@ob.matrix_world
 audit.append({'position':[x,y],'dimensions':[w,d,h],'family':family,'layer':layer,'objects':len(obs)})
# Use extant depth bands. Keep first low rubble band intact and begin built forms behind it.
ys=[74,105,138,171,205,241,260]
for layer,y in enumerate(ys):
 spread=[24,30,34,39,46,52,56][layer];count=[8,12,14,16,18,20,20][layer]
 for j in range(count):
  x=-spread+(j+.5)*2*spread/count+rng.uniform(-1.4,1.4)
  if abs(x)<4.8:continue
  w=rng.uniform(1.55,2.8);d=rng.uniform(2.1,3.6);h=rng.uniform(5.8,8.6) if layer==0 else rng.uniform(7.0,14.3)
  building(x,y+rng.uniform(-3.5,3.5),w,d,h,(j+layer*2)%3,layer)
(O/'layout.json').write_text(json.dumps({'buildings':audit,'hide_objects':hidden,'collection':C.name,'notes':'Seven extant depth bands; collapsed rubble preserved; native geometry and normals-based stepped shading; no reflection or lighting changes'},indent=2))
(R/'config/study-far-075.json').write_text(json.dumps({'references':['DP-08','DP-01','HM-01'],'properties':['Large slab/cantilever/service hierarchy','Simple shaded masses with sparse outlined apertures','Restrained detail in dark middle values'],'hypothesis':'Numerous narrow, tall silhouettes retain the user-directed faraway vertical city; approved facade finish binds the nearer layers to the alley while detail diminishes with depth.','fixed':['074 alley geometry/materials','camera','landmark','world and volume'],'changed':['Distant remnant architecture only'],'review_criteria':['Depth and scale','Silhouette family variety','Alley language continuity','No tiny-detail visual noise']},indent=2))
bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
