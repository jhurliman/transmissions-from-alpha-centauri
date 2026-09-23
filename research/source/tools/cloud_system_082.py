"""Native cloud silhouette meshes with independent smooth inset contours."""
import bpy,math,random,json,bmesh,os,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/cloud-082'
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def apply(scene,config=None):
 cfg=json.loads((R/'config/cloud-system-082.json').read_text()) if config is None else dict(config)
 ratio=cfg['inset_frequency_ratio'];assert 0<ratio<1,'Inset contour frequency must remain lower than outer.'
 if bpy.data.collections.get('082 Native cloud banks'):return bpy.data.collections['082 Native cloud banks']
 scene.world=scene.world.copy();nt=scene.world.node_tree;cloud=next(q for q in nt.nodes if q.label=='075 Cloud oxide red')
 for link in list(cloud.inputs[0].links):nt.links.remove(link)
 cloud.inputs[0].default_value=0
 C=bpy.data.collections.new('082 Native cloud banks');scene.collection.children.link(C)
 def material(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links;em=n.new('ShaderNodeEmission');em.inputs[0].default_value=rgb(color);em.inputs[1].default_value=.9;tr=n.new('ShaderNodeBsdfTransparent');lp=n.new('ShaderNodeLightPath');mix=n.new('ShaderNodeMixShader');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs[0]);return m
 outer=material('082 Cloud | sunlit oxide',cfg['outer_color']);inside=material('082 Cloud | smooth dark interior',cfg['inner_color']);rare=material('082 Cloud | rare warm small body','#cf5b42')
 def volume_material():
  m=material('082 Native normal-lit cloud',cfg['outer_color']);nt=m.node_tree;n=nt.nodes;l=nt.links;em=next(q for q in n if q.type=='EMISSION');geo=n.new('ShaderNodeAttribute');geo.attribute_name='cloud_macro_normal';dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.35,-.70,.62);l.new(geo.outputs['Vector'],dot.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT';r.color_ramp.elements[0].position=.0;r.color_ramp.elements[0].color=rgb('#bd4b37');r.color_ramp.elements[1].position=.25;r.color_ramp.elements[1].color=rgb('#ce5940');r.color_ramp.elements.new(.86).color=rgb('#d15c41');l.new(dot.outputs['Value'],r.inputs[0]);l.new(r.outputs[0],em.inputs[0]);return m
 volmat=volume_material()
 def sphere(location,segments=64,rings=32):
  me=bpy.data.meshes.new('082 Ellipsoid');bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=segments,v_segments=rings,radius=1);bm.to_mesh(me);bm.free();o=bpy.data.objects.new('082 Ellipsoid',me);C.objects.link(o);o.location=location;return o
 def mesh(name,verts,mat):
  me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[tuple(range(len(verts)))]);me.materials.append(mat);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);C.objects.link(o);return o
 def contours(seed,count,ratio,kind):
  rng=random.Random(seed);N=220;H=100;xs=np.linspace(-.35,1.35,N);ys=np.linspace(-1.3,1.3,H);X,Y=np.meshgrid(xs,ys);base=np.zeros_like(X)
  # Authored mass grammars: compact billows, broad shoulder banks, and tapering wisps.
  forms={
   'billow':[(.18,-.17,.22,.14),(.36,.0,.20,.34),(.54,.20,.23,.60),(.76,.02,.18,.38),(.9,-.17,.20,.13)],
   'shoulder':[(.1,-.17,.20,.10),(.3,-.06,.20,.26),(.46,.12,.24,.48),(.68,-.03,.25,.29),(.89,-.16,.18,.12)],
   'wisp':[(.12,-.12,.20,.075),(.38,-.04,.26,.16),(.61,.04,.22,.24),(.85,-.03,.26,.11)]}
  mass=[]
  for x,y,wx,wy in forms[kind]:
   x+=rng.uniform(-.035,.035);y+=rng.uniform(-.035,.035);wx*=rng.uniform(.9,1.12);wy*=rng.uniform(.9,1.12);mass.append((x,y,wx,wy));base+=np.exp(-(((X-x)/wx)**2+((Y-y)/wy)**2)*1.6)
  shadow=np.zeros_like(X)
  for j,(x,y,wx,wy) in enumerate(mass):
   if wy<.20:continue
   # Under-folds sit low and a little to the right of each billowing shoulder.
   shadow+=np.exp(-(((X-x-.025)/(wx*.78))**2+((Y-y+wy*.32)/(wy*.34))**2)*1.5)
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
  outerpaths=[p for p in trace(field,.43) if area(p)>.025];innerpaths=[p for p in trace(np.minimum(shadow,base/.72),.58) if area(p)>.008]
  for path,isinner in [(p,False) for p in outerpaths]+[(p,True) for p in innerpaths]:
   old=list(path);lengths=[0.]
   for k in range(1,len(path)):lengths.append(lengths[-1]+math.hypot((old[k][0]-old[k-1][0])*5,old[k][1]-old[k-1][1]))
   total=lengths[-1]+math.hypot((old[-1][0]-old[0][0])*5,old[-1][1]-old[0][1])
   for k,(x,y) in enumerate(old):
    a=old[k-1];b=old[(k+1)%len(old)];dx=(b[0]-a[0])*5;dy=b[1]-a[1];norm=max(1e-9,math.hypot(dx,dy));phase=lengths[k]/total*math.tau;freq=count*ratio if isinner else count*2;d=(0 if total<3 else min(1,total/3))*(.009*math.sin(phase*freq) if isinner else (.014*math.sin(phase*freq)+.006*math.sin(phase*count*3+1.2)));path[k]=(x-d*dy/norm/5,y+d*dx/norm)
  return outerpaths,innerpaths,(xs,ys,field,base)
 # Angular bank layout expressed as real world geometry at distant y planes.
 banks=[
  (-.15,.37,.27,.072,'billow'),(.10,.395,.30,.065,'shoulder'),
  (-.16,.285,.20,.032,'wisp'),(.245,.29,.28,.065,'billow'),
  (.11,.23,.20,.025,'wisp'),(-.035,.32,.19,.033,'shoulder'),
  (-.25,.235,.13,.025,'wisp'),(.30,.36,.16,.027,'wisp')]
 if cfg.get('hero_only',False):banks=[(0,.25,.50,.15,cfg.get('shape_family','billow'))]
 records=[]
 for i,(cx,cz,width,height,kind) in enumerate(banks):
  height*=cfg.get('vertical_scale',1.0)
  rng=random.Random(cfg['seed']+i*231);distance=800.0;count=max(3,round(cfg['contour_frequency']*rng.uniform(1-cfg['per_cloud_frequency_jitter'],1+cfg['per_cloud_frequency_jitter'])));paths,innerpaths,volume=contours(cfg['seed']+i*431,count,ratio,kind)
  def point(t,v,dep=0):return ((cx+(t-.5)*width)*distance,distance+dep,(cz+v*height)*distance)
  use_rare=height/cfg.get('vertical_scale',1.0)<cfg['large_cloud_inset_threshold'] and rng.random()<cfg['rare_color_chance']
  if cfg.get('ellipsoid_union',False):
   prior=set(C.objects)
   rng=random.Random(cfg['seed']+i*431)
   forms=[(.24,.10,.18,.16),(.39,-.035,.10,.105),(.35,.31,.10,.19),(.51,.30,.12,.043),(.65,.14,.105,.185),(.8,.04,.12,.09),(.94,.10,.10,.055),(1.06,.14,.08,.025),(.78,-.06,.08,.035),(.88,-.095,.07,.023),(.97,-.065,.055,.015),(.92,-.23,.055,.011),(.98,-.215,.035,.006),(1.07,.27,.045,.008),(1.12,.28,.025,.005)] if kind!='wisp' else [(.15,-.10,.24,.07),(.4,-.04,.26,.10),(.61,.02,.22,.16),(.84,-.02,.22,.075)]
   if kind=='shoulder':forms=[(.24,.04,.17,.20),(.43,.22,.13,.22),(.62,.00,.14,.18),(.71,.29,.10,.15),(.06,-.02,.15,.045),(-.12,.01,.10,.021),(.79,-.10,.13,.035),(.97,-.14,.10,.015)]
   elif kind=='wisp':forms=[(.02,.02,.17,.04),(.20,.04,.15,.055),(.36,.00,.12,.12),(.55,.07,.10,.045),(.70,.12,.105,.026),(.87,.20,.12,.018),(.57,-.09,.12,.025),(.75,-.14,.09,.01)]
   for j,(x,z,rx,rz) in enumerate(forms):
    depth=-rng.uniform(0,12)-rz*height*distance*.4-(25 if j==1 else 0)
    if rz<.12:depth=-16
    o=sphere(point(x,z,depth));o.name='082 Billow %02d.%02d'%(i,j)
    for col in list(o.users_collection):col.objects.unlink(o)
    C.objects.link(o);o.scale=(rx*width*distance,height*distance*rz*.75,rz*height*distance);o.data.materials.append(volmat)
    for p in o.data.polygons:p.use_smooth=True
    if rz>.14:
     for k in range(10 if j in (0,4) else 8):
      a=(.22,.72,1.23,1.83,2.40,2.94,3.55,4.28,4.83,5.65)[k]+rng.uniform(-.13,.13);rr=rz*rng.uniform(.12,.29);xx=x+math.cos(a)*rx*1.0;zz=z+math.sin(a)*rz*1.0
      q=sphere(point(xx,zz,depth+rng.uniform(-3,3)),48,24);q.name='082 Shoulder %02d.%02d.%02d'%(i,j,k)
      for col in list(q.users_collection):col.objects.unlink(q)
      C.objects.link(q);q.scale=(rr*height*distance*1.4,rr*height*distance,rr*height*distance);q.data.materials.append(volmat)
      for p in q.data.polygons:p.use_smooth=True
      if k%2==0:
       for da in [-.18,.18]:
        tiny=rz*rng.uniform(.08,.14);tx=x+math.cos(a+da)*rx*.97;tz=z+math.sin(a+da)*rz*.96;r=sphere(point(tx,tz,depth),32,16);r.name='082 Fine shoulder';r.scale=(tiny*height*distance*1.5,tiny*height*distance,tiny*height*distance);r.data.materials.append(volmat)
        for p in r.data.polygons:p.use_smooth=True
   pieces=[o for o in C.objects if o not in prior];bpy.ops.object.select_all(action='DESELECT')
   for o in pieces:o.select_set(True)
   bpy.context.view_layer.objects.active=pieces[0];bpy.ops.object.join();bank=bpy.context.object;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rem=bank.modifiers.new('Union cloud volumes','REMESH');rem.mode='VOXEL';rem.voxel_size=.7;bpy.ops.object.modifier_apply(modifier=rem.name);sm=bank.modifiers.new('Soften volume joins','SMOOTH');sm.factor=.7;sm.iterations=4;bpy.ops.object.modifier_apply(modifier=sm.name)
   bank.data.update();attr=bank.data.attributes.new('cloud_macro_normal','FLOAT_VECTOR','POINT')
   normals=np.array([tuple(v.normal) for v in bank.data.vertices],dtype=np.float32);attr.data.foreach_set('vector',normals.ravel())
   tex=bpy.data.textures.new('082 Volume boundary octave',type='CLOUDS');tex.noise_scale=width*distance/count;tex.noise_depth=1;dis=bank.modifiers.new('Shallow billow irregularity','DISPLACE');dis.texture=tex;dis.texture_coords='GLOBAL';dis.strength=height*distance*.12;dis.mid_level=.5;bpy.ops.object.modifier_apply(modifier=dis.name)
   for p in bank.data.polygons:p.use_smooth=True
  elif cfg.get('native_volume',False):
   xs,ys,F,base=volume;verts=[];faces=[]
   for iy in range(len(ys)-1):
    for ix in range(len(xs)-1):
     q=[(xs[ix],ys[iy],F[iy,ix],base[iy,ix]),(xs[ix+1],ys[iy],F[iy,ix+1],base[iy,ix+1]),(xs[ix+1],ys[iy+1],F[iy+1,ix+1],base[iy+1,ix+1]),(xs[ix],ys[iy+1],F[iy+1,ix],base[iy+1,ix])];poly=[]
     for j,a in enumerate(q):
      b=q[(j+1)%4]
      if a[2]>.43:poly.append(a)
      if (a[2]>.43)!=(b[2]>.43):
       t=(.43-a[2])/(b[2]-a[2]);poly.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1]),.43,a[3]+t*(b[3]-a[3])))
     if len(poly)>=3:
      start=len(verts);verts.extend(point(x,z,-height*distance*.55*math.sqrt(max(0,macro-.15))) for x,z,val,macro in poly);faces.append(tuple(range(start,start+len(poly))))
   me=bpy.data.meshes.new('082 Cloud volume');me.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.materials.append(volmat);ob=bpy.data.objects.new('082 Volume bank %02d'%i,me);C.objects.link(ob)
   for p in me.polygons:p.use_smooth=True
   ob['contour_frequency']=count;ob['seed']=cfg['seed']+i*431
  else:
   for k,path in enumerate(paths):
    ob=mesh('082 Cloud bank %02d.%02d'%(i,k),[point(t,v) for t,v in path],rare if use_rare else outer);ob['contour_frequency']=count;ob['seed']=cfg['seed']+i*431;ob['angular_width']=width;ob['angular_height']=height
  inset_count=max(2,round(count*ratio));inset_count=min(inset_count,count-1)
  if not cfg.get('native_volume',False) and height/cfg.get('vertical_scale',1.0)>=cfg['large_cloud_inset_threshold']:
   for k,path in enumerate(innerpaths):
    ins=mesh('082 Smooth inset %02d.%02d'%(i,k),[point(t,v,-5.0) for t,v in path],inside);ins['contour_frequency']=inset_count;ins['outer_frequency']=count
  records.append({'cloud':i,'outer_frequency':count,'inset_frequency':inset_count if height/cfg.get('vertical_scale',1.0)>=cfg['large_cloud_inset_threshold'] else None,'rare_palette':use_rare})
 for key in ['seed','contour_frequency','per_cloud_frequency_jitter','inset_frequency_ratio','large_cloud_inset_threshold','rare_color_chance','macro_body_count']:C[key]=cfg[key]
 C['audit']=json.dumps(records)
 # Exclude cloud polygons from architectural ink without altering existing line settings.
 for o in C.objects:o.visible_shadow=False
 for ls in scene.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return C
