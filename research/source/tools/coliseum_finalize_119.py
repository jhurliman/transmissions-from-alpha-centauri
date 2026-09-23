"""Visible bay8 study in the locked scene, with regenerated landmark contact ink."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-119';sys.path.insert(0,str(R/'tools'))
from coliseum_weathering_117 import apply,exposed_core
from coliseum_depth_118 import cavity_shade
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
objects=[o for o in C.objects if o.type=='MESH' and o.get('bay')==8]
audit=json.loads((O/'geometry-audit.json').read_text())
regions=audit['weathering_regions_original_world']
deposits=apply([o for o in objects if o.get('tier')==3],regions)
core=exposed_core();core_count=0
for ob in objects:
    attr=ob.data.attributes.get('117 Exposed core')
    if not attr:continue
    idx=len(ob.data.materials);ob.data.materials.append(core)
    for face in ob.data.polygons:
        if attr.data[face.index].value>.5:face.material_index=idx;core_count+=1
cavity=cavity_shade(objects)
(O/'material-audit.json').write_text(json.dumps({'deposits':deposits,'core_faces':core_count,'cavity':cavity},indent=2))
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
