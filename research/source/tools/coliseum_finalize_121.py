"""121 broader architectural integration, preserving120 and all locked surroundings."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-121';sys.path.insert(0,str(R/'tools'))
from coliseum_upper_121 import apply as upper
from coliseum_tower_121 import apply as towers
from coliseum_surface_121 import apply as weather
from coliseum_color_121 import apply as colors
from coliseum_depth_118 import cavity_shade
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-120/scene.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];prior={o.name:o.data for o in C.objects if o.type=='MESH'};t=time.time()
parts,ua=upper(C);ta=towers(C)
changed=[o for o in C.objects if o.type=='MESH' and prior.get(o.name)!=o.data]
regions=ua.get('weathering_regions_original_world',[])+ta.get('weathering_regions_original_world',[])
wa=weather(changed,regions);ca=cavity_shade(changed);pa=colors(C)
for name,data in [('upper-integration',ua),('tower-integration',ta),('surface-integration',wa),('cavity-integration',ca),('color-integration',pa)]:
 (O/(name+'.json')).write_text(json.dumps(data,indent=2))
(O/'generation-performance.json').write_text(json.dumps({'seconds':time.time()-t,'changed_mesh_objects':len(changed)},indent=2))
old=bpy.data.objects.get('110 Landmark contact ink')
if old:bpy.data.objects.remove(old,do_unlink=True)
old=bpy.data.collections.get('110 Contact ink source')
if old:bpy.data.collections.remove(old)
contacts=bpy.data.collections.new('110 Contact ink source');s.collection.children.link(contacts)
for ob in C.objects:
    if ob.type=='MESH' and (ob.get('coliseum_role') in ['wall','band','tower','pier','fracture'] or
                           (ob.get('bay') in [6,7,8,9,11,12] and ob.get('coliseum_role') in ['detail','arch_molding'])):
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
