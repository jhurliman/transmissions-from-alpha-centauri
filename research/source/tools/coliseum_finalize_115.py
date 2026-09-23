import bpy,sys,json,time,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));label=os.environ.get('COLISEUM_VARIANT','A');O=R/'art/studies/coliseum-115'/label;O.mkdir(parents=True,exist_ok=True)
from coliseum_ink_occlusion_110 import clip_contacts
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-perspective-115'/label/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
s.render.use_freestyle=True
if label in ['C','D','E']:
 from coliseum_sliver_cleanup_115 import cleanup_slivers
 (O/'sliver-cleanup.json').write_text(json.dumps(cleanup_slivers(C,variant=label),indent=2))
old=bpy.data.objects.get('110 Landmark contact ink')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.collections.get('110 Contact ink source')
if old:bpy.data.collections.remove(old)
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
 if ob.get('coliseum_role') in ['wall','band','tower','pier','fracture']:contacts.objects.link(ob)
usage={};members=set(C.objects)
for ob in s.objects:
 if ob.type=='MESH':usage[ob.name]=ob.lineart.usage;ob.lineart.usage='INCLUDE' if ob in members else 'EXCLUDE'
t=time.time();ink=add_intersection_ink(contacts,'110 Landmark contact ink',radius=.09);count=bake_intersection_ink(ink)
for name,u in usage.items():
 if bpy.data.objects.get(name):bpy.data.objects[name].lineart.usage=u
(O/'ink-rebuild.json').write_text(json.dumps({'source_strokes':count,'seconds':time.time()-t,'clipping':clip_contacts(s)},indent=2))
s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.line_thickness=1;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-4k.blend'));t=time.time();bpy.ops.render.render(write_still=True);(O/'render-performance.json').write_text(json.dumps({'resolution':[3840,2885],'seconds':time.time()-t},indent=2))
