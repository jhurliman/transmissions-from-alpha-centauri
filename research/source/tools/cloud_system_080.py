"""Native cloud silhouette meshes with independent smooth inset contours."""
import bpy,math,random,json,bmesh,os,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/cloud-080'
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def apply(scene,config=None):
 cfg=json.loads((R/'config/cloud-system-080.json').read_text()) if config is None else dict(config)
 ratio=cfg['inset_frequency_ratio'];assert 0<ratio<1,'Inset contour frequency must remain lower than outer.'
 if bpy.data.collections.get('080 Native cloud banks'):return bpy.data.collections['080 Native cloud banks']
 scene.world=scene.world.copy();nt=scene.world.node_tree;cloud=next(q for q in nt.nodes if q.label=='075 Cloud oxide red')
 for link in list(cloud.inputs[0].links):nt.links.remove(link)
 cloud.inputs[0].default_value=0
 C=bpy.data.collections.new('080 Native cloud banks');scene.collection.children.link(C)
 def material(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;em=n.new('ShaderNodeEmission');em.inputs[0].default_value=rgb(color);em.inputs[1].default_value=.9;tr=n.new('ShaderNodeBsdfTransparent');lp=n.new('ShaderNodeLightPath');mix=n.new('ShaderNodeMixShader');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);return m
 outer=material('080 Cloud | sunlit oxide',cfg['outer_color']);inside=material('080 Cloud | smooth dark interior',cfg['inner_color']);rare=material('080 Cloud | rare warm small body','#cf5b42')
 def mesh(name,verts,mat):
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);C.objects.link(o);return o
 def contours(seed,count,ratio):
  rng=random.Random(seed);N=220;H=100;xs=np.linspace(-.35,1.35,N);ys=np.linspace(-1.3,1.3,H);X,Y=np.meshgrid(xs,ys);base=np.zeros_like(X)
  n=cfg.get('macro_body_count',4);mass=[]
  for j in range(n):
   x=.08+.84*j/max(1,n-1)+rng.uniform(-.04,.04);y=rng.uniform(-.32,.32);wx=rng.uniform(.115,.255);wy=rng.uniform(.19,.53);mass.append((x,y,wx,wy));base+=np.exp(-(((X-x)/wx)**2+((Y-y)/wy)**2)*1.6)
  # Thin atmospheric neck joins asymmetric larger bodies without making uniform tubes.
  base+=.25*np.exp(-((Y+.04)/.13)**2)*np.exp(-((X-.5)/.5)**6)
  bx=rng.uniform(.3,.7);by=rng.choice([-1,1])*rng.uniform(.28,.45);base+=.52*np.exp(-(((X-bx)/.14)**2+((Y-by)/.22)**2)*1.5)
  field=base.copy()
  for j in range(count):
   x=(j+rng.uniform(.05,.95))/count;ix=int(np.argmin(abs(xs-x)));rows=np.flatnonzero(base[:,ix]>.43);y=(ys[rows[-1]] if rng.random()>.38 else ys[rows[0]])+rng.uniform(-.035,.025) if len(rows) else 0;wx=rng.uniform(.65,1.05)/count;wy=rng.uniform(.19,.30)*math.sqrt(10/count);field+=.85*np.exp(-(((X-x)/wx)**2+((Y-y)/wy)**2)*1.5)
  def trace(F,level):
   segments=[]
   for iy in range(H-1):
    for ix in range(N-1):
     pts=[(xs[ix],ys[iy]),(xs[ix+1],ys[iy]),(xs[ix+1],ys[iy+1]),(xs[ix],ys[iy+1])];vs=[F[iy,ix],F[iy,ix+1],F[iy+1,ix+1],F[iy+1,ix]];hits=[]
     for e in range(4):
      k=(e+1)%4
      if (vs[e]>level)!=(vs[k]>level):
       t=(level-vs[e])/(vs[k]-vs[e]);hits.append(tuple(round(pts[e][c]+t*(pts[k][c]-pts[e][c]),7) for c in range(2)))
     if len(hits)==2:segments.append(hits)
     elif len(hits)==4:segments.extend([hits[:2],hits[2:]])
   graph={}
   for a,b in segments:graph.setdefault(a,[]).append(b);graph.setdefault(b,[]).append(a)
   paths=[]
   while graph:
    first=next(iter(graph));path=[first];prev=None;cur=first
    for _ in range(len(segments)+1):
     adj=graph.get(cur,[]);nxt=next((q for q in adj if q!=prev),None)
     if nxt is None:break
     graph.pop(cur,None);prev,cur=cur,nxt
     if cur==first:break
     path.append(cur)
    if len(path)>3:paths.append(path)
   return sorted(paths,key=len,reverse=True)
  area=lambda p:abs(sum(p[j][0]*p[(j+1)%len(p)][1]-p[(j+1)%len(p)][0]*p[j][1] for j in range(len(p)))/2)
  outerpaths=[p for p in trace(field,.43) if area(p)>.025];innerpaths=[p for p in trace(base-np.clip(.19*Y,-.12,.16),.60) if area(p)>.025]
  for path,isinner in [(p,False) for p in outerpaths]+[(p,True) for p in innerpaths]:
   old=list(path);lengths=[0.]
   for k in range(1,len(path)):lengths.append(lengths[-1]+math.hypot((old[k][0]-old[k-1][0])*5,old[k][1]-old[k-1][1]))
   total=lengths[-1]+math.hypot((old[-1][0]-old[0][0])*5,old[-1][1]-old[0][1])
   for k,(x,y) in enumerate(old):
    a=old[k-1];b=old[(k+1)%len(old)];dx=(b[0]-a[0])*5;dy=b[1]-a[1];norm=max(1e-9,math.hypot(dx,dy));phase=lengths[k]/total*math.tau;freq=count*ratio if isinner else count*2;d=(0 if total<3 else min(1,total/3))*(.009*math.sin(phase*freq) if isinner else (.014*math.sin(phase*freq)+.006*math.sin(phase*count*3+1.2)));path[k]=(x-d*dy/norm/5,y+d*dx/norm)
  return outerpaths,innerpaths
 # Angular bank layout expressed as real world geometry at distant y planes.
 banks=[(-.0376776,.3377706,.208,.0455),(.15,.205,.32,.049),(-.12,.155,.30,.052),(-.24,.255,.16,.04),(.32,.29,.22,.047),(.035,.39,.30,.055),(-.02,.245,.13,.026),(.24,.12,.12,.026),(-.33,.13,.15,.022),(.05,.105,.10,.022),(.20,.36,.10,.018),(-.32,.40,.18,.033),(-.27,.30,.24,.048),(.29,.285,.23,.062),(-.1520194,.2699562,.075,.018),(.1716181,.2424995,.075,.016)]
 records=[]
 for i,(cx,cz,width,height) in enumerate(banks):
  height*=cfg.get('vertical_scale',1.0)
  rng=random.Random(cfg['seed']+i*231);distance=800.0;count=max(3,round(cfg['contour_frequency']*rng.uniform(1-cfg['per_cloud_frequency_jitter'],1+cfg['per_cloud_frequency_jitter'])));paths,innerpaths=contours(cfg['seed']+i*431,count,ratio)
  def point(t,v,dep=0):return ((cx+(t-.5)*width)*distance,distance+dep,(cz+v*height)*distance)
  use_rare=height/cfg.get('vertical_scale',1.0)<cfg['large_cloud_inset_threshold'] and rng.random()<cfg['rare_color_chance']
  for k,path in enumerate(paths):
   ob=mesh('080 Cloud bank %02d.%02d'%(i,k),[point(t,v) for t,v in path],rare if use_rare else outer);ob['contour_frequency']=count;ob['seed']=cfg['seed']+i*431;ob['angular_width']=width;ob['angular_height']=height
  inset_count=max(2,round(count*ratio));inset_count=min(inset_count,count-1)
  if height/cfg.get('vertical_scale',1.0)>=cfg['large_cloud_inset_threshold']:
   for k,path in enumerate(innerpaths):
    ins=mesh('080 Smooth inset %02d.%02d'%(i,k),[point(t,v,-5.0) for t,v in path],inside);ins['contour_frequency']=inset_count;ins['outer_frequency']=count
  records.append({'cloud':i,'outer_frequency':count,'inset_frequency':inset_count if height/cfg.get('vertical_scale',1.0)>=cfg['large_cloud_inset_threshold'] else None,'rare_palette':use_rare})
 for key in ['seed','contour_frequency','per_cloud_frequency_jitter','inset_frequency_ratio','large_cloud_inset_threshold','rare_color_chance','macro_body_count']:C[key]=cfg[key]
 C['audit']=json.dumps(records)
 # Exclude cloud polygons from architectural ink without altering existing line settings.
 for o in C.objects:o.visible_shadow=False
 for ls in scene.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return C
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-079/scene.blend'));s=bpy.context.scene;cfg=json.loads((R/'config/cloud-system-080.json').read_text());
 if os.getenv('CLOUD_FREQUENCY'):cfg['contour_frequency']=float(os.environ['CLOUD_FREQUENCY'])
 if os.getenv('CLOUD_VARIANT'):
  O=O/os.environ['CLOUD_VARIANT'];O.mkdir(parents=True,exist_ok=True)
 C=apply(s,cfg);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));
 if not os.getenv('CLOUD_PROOF_ONLY'):bpy.ops.render.render(write_still=True)
 # Dedicated field proof uses only native cloud geometry and identical camera-visible world.
 proof=bpy.data.scenes.new('080 Cloud field proof');proof.render.engine='BLENDER_EEVEE';proof.world=s.world.copy();proof.collection.children.link(C);cam=bpy.data.objects.new('080 Cloud proof camera',bpy.data.cameras.new('080 Cloud proof camera'));proof.collection.objects.link(cam);cam.location=(0,0,-20);cam.rotation_euler=(Vector((0,800,180))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=35;cam.data.clip_end=3000;proof.camera=cam;proof.render.resolution_x=1440;proof.render.resolution_y=640;proof.render.resolution_percentage=100;proof.render.threads_mode='FIXED';proof.render.threads=4;proof.view_settings.view_transform=s.view_settings.view_transform;proof.view_settings.look=s.view_settings.look;proof.view_settings.exposure=s.view_settings.exposure;proof.view_settings.gamma=s.view_settings.gamma;bpy.context.window.scene=proof;proof.render.filepath=str(O/'detail.png');bpy.ops.render.render(write_still=True)
 for o in C.objects:
  if o.name.startswith('080 Smooth'):o.hide_render=True
  else:
   m=bpy.data.materials.new('080 Mask black');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);o.data.materials.clear();o.data.materials.append(m)
 proof.world=bpy.data.worlds.new('080 Mask white');proof.world.use_nodes=True;proof.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);proof.render.filepath=str(O/'mask.png');bpy.ops.render.render(write_still=True)
