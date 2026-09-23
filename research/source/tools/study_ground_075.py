import os,bpy,math,random,json,bmesh
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-075';O.mkdir(parents=True,exist_ok=True);rng=random.Random(7501)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-074/scene.blend'));s=bpy.context.scene
for o in s.objects:
 if o.name.startswith(('Small angular street fragment','Side crushed masonry','Flaked road surface')):o.hide_render=True
C=bpy.data.collections.new('075 Soil and mineral scatter');s.collection.children.link(C)
def rgb(h):
 return tuple((v/255)/12.92 if v/255<.04045 else ((v/255+.055)/1.055)**2.4 for v in [int(h[i:i+2],16) for i in (0,2,4)])
def mat(n,h):
 m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*rgb(h),1);e.inputs[1].default_value=1.12;o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
m=mat('075 soil palette','684637');nt=m.node_tree;n=nt.nodes;l=nt.links;em=next(a for a in n if a.type=='EMISSION');coord=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],sep.inputs[0])
def mathn(op,a,b=None):
 q=n.new('ShaderNodeMath');q.operation=op
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):q.inputs[i].default_value=v
  else:l.new(v,q.inputs[i])
 return q.outputs[0]
def noise(scale,detail=2):
 q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;l.new(coord.outputs['Object'],q.inputs['Vector']);return q.outputs['Fac']
# Asymmetric authored meander + multiscale erosion controls transition.
x=sep.outputs['X'];y=sep.outputs['Y'];sine=mathn('SINE',mathn('ADD',mathn('MULTIPLY',y,.34),mathn('MULTIPLY',x,.29)));edge=mathn('ADD',mathn('MULTIPLY',sine,.25),7.45)
edge=mathn('ADD',edge,mathn('MULTIPLY',mathn('SUBTRACT',noise(1.1),.5),.5));edge=mathn('ADD',edge,mathn('MULTIPLY',mathn('SINE',mathn('ADD',mathn('MULTIPLY',y,.71),mathn('MULTIPLY',x,.57))),.22));edge=mathn('ADD',edge,mathn('MULTIPLY',mathn('SUBTRACT',noise(5),.5),.32));dist=mathn('SUBTRACT',mathn('ABSOLUTE',x),edge)
mask=mathn('MULTIPLY_ADD',dist,3.5); # smooth boundary band, clamp through map range
q=n.new('ShaderNodeMapRange');q.clamp=True;q.inputs['From Min'].default_value=-.025;q.inputs['From Max'].default_value=.025;l.new(dist,q.inputs['Value']);mask=q.outputs[0]
# Localized pale deposits around actual support-foot positions, not broad sidewalks.
for fx,fy in [(6.6,7.15),(6.6,11.7),(6.6,12.75),(6.9,20.3),(6.9,21.4)]:
 dx=mathn('DIVIDE',mathn('SUBTRACT',x,fx),.72);dy=mathn('DIVIDE',mathn('SUBTRACT',y,fy),1.05);rr=mathn('ADD',mathn('MULTIPLY',dx,dx),mathn('MULTIPLY',dy,dy));fan=mathn('LESS_THAN',mathn('ADD',rr,mathn('MULTIPLY',noise(5),.4)),1);mask=mathn('MAXIMUM',mask,fan)
macro=noise(2.8);fine=noise(22,2)
def ramp(src,colors,positions):
 q=n.new('ShaderNodeValToRGB');rr=q.color_ramp
 while len(rr.elements)>2:rr.elements.remove(rr.elements[-1])
 for i,(h,pos) in enumerate(zip(colors,positions)):
  e=rr.elements[i] if i<2 else rr.elements.new(pos);e.position=pos;e.color=(*rgb(h),1)
 l.new(src,q.inputs[0]);return q.outputs[0]
