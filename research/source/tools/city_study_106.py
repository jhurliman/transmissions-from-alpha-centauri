import bpy,json,math,random,hashlib,ast,os
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-106';O.mkdir(parents=True,exist_ok=True);MODE=os.environ.get('CITY_MODE','placement')
def project(ob,dx=0,dy=0):
 return [world_to_camera_view(s,s.camera,ob.matrix_world@Vector(v)+Vector((dx,dy,0))).x*1440 for v in ob.bound_box]
def crop_render(path):
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=520/1440;s.render.border_max_x=980/1440;s.render.border_min_y=1-505/1082;s.render.border_max_y=1-245/1082;s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
if MODE=='placement':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/scrap-105/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['101 Original city layout study']
 pair=[o for o in C.objects if o.get('reference_mass') in ['L04','L05'] and not o.hide_render];brown=next(o for o in C.objects if o.get('reference_mass')=='L06' and 'measured crown mass' in o.name);bounds=project(brown);target=(min(bounds)+max(bounds))/2
 low=0;high=30;depth_shift=55
 for _ in range(36):
  mid=(low+high)/2;edge=min(x for o in pair for x in project(o,mid,depth_shift))
  if edge<target:low=mid
  else:high=mid
 delta=(low+high)/2
 for ob in pair:ob.location+=Vector((delta,depth_shift,0))
 records=json.loads((R/'art/studies/city-101/A/reconstruction.json').read_text())['masses'];records={r['id']:r for r in records}
 additions=[]
 for new_id,src_id,x,y,scale in [('N_L1','L01',-9.5,48,.88),('N_L2','L02',-11.5,54,1.04),('N_R1','R07',12.9,48,.82),('N_R2','R05',14.8,55,1.03)]:
  rec=records[src_id];ox,oy=rec['position'];xf=Matrix.Translation((x,y,0))@Matrix.Diagonal((scale,scale,scale,1))@Matrix.Translation((-ox,-oy,0))
  source=[o for o in list(C.objects) if o.get('reference_mass')==src_id and not o.hide_render]
  for ob in source:
   q=ob.copy();q.data=ob.data.copy();C.objects.link(q);q.name='CITY106 '+new_id+' '+ob.name;q.matrix_world=xf@ob.matrix_world;q['reference_mass']=new_id;q['source_mass']=src_id
  additions.append({'id':new_id,'source':src_id,'position':[x,y],'scale':scale})
 bpy.context.view_layer.update()
 (O/'placement.json').write_text(json.dumps({'moved_pair':['L04','L05'],'shared_translation':[delta,depth_shift,0],'pair_left_edge_px':min(x for o in pair for x in project(o)),'brown_projected_bounds_x':[min(bounds),max(bounds)],'target_half_overlap_edge_px':target,'additions':additions},indent=2))
 s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4;bpy.ops.wm.save_as_mainfile(filepath=str(O/'placement.blend'));crop_render(O/'placement-preview.png')
elif MODE=='proof':
 for name,path in [('before',R/'art/studies/scrap-105/scene.blend'),('after',O/'placement.blend')]:
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  removed=set()
  for c in bpy.data.collections:
   if 'dome' in c.name.lower() or 'cloud' in c.name.lower():
    removed.update(c.all_objects)
  removed.update(ob for ob in s.objects if any(t in ob.name.lower() for t in ['sky','sun disc','sun disk','distant dust volume']))
  for ob in removed:bpy.data.objects.remove(ob,do_unlink=True)
  s.world=s.world.copy()
  for q in s.world.node_tree.nodes:
   if q.type=='OUTPUT_WORLD':
    for link in list(q.inputs['Volume'].links):s.world.node_tree.links.remove(link)
  s.render.film_transparent=False;s.compositing_node_group=None;nt=s.world.node_tree;out=next(q for q in nt.nodes if q.type=='OUTPUT_WORLD');bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(1,0,1,1);bg.inputs[1].default_value=1;old=out.inputs['Surface'].links[0].from_socket;ray=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(ray.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface']);s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
  crop_render(O/('magenta-'+name+'.png'))
else:
 # Reuse the native102 palette/stamp constructor with one-axis brush feathering.
 source=(R/'tools/city_facades_102.py').read_text();source=source.replace("centers.append((cx,cz));wx=rng.uniform(.035,.075);wz=rng.uniform(.012,.028)","centers.append((cx,cz));wx=rng.uniform(.035,.075);wz=rng.uniform(.012,.028)")
 source=source.replace("shape=mathnode('ADD',shape,warp);mask=mathnode('LESS_THAN',shape,1)","shape=mathnode('ADD',shape,warp);mask=mathnode('LESS_THAN',shape,1);feather=mathnode('MINIMUM',mathnode('MAXIMUM',mathnode('DIVIDE',mathnode('SUBTRACT',1,dz),.32),0),1);mask=mathnode('MULTIPLY',mask,feather)")
 module=ast.parse(source);defs=[n for n in module.body if isinstance(n,ast.FunctionDef) and n.name in ['lin','rgb','rgba','scale','blend','material']];exec(compile(ast.Module(body=defs,type_ignores=[]),'106_native_stamps','exec'),globals())
 records={r['id']:r for r in json.loads((R/'art/studies/city-101/A/reconstruction.json').read_text())['masses']};basecounts={r['id']:r['paint_stamps'] for r in json.loads((R/'art/studies/city-102/changes.json').read_text())['masses']}
 for variant,factor in [('A',2),('B',4),('C',8)]:
  bpy.ops.wm.open_mainfile(filepath=str(O/'placement.blend'));s=bpy.context.scene;folder=O/variant;folder.mkdir(exist_ok=True);audit=[]
  for ob in bpy.data.collections['101 Original city layout study'].objects:
   if ob.hide_render or 'measured crown mass' not in ob.name:continue
   mid=ob['reference_mass'];src=ob.get('source_mass',mid);seed=int(hashlib.sha256(mid.encode()).hexdigest()[:8],16);count=basecounts[src]*factor
   mat=material(mid,'106 feathered pigment '+variant,rgb(records[src]['color_hex']),seed,marks=count);mat.name='CITY106 '+variant+' '+mid+' feathered strokes';ob.data=ob.data.copy();ob.data.materials[0]=mat;audit.append({'id':mid,'strokes':count,'base_count':basecounts[src]})
  (folder/'marks.json').write_text(json.dumps(audit,indent=2));s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.filepath=str(folder/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'))
  if MODE=='previews':crop_render(folder/'preview.png')
  else:bpy.ops.render.render(write_still=True)
