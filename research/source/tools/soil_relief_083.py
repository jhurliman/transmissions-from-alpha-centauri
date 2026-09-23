"""Native compacted-soil relief and palette-quantized illumination proof."""
import bpy,math,random,json
from pathlib import Path
from mathutils import Vector,noise
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';C=json.loads((R/'config/soil-relief-083.json').read_text())
def lin(v):
 v=v/255;return v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4
def ns(x,y,f=1):return noise.noise_vector(Vector((x*f+13.1,y*f-7.3,8.7)))[0]
CLODS={}
rng_clods=random.Random(C['seed'])
for _ in range(30000):
 x=rng_clods.uniform(-2.5,2.5);y=rng_clods.uniform(-2.5,2.5);density=.2+.8*max(0,min(1,(ns(x,y,1.1)+.16)*2.4))
 if rng_clods.random()>density:continue
 radius=rng_clods.choice([.006,.010,.017])*rng_clods.uniform(.7,1.3);CLODS.setdefault((math.floor(x/.05),math.floor(y/.05)),[]).append((x,y,radius,rng_clods.uniform(.0006,.003),rng_clods.uniform(.65,1.4),rng_clods.uniform(0,math.tau)))
RIDGES=[]
for _ in range(13):
 angle=rng_clods.choice([0,math.pi/2]) + rng_clods.uniform(-.45,.45);length=rng_clods.uniform(.25,1.3);RIDGES.append((rng_clods.uniform(-2.2,2.2),rng_clods.uniform(-2.2,2.2),math.cos(angle),math.sin(angle),length,rng_clods.uniform(.012,.03),rng_clods.uniform(.001,.003)))
def height(x,y):
 macro=C['macro_height_m']*(.6*ns(x,y,.6)+.4*ns(x,y,1.3))
 # Sparse embedded-clod fields with genuine quieter compacted interstices.
 mask=.15+.85*max(0,min(1,(ns(x,y,1.1)+.16)*2.4));micro=C['micro_height_m']*mask*(.6*ns(x,y,36)+.4*ns(x,y,73))
 ridge=0
 for cx,cy,dx,dy,length,width,h in RIDGES:
  t=((x-cx)*dx+(y-cy)*dy)/length+.5
  if 0<t<1:
   across=-(x-cx)*dy+(y-cy)*dx+.018*math.sin(t*5)
   ridge+=h*math.exp(-(across/width)**2)*math.sin(math.pi*t)**.7
 mound=.017*math.exp(-((x+1.3)**2/.5+(y-.3)**2/1.8))+.009*math.exp(-((x-1.5)**2/.2+(y+.8)**2/.7))
 clod=0
 for ix in range(math.floor(x/.05)-1,math.floor(x/.05)+2):
  for iy in range(math.floor(y/.05)-1,math.floor(y/.05)+2):
   for cx,cy,rad,h,aspect,angle in CLODS.get((ix,iy),[]):
    dx=(x-cx)*math.cos(angle)+(y-cy)*math.sin(angle);dy=-(x-cx)*math.sin(angle)+(y-cy)*math.cos(angle);d=(dx/rad)**2+(dy/(rad*aspect))**2
    if d<5:clod=max(clod,h*math.exp(-d*2.2))
 return macro+micro*.15+ridge+mound+clod

