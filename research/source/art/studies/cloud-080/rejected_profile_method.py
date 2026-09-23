"""Native cloud silhouette meshes with independent smooth inset contours."""
import bpy,math,random,json,bmesh,os
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
 def profiles(seed,count,inner=False):
  rng=random.Random(seed)
  macro=[(x+rng.uniform(-.075,.075),rng.uniform(.11,.23),rng.uniform(.26,.61)) for x in (.21,.48,.73)]
  phase=rng.random()*math.tau
  lobes=[((j+rng.uniform(.1,.9))/count,rng.uniform(.25,.52)/count,rng.uniform(.09,.24)) for j in range(count)]
  def sample(t):
   cap=math.sqrt(max(0,1-((t-.045)/.045)**2)) if t<.045 else (math.sqrt(max(0,1-((t-.955)/.045)**2)) if t>.955 else 1)
   envelope=.12+sum(a*math.exp(-((t-x)/w)**2) for x,w,a in macro)
   spine=.09*math.sin(t*math.tau*1.3+phase)
   ripple=sum(a*math.exp(-((t-x)/w)**4) for x,w,a in lobes)
   if inner:
    return cap*(spine+envelope*.46+ripple*.35),cap*(spine-envelope*.22-ripple*.2)
   return cap*(spine+envelope*.65+ripple),cap*(spine-envelope*.36-ripple*.38)
  return sample
 # Angular bank layout expressed as real world geometry at distant y planes.
 banks=[(-.17,.32,.40,.07),(.15,.205,.32,.049),(-.12,.155,.30,.052),(-.24,.255,.16,.04),(.32,.29,.22,.047),(.035,.39,.30,.055),(-.02,.245,.13,.026),(.24,.12,.12,.026),(-.33,.13,.15,.022),(.05,.105,.10,.022),(.20,.36,.10,.018),(-.32,.40,.18,.033),(-.27,.30,.24,.048),(.29,.285,.23,.062)]
 records=[]
 for i,(cx,cz,width,height) in enumerate(banks):
  height*=1.5
  rng=random.Random(cfg['seed']+i*231);distance=rng.uniform(650,850);count=max(3,round(cfg['contour_frequency']*rng.uniform(1-cfg['per_cloud_frequency_jitter'],1+cfg['per_cloud_frequency_jitter'])));fn=profiles(cfg['seed']+i*431,count);samples=160
  def point(t,v,dep=0):return ((cx+(t-.5)*width)*distance,distance+dep,(cz+v*height)*distance)
  verts=[point(j/samples,fn(j/samples)[0]) for j in range(samples+1)]+[point(j/samples,fn(j/samples)[1]) for j in range(samples,-1,-1)]
  use_rare=height/1.5<cfg['large_cloud_inset_threshold'] and rng.random()<cfg['rare_color_chance'];ob=mesh('080 Cloud bank %02d'%i,verts,rare if use_rare else outer);ob['contour_frequency']=count;ob['seed']=cfg['seed']+i*431;ob['angular_width']=width;ob['angular_height']=height
  inset_count=max(2,round(count*ratio));inset_count=min(inset_count,count-1)
  if height/1.5>=cfg['large_cloud_inset_threshold']:
   smooth=profiles(cfg['seed']+i*431,inset_count,True);scale=1.0;start=.08;end=.93
   def inset_point(j,side):
    u=j/samples;t=start+(end-start)*u;up,lo=smooth(t);mid=(up+lo)/2;v=mid+((up if side==0 else lo)-mid)*math.sin(math.pi*u)**.32;return point(t,v,-.10)
   vs=[inset_point(j,0) for j in range(samples+1)]+[inset_point(j,1) for j in range(samples,-1,-1)]
   ins=mesh('080 Smooth inset %02d'%i,vs,inside);ins['contour_frequency']=inset_count;ins['outer_frequency']=count;ins['fit_scale']=scale
  records.append({'cloud':i,'outer_frequency':count,'inset_frequency':inset_count if height/1.5>=cfg['large_cloud_inset_threshold'] else None,'rare_palette':use_rare})
 for key in ['seed','contour_frequency','per_cloud_frequency_jitter','inset_frequency_ratio','large_cloud_inset_threshold','rare_color_chance']:C[key]=cfg[key]
 C['audit']=json.dumps(records)
 # Exclude cloud polygons from architectural ink without altering existing line settings.
 for o in C.objects:o.visible_shadow=False
 for ls in scene.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return C
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-079/scene.blend'));s=bpy.context.scene;C=apply(s);s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.use_border=False;s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));
 if not os.getenv('CLOUD_PROOF_ONLY'):bpy.ops.render.render(write_still=True)
 # Dedicated field proof uses only native cloud geometry and identical camera-visible world.
 proof=bpy.data.scenes.new('080 Cloud field proof');proof.render.engine='BLENDER_EEVEE';proof.world=s.world.copy();proof.collection.children.link(C);cam=bpy.data.objects.new('080 Cloud proof camera',bpy.data.cameras.new('080 Cloud proof camera'));proof.collection.objects.link(cam);cam.location=(0,0,-20);cam.rotation_euler=(Vector((0,800,180))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=700;cam.data.clip_end=3000;proof.camera=cam;proof.render.resolution_x=1440;proof.render.resolution_y=640;proof.render.resolution_percentage=100;proof.render.threads_mode='FIXED';proof.render.threads=4;proof.view_settings.view_transform=s.view_settings.view_transform;proof.view_settings.look=s.view_settings.look;proof.view_settings.exposure=s.view_settings.exposure;proof.view_settings.gamma=s.view_settings.gamma;bpy.context.window.scene=proof;proof.render.filepath=str(O/'detail.png');bpy.ops.render.render(write_still=True)
 for o in C.objects:
  if o.name.startswith('080 Smooth'):o.hide_render=True
  else:
   m=bpy.data.materials.new('080 Mask black');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(0,0,0,1);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);o.data.materials.clear();o.data.materials.append(m)
 proof.world=bpy.data.worlds.new('080 Mask white');proof.world.use_nodes=True;proof.world.node_tree.nodes['Background'].inputs[0].default_value=(1,1,1,1);proof.render.filepath=str(O/'mask.png');bpy.ops.render.render(write_still=True)
