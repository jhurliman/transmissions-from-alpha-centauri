"""129 thicker inward arch stones, consistent tower niches and calibrated lighter cornices."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-129';sys.path.insert(0,str(R/'tools'))
from coliseum_b10_prepared_128 import apply as b10
from coliseum_arch_thickness_129 import apply as arches
from coliseum_pillars_129 import apply as pillars
from coliseum_cornice_color_129 import apply as cornice
from coliseum_cornice_clearance_129 import apply as cornice_clearance
from coliseum_joint_shading_129 import apply as joint_shading
from coliseum_crown_repair_123 import topology
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-128/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];t=time.time()
oldslots=[(x.link,x.material)for x in bpy.data.objects['COL127 T2 continuous arcade wall'].material_slots]
audit={'b10':b10(C),'arches':arches(C)}
assert oldslots==[(x.link,x.material)for x in bpy.data.objects['COL127 T2 continuous arcade wall'].material_slots], 'Upper wall materials changed unexpectedly'
audit['pillars']=pillars(C);audit['cornice_clearance']=cornice_clearance(C);audit['cornice']=cornice(C);audit['joint_shading']=joint_shading(C,strength=1.,actual_diffuse=False,reduce_ao=True)
check=topology(bpy.data.objects['COL127 T2 continuous arcade wall']);audit['integrated_T2_topology']=check
if check['nonmanifold']or check['strict_crossings']:raise RuntimeError('Unsafe integrated upper arcade wall')
audit['generation_seconds']=time.time()-t
audit['held_unintegrated']=['129 connected B7 damage','129 exposed mineral/deposit material']
(O/'generation.json').write_text(json.dumps(audit,indent=2,default=str))
old=bpy.data.objects.get('110 Landmark contact ink')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.collections.get('110 Contact ink source')
if old:bpy.data.collections.remove(old)
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
 if ob.type=='MESH' and (ob.get('coliseum_role')in['wall','band','tower','pier','fracture']or(ob.get('bay')in[6,7,8,9,10,11,12]and ob.get('coliseum_role')in['detail','arch_molding'])):contacts.objects.link(ob)
usage={};members=set(C.objects)
for ob in s.objects:
 if ob.type=='MESH':usage[ob.name]=ob.lineart.usage;ob.lineart.usage='INCLUDE'if ob in members else'EXCLUDE'
t=time.time();ink=add_intersection_ink(contacts,'110 Landmark contact ink',radius=.09);count=bake_intersection_ink(ink)
for name,v in usage.items():
 if bpy.data.objects.get(name):bpy.data.objects[name].lineart.usage=v
(O/'ink-audit.json').write_text(json.dumps({'strokes':count,'seconds':time.time()-t,'clipping':clip_contacts(s)},indent=2))
s.render.use_freestyle=True;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.line_thickness=1;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
# Reload the saved artifact before rendering the final review image.
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'render-performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]},indent=2))
