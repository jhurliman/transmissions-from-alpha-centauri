"""101: native reconstruction of visible original city masses; inferred depth."""
import bpy,sys,json,math,random,ast,os
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));V=os.environ.get('CITY_VARIANT','A');ROOT=R/'art/studies/city-101';O=ROOT/V;O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-100/scene.blend'));s=bpy.context.scene;rng=random.Random(101041)
for o in s.objects:
 if o.name.startswith(('FAR075 ','CITY099 ')):o.hide_render=True
# Preserve approved nearby ink; discard old distant-city strokes for replacement.
for name in ['096 contacts ink','096 damage ink']:
 ob=s.objects.get(name)
 if not ob:continue
 for layer in ob.data.layers:
  for f in layer.frames:
   dr=f.drawing;ids=[i for i,st in enumerate(dr.strokes) if any(p.position.y>42 for p in st.points)]
   if ids:dr.remove_strokes(indices=ids)
C=bpy.data.collections.new('101 Original city layout study');s.collection.children.link(C)
# Reuse native clean-kit geometry constructors, with new measured palette families.
module=ast.parse((R/'tools/study_far_075.py').read_text());defs=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['mesh','box','prism','pipe','building']]
for definition in defs:
 for node in ast.walk(definition):
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='turn' for t in node.targets):node.value=ast.Constant(0)
exec(compile(ast.fix_missing_locations(ast.Module(body=defs,type_ignores=[])),'far_kit_functions','exec'),globals())
def linear(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def color(h,factor=1):
 h=h.lstrip('#');return tuple(linear(min(1,int(h[i:i+2],16)/255*factor)) for i in [0,2,4])+(1,)
def mat(name,h,factor=1):
 m=bpy.data.materials.new('CITY101 '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();n=nt.nodes;l=nt.links
 out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');l.new(em.outputs[0],out.inputs[0]);g=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.38,-.67,.64);l.new(g.outputs['Normal'],dot.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT';r.color_ramp.elements[0].position=0;r.color_ramp.elements[0].color=color(h,factor*.81);r.color_ramp.elements[1].position=.5;r.color_ramp.elements[1].color=color(h,factor);l.new(dot.outputs['Value'],r.inputs[0]);l.new(r.outputs[0],em.inputs[0]);return m
frame=s.camera.data.view_frame(scene=s);cam=s.camera.matrix_world.translation;basis=s.camera.matrix_world.to_3x3()
def ray(px,py):
 nx=px/s.render.resolution_x;ny=1-py/s.render.resolution_y
 return (basis@Vector((min(v.x for v in frame)+(max(v.x for v in frame)-min(v.x for v in frame))*nx,min(v.y for v in frame)+(max(v.y for v in frame)-min(v.y for v in frame))*ny,frame[0].z))).normalized()
def project(v):
 q=world_to_camera_view(s,s.camera,Vector(v));return Vector((q.x*s.render.resolution_x,(1-q.y)*s.render.resolution_y))
def height_at(x,y,py):
 low=.2;high=120
 for _ in range(30):
  mid=(low+high)*.5
  if project((x,y,mid)).y>py:low=mid
  else:high=mid
 return (low+high)*.5
# Reference x415.5 is midpoint of omitted four-building cluster, aligned with route.
SX=372/(720 if V=='A' else 626)
def mapped(x,y):return (564+(x-(26 if V=='A' else 24))*SX,(460+(y-330)*.60) if V=='A' else (467+(y-260)*.62))
inventory=json.loads((ROOT/('reference-inventory.json' if V=='A' else 'reference-inventory-B.json')).read_text());audit=[];results=[]
# Schema normalized by integration step before execution.
for r in inventory['buildings']:
 if r.get('omit'):continue
 x0,y0,x1,y1=r['bbox'];px,py=mapped((x0+x1)/2,y1);roof=mapped(0,y0)[1];v=ray(px,py)
 pos=cam+v*(-cam.z/v.z);x,y=pos.x,pos.y
 if y<48:y=48;x=cam.x+v.x*((y-cam.y)/v.y)
 span=abs(project((x+1,y,0)).x-project((x,y,0)).x);w=(x1-x0)*SX/span
 # Observed baselines infer depth; the newer user direction permits a winding route.
 # Place facade plane on measured pixel footprint; body extends away from viewer.
 h=height_at(x,y,roof);depth=max(.8,min(w*.60,5.2));hexcol=r['color_hex'];m=mat(r['id']+' body',hexcol);rec=mat(r['id']+' recess',hexcol,.65);seam=mat(r['id']+' service',hexcol,.88);hi=mat(r['id']+' highlight',hexcol,1.21)
 materials=[[m,m,m,rec,seam,hi] for _ in range(4)];before=set(C.objects)
 if r.get('low') or h<4.1:
  box('low single-story block',(x,y+depth/2,h/2),(w,depth,h),m)
  box('low roof rim',(x,y+depth/2,h),(w+.10,depth+.1,.13),hi)
  for k in range(max(1,int(w/1.8))):
   xx=x-w*.4+(k+.5)*w*.8/max(1,int(w/1.8));box('low opening',(xx,y-.03,h*.52),(min(.8,w*.2),.06,min(.7,h*.35)),rec)
 else:
  family=1 if 'step' in r.get('profile','').lower() else (2 if w/h>.42 else 0)
  # Match visible facade detail frequency as well as overall mass dimensions.
  th=max(6.4,(y1-y0)*(.60 if V=='A' else .62)/8*3.2)
  tw=max(2.7,(x1-x0)*SX/9*2.6)
  td=max(2.0,tw*.6)
  building(0,0,tw,td,th,family,2)
  xf=Matrix.Translation((x,y,0))@Matrix.Diagonal((w/tw,depth/td,h/th,1))
  for ob in set(C.objects)-before:ob.matrix_world=xf@ob.matrix_world
 # Reconstruct measured coarse crown contour as actual extruded geometry.
 if not (r.get('low') or h<4.1):
  roofpts=[]
  for rx,ry in r.get('profile_px',[]):
   xx=x+(rx-(x0+x1)/2)/(x1-x0)*w
   zz=height_at(xx,y,mapped(rx,ry)[1]);roofpts.append((xx,zz))
  if len(roofpts)>=2:
   roofpts.sort();roofpts=[(x-w/2,roofpts[0][1])]+roofpts+[(x+w/2,roofpts[-1][1])]
   def roofheight(xx):
    for (ax,az),(bx,bz) in zip(roofpts,roofpts[1:]):
     if ax<=xx<=bx and bx>ax:return az+(bz-az)*(xx-ax)/(bx-ax)
    return h
   for ob in list(set(C.objects)-before):
    pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];cx=sum(v.x for v in pts)/len(pts)
    remove=any(t in ob.name for t in ['raked slab','gallery slab','chamfered service tower','offset crown','roof receiver'])
    if remove or max(v.z for v in pts)>roofheight(cx)+.035:bpy.data.objects.remove(ob,do_unlink=True)
   profile=[(x-w/2,0),(x+w/2,0)]+list(reversed(roofpts));N=len(profile)
   front=(.8 if family==0 else (-.6 if family==2 else 0))*depth/td
   verts=[(xx,y+dep,zz) for dep in [front,depth] for xx,zz in profile]
   faces=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
   mesh('measured crown mass',verts,faces,m)
 for ob in set(C.objects)-before:
  ob.name='CITY101 '+r['id']+' '+ob.name;ob['reference_mass']=r['id'];ob['reference_bbox']=json.dumps(r['bbox'])
 results.append({'id':r['id'],'target_bbox':r['bbox'],'color_hex':hexcol,'position':[x,y],'dimensions':[w,depth,h],'low':r.get('low',False),'projected_foot':list(project((x,y,0))),'projected_roof':list(project((x,y,h)))})
(O/'reconstruction.json').write_text(json.dumps({'reference_mapping':{'visible_aperture_x':[564,936],'horizontal_scale':SX,'vertical_scale':.60 if V=='A' else .62},'masses':results,'hidden_depth':'inferred from visible ground baselines; winding street permitted','omitted':[r['id'] for r in inventory['buildings'] if r.get('omit')]},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'placement.blend'));s.render.use_freestyle=False;s.render.resolution_percentage=75;s.render.filepath=str(O/'preview.png');bpy.ops.render.render(write_still=True)
