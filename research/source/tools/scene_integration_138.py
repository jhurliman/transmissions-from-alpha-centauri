"""Combine inspected crown135, finite haze136E and bolt-led rust137."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/scene-details-138';O.mkdir(parents=True,exist_ok=True)
def objects(s):
 found=set(s.objects);todo=list(found)
 while todo:
  ob=todo.pop()
  if ob.instance_collection:
   for child in ob.instance_collection.all_objects:
    if child not in found:found.add(child);todo.append(child)
 return found
def fingerprint(s):
 out={}
 for ob in objects(s):
  d={'matrix':[list(v)for v in ob.matrix_world],'hidden':ob.hide_render,'instance':ob.instance_collection.name if ob.instance_collection else None,'materials':[m.material.name if m.material else None for m in ob.material_slots]}
  if ob.type=='MESH':
   a=array.array('f',[0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);d['geometry']=hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest();a=array.array('f',[0])*(len(ob.data.corner_normals)*3);ob.data.corner_normals.foreach_get('vector',a);d['normals']=hashlib.sha256(a.tobytes()).hexdigest()
  if ob.type=='CAMERA':d['camera']=[ob.data.lens,ob.data.shift_x,ob.data.shift_y,ob.data.ortho_scale]
  if ob.type=='LIGHT':d['light']=[ob.data.energy,list(ob.data.color)]
  out[ob.name]=d
 return out
def material_snapshot():
 def value(v):
  if isinstance(v,(int,float,str,bool))or v is None:return v
  try:return list(v)
  except:return getattr(v,'name',str(v))
 out={}
 for m in bpy.data.materials:
  if not m.use_nodes:out[m.name]=str(tuple(m.diffuse_color));continue
  nt=m.node_tree;nodes=[]
  for n in nt.nodes:
   row=[n.name,n.bl_idname,[(i.name,value(i.default_value))for i in n.inputs if hasattr(i,'default_value')]]
   for prop in ['operation','blend_type','interpolation_type','attribute_name','noise_dimensions','normalize','distribution']:
    if hasattr(n,prop):row.append((prop,value(getattr(n,prop))))
   if hasattr(n,'color_ramp'):row.append([(e.position,list(e.color))for e in n.color_ramp.elements])
   nodes.append(row)
  payload=[nodes,[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in nt.links]];out[m.name]=hashlib.sha256(json.dumps(payload,default=str).encode()).hexdigest()
 return out
if 'render' not in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-135/scene.blend'));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot();target=s.objects['Architecture | gangway_single_Y_8m'].instance_collection;allowed={ob.name for ob in target.all_objects}|{'Distant dust volume - real lighting'}
 from coliseum_haze_136 import apply as haze
 from alley_rust_137 import apply as rust
 t=time.time();audit={'source':'135 scene: inspected v2 crown and weathering','haze':haze(s,'E'),'rust':rust(s),'seconds':time.time()-t};after=fingerprint(s);mats_after=material_snapshot();changes={k:[f for f in v if v[f]!=after.get(k,{}).get(f)]for k,v in before.items()if v!=after.get(k)};mat_changes=[k for k,v in mats.items()if v!=mats_after.get(k)]
 assert set(before)==set(after),'Object inventory changed';assert all(k in allowed and fs==['materials']for k,fs in changes.items()),changes;assert not mat_changes,mat_changes
 (O/'preservation.json').write_text(json.dumps({'recursive_scene_and_instance_objects':len(before),'changed_objects':changes,'existing_material_nodes_changed':mat_changes,'geometry_normals_camera_lights_transforms_unchanged':True,'limitations':'Compared old material nodes/links/defaults and selected shader properties; not a whole-landmark contact certificate.'},indent=2));(O/'generation.json').write_text(json.dumps(audit,indent=2,default=str));s.render.use_compositing=False;s.render.use_freestyle=True;s.render.use_border=False;s.render.use_crop_to_border=False;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library);bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
else:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'render_seconds':time.time()-t,'resolution':[3840,2885]},indent=2))
