"""Native material and geometric soil proof; no image textures."""
import bpy,math,json,random,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-081';CFG=json.loads((R/'config/soil-study-081.json').read_text())
def linear(v):
 v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def mat(cfg,name='081 compact earth',shade=1,target=None):
 m=target or bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes
 if target is None:n.clear()
 l=m.node_tree.links
 tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=cfg['noise_scale'];noise.inputs['Detail'].default_value=cfg['noise_detail'];noise.inputs['Roughness'].default_value=.62;stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(.85,1,1);l.new(tex.outputs['Object'],stretch.inputs[0]);l.new(stretch.outputs[0],noise.inputs['Vector'])
 if cfg.get('grain_mode')=='discrete':
  grid=n.new('ShaderNodeVectorMath');grid.operation='SCALE';grid.inputs['Scale'].default_value=80;l.new(stretch.outputs[0],grid.inputs[0]);floor=n.new('ShaderNodeVectorMath');floor.operation='FLOOR';l.new(grid.outputs[0],floor.inputs[0]);inv=n.new('ShaderNodeVectorMath');inv.operation='SCALE';inv.inputs['Scale'].default_value=1/80;l.new(floor.outputs[0],inv.inputs[0]);l.new(inv.outputs[0],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
 for e,rgb in zip(ramp.color_ramp.elements,[cfg['ramp_low'],cfg['ramp_high']]):e.color=tuple(linear(v)*shade for v in rgb)+(1,)
 clump=n.new('ShaderNodeTexNoise');clump.inputs['Scale'].default_value=1.2;clump.inputs['Detail'].default_value=1;l.new(stretch.outputs[0],clump.inputs['Vector']);mask=n.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.63;mask.inputs['From Max'].default_value=.78;mask.inputs['To Max'].default_value=.1;l.new(clump.outputs['Fac'],mask.inputs[0]);sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';l.new(noise.outputs['Fac'],sub.inputs[0]);l.new(mask.outputs[0],sub.inputs[1]);l.new(sub.outputs[0],ramp.inputs[0])
 if cfg.get('grain_mode')=='discrete':
  ramp.color_ramp.interpolation='CONSTANT'
  for i,(pos,rgb) in enumerate(zip([.2,.35,.44,.52,.61,.73],[(68,48,41),(73,52,44),(77,55,46),(80,58,48),(84,61,50),(90,65,53)])):
   el=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(pos);el.position=pos;el.color=tuple(linear(v)*shade for v in rgb)+(1,)
 if target:return ramp.outputs[0]
 em=n.new('ShaderNodeEmission');l.new(ramp.outputs[0],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs[0]);return m

def apply(scene,cfg):
 """Material-only integration. Preserve all soil geometry and pale footprint deposits."""
 ground=bpy.data.objects.get('Street foundation')
 if not ground:return None
 old=ground.data.materials[0];m=old.copy();m.name='081 calibrated road, preserved pale deposits';n=m.node_tree.nodes;l=m.node_tree.links
 em=next(x for x in n if x.type=='EMISSION');oldbase=em.inputs[0].links[0].from_socket
 blend=next(q for q in n if q.type=='MIX_RGB' and q.blend_type=='MIX' and q.inputs[1].is_linked and q.inputs[2].is_linked and q.inputs[1].links[0].from_node.type=='VALTORGB' and q.inputs[2].links[0].from_node.type=='VALTORGB')
 mask=blend.inputs[0].links[0].from_socket
 clean=mat(cfg,target=m)
 # Real occlusion remains a separate factor, rather than baking reference shadows.
 ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=.65;ao.samples=16
 sh=n.new('ShaderNodeMapRange');sh.inputs['To Min'].default_value=.55;sh.inputs['To Max'].default_value=1;l.new(ao.outputs['AO'],sh.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;l.new(clean,mul.inputs[1]);l.new(sh.outputs[0],mul.inputs[2])
 mix=n.new('ShaderNodeMixRGB');l.new(mask,mix.inputs[0]);l.new(mul.outputs[0],mix.inputs[1]);l.new(oldbase,mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0]);em.inputs[1].default_value=1
 ground.data.materials[0]=m
 return m

def cube(name,loc,scale,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o

def proof():
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES' if False else 'BLENDER_EEVEE';s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1370;s.render.resolution_y=746;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.world=bpy.data.worlds.new('081 studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.1,.1,1)
 bpy.ops.object.light_add(type='SUN',location=(-4,-6,9));sun=bpy.context.object;sun.rotation_euler=Vector((4,6,-9)).to_track_quat('-Z','Y').to_euler();sun.data.energy=2;sun.data.angle=.12
 m=mat(CFG);g=cube('081 editable soil slab',(0,0,-.25),(22,22,.5),m)
 bpy.ops.object.camera_add(location=(0,-10,8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=14.5;s.camera=cam
 s.render.filepath=str(O/'clean.png');bpy.ops.render.render(write_still=True)
 cam.location=(4,-10,6);cam.rotation_euler=(Vector((4,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=32
 # Actual triangular cross-section cuts. Axis-aligned segments reflect buried road structure.
 rng=random.Random(CFG['seed']);inner=mat(CFG,'081 exposed fracture',.38);g.data.materials.append(inner)
 lip=mat(CFG,'081 light responding fracture lip');n=lip.node_tree.nodes;l=lip.node_tree.links;em=next(x for x in n if x.type=='EMISSION');base=em.inputs[0].links[0].from_socket;gl=n.new('ShaderNodeBsdfGlossy');gl.inputs['Roughness'].default_value=.36;sr=n.new('ShaderNodeShaderToRGB');l.new(gl.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);mp=n.new('ShaderNodeMapRange');mp.clamp=True;mp.inputs['From Max'].default_value=1.5;mp.inputs['To Max'].default_value=.45;l.new(bw.outputs[0],mp.inputs[0]);mx=n.new('ShaderNodeMixRGB');l.new(mp.outputs[0],mx.inputs[0]);l.new(base,mx.inputs[1]);mx.inputs[2].default_value=tuple(linear(x) for x in (154,120,89))+(1,);l.new(mx.outputs[0],em.inputs[0])
 cutters=[];lips=[]
 for idx,(a,b) in enumerate([((-10,-3),(10,-3)),((-10,1.2),(10,1.2)),((-3,-8),(-3,6)),((3,-3),(3,8)),((-3,-3),(0,-.5))]):
  a=Vector(a);b=Vector(b);d=(b-a).normalized();p=Vector((-d.y,d.x));steps=max(8,int((b-a).length/.16));vs=[];fs=[];samples=[]
  for k in range(steps+1):
   t=k/steps;c=a.lerp(b,t)+p*rng.uniform(-.012,.012);w=rng.uniform(.014,.075)*(1 if (k//4+idx)%7 else .04);depth=rng.uniform(.026,.065);samples.append((c.copy(),w,depth))
   for xy,z in [(c-p*w,.025),(c+p*w,.025),(c,-depth)]:vs.append((*xy,z))
  fs=[(2,1,0),(3*steps,3*steps+1,3*steps+2)]
  for k in range(steps):
   for j in range(3):fs.append((3*k+j,3*k+(j+1)%3,3*k+3+(j+1)%3,3*k+3+j))
  me=bpy.data.meshes.new('081 V incision');me.from_pydata(vs,[],fs);me.materials.append(m);me.materials.append(inner)
  for f in me.polygons:f.material_index=1
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(me.name,me);s.collection.objects.link(ob);bpy.context.view_layer.objects.active=g;mod=g.modifiers.new('081 shallow incision','BOOLEAN');mod.operation='DIFFERENCE';mod.object=ob;bpy.ops.object.modifier_apply(modifier=mod.name);ob.hide_render=True;cutters.append(ob)
  for k in range(steps):
   if rng.random()<.32:continue
   verts=[];lipwidth=rng.uniform(.016,.032)
   for end,(pt,width,dep) in enumerate((samples[k],samples[k+1])):
    edge=width*dep/(dep+.025);lw=lipwidth*rng.uniform(.25,1.2)
    for off,z in ((edge,-.003),(edge+lw,.003),(edge+lw+.012,0)):verts.append((*(pt+p*off),z))
   mesh=bpy.data.meshes.new('081 chipped earth lip');mesh.from_pydata(verts,[],[(0,3,4,1),(1,4,5,2)]);mesh.materials.append(lip);obj=bpy.data.objects.new(mesh.name,mesh);s.collection.objects.link(obj);lips.append(obj)
 # Every lip is clipped against the union of all incisions, including crossings.
 for obj in lips:
  bpy.context.view_layer.objects.active=obj
  solid=obj.modifiers.new('081 physical lip thickness','SOLIDIFY');solid.thickness=.007;bpy.ops.object.modifier_apply(modifier=solid.name)
  for cutter in cutters:
   mod=obj.modifiers.new('081 shared crack void clipping','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name)
 for cutter in cutters:bpy.data.objects.remove(cutter,do_unlink=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'cracks.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':proof()