lane=ramp(macro,['5c4033','624536','6b4938'],[.2,.52,.82]);dust=ramp(macro,['806a53','94795c','a18564'],[.22,.52,.8]);mix=n.new('ShaderNodeMixRGB');l.new(mask,mix.inputs[0]);l.new(lane,mix.inputs[1]);l.new(dust,mix.inputs[2]);grain=n.new('ShaderNodeMixRGB');grain.blend_type='MULTIPLY';grain.inputs[0].default_value=.30;l.new(mix.outputs[0],grain.inputs[1]);gr=ramp(fine,['534238','c9b39b','fff7df'],[.30,.40,.69]);l.new(gr,grain.inputs[2]);l.new(grain.outputs[0],em.inputs[0])
# Intrinsic soil-tone fractures: warped cellular seams with irregular grit coverage.
warp=n.new('ShaderNodeTexNoise');warp.inputs['Scale'].default_value=2.5;warp.inputs['Detail'].default_value=3;l.new(coord.outputs['Object'],warp.inputs['Vector'])
ws=n.new('ShaderNodeVectorMath');ws.operation='SCALE';ws.inputs['Scale'].default_value=.32;l.new(warp.outputs['Color'],ws.inputs[0]);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(coord.outputs['Object'],add.inputs[0]);l.new(ws.outputs[0],add.inputs[1]);vor=n.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=.36;l.new(add.outputs[0],vor.inputs['Vector'])
seam=mathn('LESS_THAN',vor.outputs['Distance'],.010);coverage=mathn('GREATER_THAN',noise(1.8),.49);seam=mathn('MULTIPLY',seam,coverage)
grit=mathn('MULTIPLY',mathn('LESS_THAN',vor.outputs['Distance'],.043),mathn('GREATER_THAN',noise(24),.58));seam=mathn('MAXIMUM',seam,mathn('MULTIPLY',grit,.7));seam=mathn('MULTIPLY',seam,.42)
cm=n.new('ShaderNodeMixRGB');cm.blend_type='MULTIPLY';l.new(seam,cm.inputs[0]);l.new(grain.outputs[0],cm.inputs[1]);cm.inputs[2].default_value=(.42,.40,.44,1);l.new(cm.outputs[0],em.inputs[0])
bpy.data.objects['Street foundation'].data=bpy.data.objects['Street foundation'].data.copy();bpy.data.objects['Street foundation'].data.materials.clear();bpy.data.objects['Street foundation'].data.materials.append(m)
# Multiple stone families and clustered rather than uniform distribution.
rockm=[mat('075 mineral '+str(i),h) for i,h in enumerate(['68564b','877260','9d856a','56505a','756963'])]
def rock(x,y,size):
 vs=[]
 for j in range(12):
  a=math.tau*j/6+rng.uniform(-.2,.2);z=(-.04 if j<6 else rng.uniform(.12,.42)*size);rr=size*rng.uniform(.45,1);vs.append((x+math.cos(a)*rr,y+math.sin(a)*rr*rng.uniform(.55,1.5),z))
 me=bpy.data.meshes.new('075 irregular embedded mineral');bm=bmesh.new();vv=[bm.verts.new(v) for v in vs];bmesh.ops.convex_hull(bm,input=vv);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(me.name,me);C.objects.link(o)
 for ma in rockm:me.materials.append(ma)
 family=rng.randrange(5)
 for p in me.polygons:p.material_index=family if rng.random()<.75 else max(0,min(4,family+rng.choice([-1,1])))
 if size>.18:
  for k in range(4):
   a=rng.random()*math.tau;rock(x+math.cos(a)*size,y+math.sin(a)*size,rng.uniform(.018,.04))
clusters=[(rng.choice([-1,1])*rng.uniform(7.1,8.0),rng.uniform(-8.5,31)) for _ in range(26)]
for i in range(820):
 if i<690:
  cx,cy=rng.choice(clusters);x=rng.gauss(cx,.38);y=rng.gauss(cy,1.2)
 else:x=rng.uniform(-5.2,5.2);y=rng.uniform(-8.5,32)
 if abs(x)>8.2 or y<-8.7 or y>32:continue
 if abs(x)<.9 and -3<y<1:continue
 sz=rng.uniform(.04,.14) if rng.random()<.78 else rng.uniform(.17,.39)
 rock(x,y,sz*(.55 if abs(x)<5.1 else 1))
