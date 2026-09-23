"""125 selected asymmetric apertures and recessed platforms."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_columns_124 import apply as columns
from sky_gradient_125 import apply as sky
from coliseum_arch_ratio_125 import apply as apertures
from coliseum_platforms_125 import apply as platforms
from coliseum_armature_124 import apply as armature
from coliseum_cornice_material_124 import apply as cornice
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
O=R/'art/studies/coliseum-125';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-123/scene.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];start=time.time()
aa=apertures(C,width_reduction=.20,height_reduction=.05);pp=platforms(C);cc=columns(C);cc=cc[1] if isinstance(cc,tuple) else cc
audit={'sky':sky(),'apertures':aa,'platforms':pp,'columns':cc,'armature':armature(C),'cornice':cornice(C)}
audit['generation_seconds']=time.time()-start
(O/'generation.json').write_text(json.dumps(audit,indent=2,default=str))
old=bpy.data.objects.get('110 Landmark contact ink')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.collections.get('110 Contact ink source')
if old:bpy.data.collections.remove(old)
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
 if ob.type=='MESH' and (ob.get('coliseum_role') in ['wall','band','tower','pier','fracture'] or (ob.get('bay') in [6,7,8,9,10,11,12] and ob.get('coliseum_role') in ['detail','arch_molding'])):contacts.objects.link(ob)
usage={};members=set(C.objects)
for ob in s.objects:
 if ob.type=='MESH':usage[ob.name]=ob.lineart.usage;ob.lineart.usage='INCLUDE' if ob in members else 'EXCLUDE'
start=time.time();ink=add_intersection_ink(contacts,'110 Landmark contact ink',radius=.09);count=bake_intersection_ink(ink)
for name,v in usage.items():
 if bpy.data.objects.get(name):bpy.data.objects[name].lineart.usage=v
(O/'ink-audit.json').write_text(json.dumps({'strokes':count,'seconds':time.time()-start,'clipping':clip_contacts(s)},indent=2))
s.render.use_freestyle=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.line_thickness=1;s.render.filepath=str(O/'main.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png')
start=time.time();bpy.ops.render.render(write_still=True)
(O/'render-performance.json').write_text(json.dumps({'seconds':time.time()-start,'resolution':[3840,2885]},indent=2))
