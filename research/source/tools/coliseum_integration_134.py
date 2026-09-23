"""Integrate verified local crown repair, stable tessellation and attached weathering."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-134';O.mkdir(exist_ok=True)
def fingerprint(s):
 out={}
 for ob in s.objects:
  d={'transform':[list(x) for x in ob.matrix_world],'hidden':ob.hide_render,'materials':[x.material.name if x.material else None for x in ob.material_slots]}
  if ob.type=='MESH':
   a=array.array('f',[0])*(len(ob.data.vertices)*3);ob.data.vertices.foreach_get('co',a);b=array.array('i',[0])*len(ob.data.loops);ob.data.loops.foreach_get('vertex_index',b);d['mesh']=hashlib.sha256(a.tobytes()+b.tobytes()).hexdigest()
  if ob.type=='CAMERA':d['camera']=[ob.data.lens,ob.data.shift_x,ob.data.shift_y,ob.data.ortho_scale]
  if ob.type=='LIGHT':d['light']=[ob.data.energy,list(ob.data.color)]
  out[ob.name]=d
 return out
if 'render' not in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'standalone/scene.blend'));s=bpy.context.scene;before=fingerprint(s);C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library)
 from coliseum_triangulation_134 import apply as triangulate
 from coliseum_fracture_134 import apply as fracture
 from coliseum_weathering_134 import apply as weather
 t=time.time();audit={'triangulation':triangulate(C),'fracture':fracture(C),'weathering':weather(C,1.0)};audit['seconds']=time.time()-t
 after=fingerprint(s);changes={k:[f for f in v if v[f]!=after.get(k,{}).get(f)]for k,v in before.items() if v!=after.get(k)}
 allowed={'COL110 U12 fractured upper wall R','COL127 T2 continuous arcade wall','COL110 U9 fractured upper wall L'}
 assert set(before)==set(after),'Object inventory changed'
 assert all(not any(f in fs for f in ['transform','hidden','camera','light']) for fs in changes.values())
 assert all(k in allowed for k,fs in changes.items() if 'mesh' in fs)
 (O/'generation.json').write_text(json.dumps(audit,indent=2,default=str));(O/'preservation.json').write_text(json.dumps({'changes':changes,'object_inventory_unchanged':True,'camera_lights_transforms_unchanged':True},indent=2))
 s.render.use_compositing=False;s.render.use_freestyle=True;s.render.use_border=False;s.render.use_crop_to_border=False
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.data.libraries.write(str(O/'kit.blend'),{C},fake_user=True)
else:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'render_seconds':time.time()-t,'resolution':[3840,2885]},indent=2))