def material(target=None):
 m=target or bpy.data.materials.new('083 lit earth pigment');m.use_nodes=True;n=m.node_tree.nodes
 if target is None:n.clear()
 l=m.node_tree.links
 diff=n.new('ShaderNodeBsdfDiffuse');diff.inputs['Color'].default_value=(1,1,1,1);diff.inputs['Roughness'].default_value=.6
 if target:
  co=n.new('ShaderNodeNewGeometry');uv=n.new('ShaderNodeVectorMath');uv.operation='SCALE';uv.inputs['Scale'].default_value=1/3.8;l.new(co.outputs['Position'],uv.inputs[0]);shift=n.new('ShaderNodeVectorMath');shift.operation='ADD';shift.inputs[1].default_value=(.5,.5,0);l.new(uv.outputs[0],shift.inputs[0])
  warp=n.new('ShaderNodeTexNoise');warp.inputs['Scale'].default_value=.24;warp.inputs['Detail'].default_value=1;l.new(co.outputs['Position'],warp.inputs['Vector']);amp=n.new('ShaderNodeVectorMath');amp.operation='SCALE';amp.inputs['Scale'].default_value=.18;l.new(warp.outputs['Color'],amp.inputs[0]);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(shift.outputs[0],add.inputs[0]);l.new(amp.outputs[0],add.inputs[1])
  tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'height.exr'),check_existing=True);tex.image.colorspace_settings.name='Non-Color';tex.image.pack();tex.extension='REPEAT';tex.interpolation='Linear';l.new(add.outputs[0],tex.inputs['Vector'])
  rot=n.new('ShaderNodeVectorRotate');rot.rotation_type='Z_AXIS';rot.inputs['Angle'].default_value=.73;l.new(add.outputs[0],rot.inputs['Vector']);tex2=n.new('ShaderNodeTexImage');tex2.image=tex.image;tex2.extension='REPEAT';tex2.interpolation='Linear';l.new(rot.outputs[0],tex2.inputs['Vector'])
  blend=n.new('ShaderNodeMixRGB');l.new(warp.outputs['Fac'],blend.inputs[0]);l.new(tex.outputs['Color'],blend.inputs[1]);l.new(tex2.outputs['Color'],blend.inputs[2]);bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=1;bump.inputs['Strength'].default_value=1;l.new(blend.outputs[0],bump.inputs['Height']);l.new(bump.outputs['Normal'],diff.inputs['Normal'])

 rgb=n.new('ShaderNodeShaderToRGB');l.new(diff.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='CONSTANT'
 for i,(p,c) in enumerate(zip([.0,.60,.68,.75,.82,.91],[(59,43,36),(68,48,41),(73,52,44),(79,57,47),(85,62,51),(94,70,56)])):
  e=r.color_ramp.elements[i] if i<2 else r.color_ramp.elements.new(min(p,1));e.position=min(p,1);e.color=tuple(lin(max(floor if target else 0,min(255,center+(v-center)*1.5))) for v,center,floor in zip(c,(79,57,47),(68,48,41)))+(1,)
 gain=n.new('ShaderNodeMath');gain.operation='MULTIPLY_ADD' if target else 'MULTIPLY';gain.inputs[1].default_value=3.2 if target else 2.4;gain.inputs[2].default_value=-2.34 if target else 0;gain.label='083 scene irradiance mapping' if target else '083 study irradiance mapping';l.new(bw.outputs[0],gain.inputs[0]);l.new(gain.outputs[0],r.inputs[0])
 if target:
  ambient=n.new('ShaderNodeVectorMath');ambient.operation='DOT_PRODUCT';ambient.inputs[1].default_value=(.2,-.5,.842615);l.new(bump.outputs['Normal'],ambient.inputs[0])
  ar=n.new('ShaderNodeValToRGB');ar.label='083 soft ambient normal shading';ar.color_ramp.interpolation='LINEAR'
  for e,p,c in zip(ar.color_ramp.elements,[.79,.89],[(64,46,39),(82,60,49)]):e.position=p;e.color=tuple(lin(v) for v in c)+(1,)
  l.new(ambient.outputs['Value'],ar.inputs[0]);weight=n.new('ShaderNodeMapRange');weight.clamp=True;weight.inputs['From Min'].default_value=.75;weight.inputs['From Max'].default_value=.95;l.new(bw.outputs[0],weight.inputs[0]);choice=n.new('ShaderNodeMixRGB');choice.label='083 ambient-to-direct pigment';l.new(weight.outputs[0],choice.inputs[0]);l.new(ar.outputs[0],choice.inputs[1]);l.new(r.outputs[0],choice.inputs[2]);return choice.outputs[0]

 em=n.new('ShaderNodeEmission');l.new(r.outputs[0],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs[0]);return m

def run():
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1370;s.render.resolution_y=746;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.world=bpy.data.worlds.new('083 fill');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.13,.13,.13,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 rng=random.Random(C['seed']);N=C['grid'];W=C['patch_width_m'];vs=[];fs=[]
 for j in range(N+1):
  for i in range(N+1):
   x=(i/N-.5)*W;y=(j/N-.5)*W
   if 0<i<N and 0<j<N:x+=rng.uniform(-.25,.25)*W/N;y+=rng.uniform(-.25,.25)*W/N
   vs.append((x,y,height(x,y)))
 for j in range(N):
  for i in range(N):
   a=j*(N+1)+i;b=a+1;c=a+N+1;d=c+1
   fs.extend([(a,b,d),(a,d,c)] if rng.random()<.5 else [(a,b,c),(b,d,c)])
 me=bpy.data.meshes.new('083 real soil heightfield');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(me.name,me);s.collection.objects.link(o);o.data.materials.append(material())
 for p in me.polygons:p.use_smooth=True
 bpy.ops.object.camera_add(location=(0,-5,4));cam=bpy.context.object;cam.rotation_euler=Vector((0,5,-4)).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.625;s.camera=cam
 bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=1.3;sun.data.angle=.08
 for label,direction in [('A',(.35,.65,-.7)),('B',(-.65,-.2,-.7))]:
  sun.rotation_euler=Vector(direction).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
 clay=bpy.data.materials.new('083 neutral clay');clay.use_nodes=True;clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.4,.4,.4,1);clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;s.view_layers[0].material_override=clay;s.render.filepath=str(O/'clay.png');bpy.ops.render.render(write_still=True);s.view_layers[0].material_override=None;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if __name__=='__main__':run()
