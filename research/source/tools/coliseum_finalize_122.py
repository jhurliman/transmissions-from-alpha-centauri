"""122 regular upper-ring detail and depth-proportional shallow panel shade."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-122';sys.path.insert(0,str(R/'tools'))
from coliseum_upper_rhythm_122 import apply as rhythm
from coliseum_shallow_shade_122 import apply as shade
from coliseum_depth_118 import cavity_shade
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-121/scene.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];t=time.time()
result=rhythm(C)
ra=result[1] if isinstance(result,tuple) else result
for ob in C.objects:
 if ob.type!='MESH' or not ob.data.attributes.get('118 Recess interior'):continue
 has=any(m and m.use_nodes and any(n.label=='118 Modeled recess deposit shade' for n in m.node_tree.nodes) for m in ob.data.materials)
 if not has:cavity_shade([ob])
sa=shade(C)
brightened=[]
for m in {m for ob in C.objects if ob.type=='MESH' and ob.get('feature')=='shared undercornice dentil' for m in ob.material_slots if m.material for m in [m.material]}:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='RGB' and n.label=='User midpoint: outward light and downward shade':
   before=list(n.outputs[0].default_value)
   n.outputs[0].default_value=tuple(min(1.,v**(1/2.2)*1.35)**2.2 for v in before[:3])+(1,)
   brightened.append({'material':m.name,'before':before,'after':list(n.outputs[0].default_value),'perceived_brightness_factor':1.35})
(O/'cornice-brightness.json').write_text(json.dumps(brightened,indent=2))
(O/'rhythm-integration.json').write_text(json.dumps(ra,indent=2));(O/'shade-integration.json').write_text(json.dumps(sa,indent=2))
(O/'generation-performance.json').write_text(json.dumps({'seconds':time.time()-t},indent=2))
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