def apply_flat(s):
 for c in list(bpy.data.collections):
  if c.name.startswith(('080 Cloud','082 Native cloud','082 Derived')):
   for o in c.all_objects:o.hide_render=True
 s.world=s.world.copy()
 for n in s.world.node_tree.nodes:
  if n.label=='075 Cloud oxide red':
   for l in list(n.inputs[0].links):s.world.node_tree.links.remove(l)
   n.inputs[0].default_value=0
 C=bpy.data.collections.new('082 Derived flat clouds');s.collection.children.link(C)
 cam=s.camera;frame=cam.data.view_frame(scene=s);xmin=min(v.x/-v.z for v in frame);xmax=max(v.x/-v.z for v in frame);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame)
 placements=[('arch',615,57,390,850),('shoulder',967,8,390,880),('wisp2',565,132,165,830),('wisp',908,153,145,840)]
 for i,(family,px,py,pw,d) in enumerate(placements):
  img=bpy.data.images.load(str(O/'assets'/f'{family}-pigment.png'),check_existing=True);img.pack();asp=img.size[1]/img.size[0];ph=pw*asp
  coords=[]
  for u,v in [(px-pw/2,py+ph/2),(px+pw/2,py+ph/2),(px+pw/2,py-ph/2),(px-pw/2,py-ph/2)]:
   p=Vector(((xmin+(xmax-xmin)*u/1440)*d,(ymax-(ymax-ymin)*v/1082)*d,-d));coords.append(cam.matrix_world@p)
  me=bpy.data.meshes.new('082 Native-derived cloud plate');me.from_pydata(coords,[],[(0,1,2,3)]);uv=me.uv_layers.new()
  for k,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[k].uv=p
  ob=bpy.data.objects.new(f'082 {family} authored bank {i}',me);C.objects.link(ob);ob.visible_shadow=False
  m=bpy.data.materials.new(f'082 {family} native-derived pigment');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Linear';em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tex.outputs['Color'],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');ray=nt.nodes.new('ShaderNodeLightPath');mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(tex.outputs['Alpha'],mul.inputs[0]);nt.links.new(ray.outputs['Is Camera Ray'],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);me.materials.append(m)
 for ls in s.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return C

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-079/scene.blend'));s=bpy.context.scene;cfg=json.loads((R/'config/cloud-system-082.json').read_text());
 if os.getenv('CLOUD_FAMILY'):cfg['shape_family']=os.environ['CLOUD_FAMILY']
 if os.getenv('CLOUD_FREQUENCY'):cfg['contour_frequency']=float(os.environ['CLOUD_FREQUENCY'])
 if os.getenv('CLOUD_VARIANT'):
  O=O/os.environ['CLOUD_VARIANT'];O.mkdir(parents=True,exist_ok=True)
 C=apply(s,cfg);s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));
 if not os.getenv('CLOUD_PROOF_ONLY'):bpy.ops.render.render(write_still=True)
 # Dedicated field proof uses only native cloud geometry and identical camera-visible world.
 proof=bpy.data.scenes.new('082 Cloud field proof');proof.render.engine='BLENDER_EEVEE';proof.world=s.world.copy();proof.collection.children.link(C);cam=bpy.data.objects.new('082 Cloud proof camera',bpy.data.cameras.new('082 Cloud proof camera'));proof.collection.objects.link(cam);cam.location=(0,0,-20);cam.rotation_euler=(Vector((0,800,180))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=35;cam.data.clip_end=3000;proof.camera=cam;proof.render.resolution_x=1440;proof.render.resolution_y=640;proof.render.resolution_percentage=100;proof.render.threads_mode='FIXED';proof.render.threads=4;proof.view_settings.view_transform=s.view_settings.view_transform;proof.view_settings.look=s.view_settings.look;proof.view_settings.exposure=s.view_settings.exposure;proof.view_settings.gamma=s.view_settings.gamma;bpy.context.window.scene=proof;proof.render.filepath=str(O/'detail.png');bpy.ops.render.render(write_still=True)
 for ob in C.objects:ob.hide_render=True
 proof.render.filepath=str(O/'background.png');bpy.ops.render.render(write_still=True)
 for ob in C.objects:ob.hide_render=False
 # Native illumination pass; silhouette alpha remains separate from broad stroke filtering.
 proof.render.film_transparent=True;proof.render.image_settings.color_mode='RGBA';proof.view_settings.view_transform='Standard';proof.view_settings.look='None';proof.view_settings.exposure=0;proof.view_settings.gamma=1
 for mat in {m for o in C.objects for m in o.data.materials if m}:
  nt=mat.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None);dot=next((n for n in nt.nodes if n.type=='VECT_MATH' and n.operation=='DOT_PRODUCT'),None)
  if em and dot:
   for link in list(em.inputs[0].links):nt.links.remove(link)
   nt.links.new(dot.outputs['Value'],em.inputs[0]);em.inputs[1].default_value=1
 proof.render.filepath=str(O/'native-lightfield.png');bpy.ops.render.render(write_still=True);proof.render.film_transparent=False
 for o in C.objects:
  if o.name.startswith('082 Smooth'):o.hide_render=True
  else:
   m=bpy.data.materials.new('082 Mask black');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);o.data.materials.clear();o.data.materials.append(m)
 proof.world=bpy.data.worlds.new('082 Mask white');proof.world.use_nodes=True;proof.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);proof.render.filepath=str(O/'mask.png');bpy.ops.render.render(write_still=True)
