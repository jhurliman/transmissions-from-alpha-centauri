import bpy,json,math
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/haze-variance-240'
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
mat=bpy.context.scene.objects['Distant dust volume - real lighting'].active_material.copy();n=mat.node_tree.nodes;l=mat.node_tree.links
out=next(x for x in n if x.type=='OUTPUT_MATERIAL'and x.is_active_output)
for x in list(out.inputs['Volume'].links):l.remove(x)
em=n.new('ShaderNodeEmission');l.new(n['240 Lower arcade density only'].outputs[0],em.inputs[0]);l.new(em.outputs[0],out.inputs['Surface'])
s=bpy.data.scenes.new('240 CPU field measurement');bpy.context.window.scene=s;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=1;s.cycles.use_denoising=False;s.render.resolution_x=192;s.render.resolution_y=96;s.render.resolution_percentage=100;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
me=bpy.data.meshes.new('field');me.from_pydata([(-50,160,0),(50,160,0),(50,160,25),(-50,160,25)],[],[(0,1,2,3)]);ob=bpy.data.objects.new('field',me);s.collection.objects.link(ob);me.materials.append(mat)
ca=bpy.data.cameras.new('probe');cam=bpy.data.objects.new('probe',ca);s.collection.objects.link(cam);s.camera=cam;ca.type='ORTHO';ca.ortho_scale=100;cam.location=(0,60,12.5);cam.rotation_euler=(Vector((0,160,12.5))-cam.location).to_track_quat('-Z','Y').to_euler()
results=[]
for y in [100,140,180,210]:
 ob.location.y=y-160;s.render.filepath=str(O/f'field-probe-y{y}.exr');bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False);p=list(im.pixels);v=sorted(p[i]for i in range(0,len(p),4)if p[i+3]>.9)
 avg=sum(v)/len(v);results.append({'world_y':y,'sample_count':len(v),'mean':avg,'standard_deviation':(sum((x-avg)**2 for x in v)/len(v))**.5,'percentiles':[v[int((len(v)-1)*q)]for q in [0,.05,.25,.5,.75,.95,1]],'fraction_below_0_3':sum(x<.3 for x in v)/len(v),'fraction_above_1_7':sum(x>1.7 for x in v)/len(v)})
(O/'native-field-probe.json').write_text(json.dumps({'method':'Actual shader evaluated in isolated Cycles CPU emission probe,192x96,X[-50,50],Z[0,25], four depth planes. No scene full render. Linear EXR data. Not projected-opacity measurement.','samples':results},indent=2));print('PROBE',results,flush=True)
