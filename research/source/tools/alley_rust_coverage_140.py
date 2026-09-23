"""Area-weighted native shader sample of all left Y beam surface triangles."""
import bpy,random,bisect,math,json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-rust-140';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));h=bpy.context.scene.objects['Architecture | gangway_single_Y_8m'];tri=[];weights=[];total=0
for ob in h.instance_collection.all_objects:
 if not ob.name.startswith(('Y arm','Y stem')):continue
 ob.data.calc_loop_triangles();M=h.matrix_world@ob.matrix_world
 for t in ob.data.loop_triangles:
  a,b,c=[M@ob.data.vertices[i].co for i in t.vertices];area=(b-a).cross(c-a).length/2
  if area>1e-10:tri.append((a,b,c));total+=area;weights.append(total)
rng=random.Random(140);pts=[]
for i in range(4096):
 a,b,c=tri[bisect.bisect_left(weights,rng.random()*total)];u=math.sqrt(rng.random());v=rng.random();pts.append((1-u)*a+u*(1-v)*b+u*v*c)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=1;s.render.resolution_x=256;s.render.resolution_y=256;s.render.resolution_percentage=100;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='16'
vs=[];fs=[]
for i,p in enumerate(pts):
 x=i%64;y=i//64;k=len(vs);vs.extend([(x,y,0),(x+1,y,0),(x+1,y+1,0),(x,y+1,0)]);fs.append((k,k+1,k+2,k+3))
me=bpy.data.meshes.new('Area samples');me.from_pydata(vs,[],fs);at=me.attributes.new('sample_position','FLOAT_VECTOR','POINT')
for i,p in enumerate(pts):
 for j in range(4):at.data[4*i+j].vector=p
ob=bpy.data.objects.new('Area samples',me);s.collection.objects.link(ob);m=bpy.data.materials.new('Native coverage');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();a=n.new('ShaderNodeAttribute');a.attribute_name='sample_position';noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.2;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.72;noise.inputs['Distortion'].default_value=.22;l.new(a.outputs['Vector'],noise.inputs['Vector']);em=n.new('ShaderNodeEmission');l.new(noise.outputs['Fac'],em.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs['Surface']);me.materials.append(m)
cam=bpy.data.cameras.new('Calibration');co=bpy.data.objects.new('Calibration',cam);s.collection.objects.link(co);co.location=(32,32,10);cam.type='ORTHO';cam.ortho_scale=64;s.camera=co;s.render.filepath=str(O/'coverage-field.png');bpy.ops.render.render(write_still=True)
pix=list(bpy.data.images.load(str(O/'coverage-field.png'),check_existing=False).pixels);values=[pix[((y*4+2)*256+x*4+2)*4]for y in range(64)for x in range(64)];sv=sorted(values);q=sv[int(len(sv)*.75)]
(O/'coverage-sampling.json').write_text(json.dumps({'samples':4096,'total_modeled_surface_area_m2':total,'threshold_for25percent':q,'coverage_at575':sum(v>.575 for v in values)/len(values),'method':'Area-weighted triangle samples evaluated through the identical native Noise shader; all modeled left Y arm/stem surfaces, including occluded backs; not camera-pixel weighting.'},indent=2))