# Broken fine ground seams: sparse, variable-width stretches, never a full grid.
crack=mat('075 fine earth seam','342b29')
for j in range(0):
 x=rng.uniform(-5.5,4.8);y=rng.uniform(-8,27);pts=[]
 for k in range(rng.randrange(9,19)):
  pts.append((x,y,-.031));x+=rng.uniform(.1,.34);y+=rng.uniform(-.18,.12)
 cu=bpy.data.curves.new('075 interrupted earth seam','CURVE');cu.dimensions='3D';cu.bevel_depth=rng.uniform(.006,.014);sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(cu.name,cu);C.objects.link(o);cu.materials.append(crack)
# Sparse discontinuous erosion traces, unlike the rejected long black strokes.
for j in range(0):
 x=-5+rng.uniform(-.4,1);y=-7+j*4.6;pts=[]
 for k in range(38):
  x+=rng.uniform(.13,.26);y+=rng.uniform(-.08,.12);pts.append((x,y,-.030))
 for k in range(0,len(pts)-1):
  if rng.random()<.50:continue
  cu=bpy.data.curves.new('075 shallow broken erosion trace','CURVE');cu.dimensions='3D';cu.bevel_depth=.0025;sp=cu.splines.new('POLY');sp.points.add(1)
  for p,v in zip(sp.points,[pts[k],pts[k+1]]):p.co=(*v,1)
  o=bpy.data.objects.new(cu.name,cu);C.objects.link(o);cu.materials.append(crack)
  if rng.random()<.4:rock(pts[k][0],pts[k][1]+.02,rng.uniform(.015,.04))
for ma in [m]+rockm:
 nt=ma.node_tree;ns=nt.nodes;lk=nt.links;e=next(n for n in ns if n.type=='EMISSION');base=e.inputs[0].links[0].from_socket if e.inputs[0].is_linked else None
 if base is None:
  q=ns.new('ShaderNodeRGB');q.outputs[0].default_value=e.inputs[0].default_value;base=q.outputs[0]
 d=ns.new('ShaderNodeBsdfDiffuse');d.inputs[0].default_value=(1,1,1,1);lr=ns.new('ShaderNodeShaderToRGB');lk.new(d.outputs[0],lr.inputs[0]);bw=ns.new('ShaderNodeRGBToBW');lk.new(lr.outputs[0],bw.inputs[0]);r=ns.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(.50,.49,.52,1);r.color_ramp.elements[1].position=.75;r.color_ramp.elements[1].color=(1,1,1,1);lk.new(bw.outputs[0],r.inputs[0]);mixer=ns.new('ShaderNodeMixRGB');mixer.blend_type='MULTIPLY';mixer.inputs[0].default_value=1;lk.new(base,mixer.inputs[1]);lk.new(r.outputs[0],mixer.inputs[2]);ao=ns.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.7;ao.samples=16;ar=ns.new('ShaderNodeValToRGB');ar.color_ramp.elements[0].position=.25;ar.color_ramp.elements[0].color=(.38,.36,.39,1);ar.color_ramp.elements[1].position=.9;ar.color_ramp.elements[1].color=(1,1,1,1);lk.new(ao.outputs['AO'],ar.inputs[0]);am=ns.new('ShaderNodeMixRGB');am.blend_type='MULTIPLY';am.inputs[0].default_value=1;lk.new(mixer.outputs[0],am.inputs[1]);lk.new(ar.outputs[0],am.inputs[2]);lk.new(am.outputs[0],e.inputs[0])
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if not os.environ.get('GROUND_BUILD_ONLY'):bpy.ops.render.render(write_still=True)
(O/'integration.json').write_text(json.dumps({'collection':C.name,'ground_material':m.name,'hide_prefixes':['Small angular street fragment','Side crushed masonry','Flaked road surface'],'seed':7501},indent=2))
