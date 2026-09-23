"""120 native detail integration: fracture before support-checked shared cornices."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-120';sys.path.insert(0,str(R/'tools'))
from coliseum_fracture_120 import apply as fracture
from coliseum_arch_depth_120 import apply as arch_depth
from coliseum_cornice_120 import add_cornice_blocks
from coliseum_weathering_117 import exposed_core
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/scene.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
t=time.time();fa=fracture(C,bays=(8,));(O/'fracture-integration.json').write_text(json.dumps(fa,indent=2))
core=exposed_core()
for ob in C.objects:
 if ob.type!='MESH' or not ob.get('120 owner'):continue
 attr=ob.data.attributes.get('117 Exposed core');idx=len(ob.data.materials);ob.data.materials.append(core)
 if attr:
  for face in ob.data.polygons:
   if attr.data[face.index].value>.5:face.material_index=idx
added,ca=add_cornice_blocks(C,bays=range(18));(O/'cornice-integration.json').write_text(json.dumps(ca,indent=2))
(O/'arch-depth-audit.json').write_text(json.dumps(arch_depth(C),indent=2))
(O/'generation-performance.json').write_text(json.dumps({'seconds':time.time()-t},indent=2))
old=bpy.data.objects.get('110 Landmark contact ink')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.collections.get('110 Contact ink source')
if old:bpy.data.collections.remove(old)
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
    if ob.type=='MESH' and (ob.get('coliseum_role') in ['wall','band','tower','pier','fracture'] or
                           (ob.get('bay')==8 and ob.get('coliseum_role') in ['detail','arch_molding'])):
        contacts.objects.link(ob)
usage={};members=set(C.objects)
for ob in s.objects:
    if ob.type=='MESH':
        usage[ob.name]=ob.lineart.usage
        ob.lineart.usage='INCLUDE' if ob in members else 'EXCLUDE'
start=time.time();ink=add_intersection_ink(contacts,'110 Landmark contact ink',radius=.09)
count=bake_intersection_ink(ink)
for name,v in usage.items():
    if bpy.data.objects.get(name):bpy.data.objects[name].lineart.usage=v
(O/'ink-audit.json').write_text(json.dumps({'strokes':count,'seconds':time.time()-start,'clipping':clip_contacts(s)},indent=2))
s.render.use_freestyle=True;s.render.use_border=False;s.render.use_crop_to_border=False
s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100
s.render.line_thickness=1;s.render.filepath=str(O/'main.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440
s.render.filepath=str(O/'main-4k.png')
start=time.time();bpy.ops.render.render(write_still=True)
(O/'render-performance.json').write_text(json.dumps({'seconds':time.time()-start,'resolution':[3840,2885]},indent=2))
