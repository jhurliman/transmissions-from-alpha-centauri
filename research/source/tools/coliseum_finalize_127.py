"""127 equal clearances, continuous arcade walls and restrained painted grain."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-127';sys.path.insert(0,str(R/'tools'))
from coliseum_seams_127 import apply as seams
from coliseum_seam_repair_127 import apply as seam_repair
from coliseum_pipe_recess_127 import apply as pipe, capture_surfaces
from pipe_ink_transfer_127 import apply as pipe_ink
from coliseum_spacing_127 import apply as spacing
from coliseum_floaters_127 import apply as cleanup
from coliseum_surface_127 import apply as surface
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
from coliseum_ink_occlusion_110 import clip_contacts
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-126/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];t=time.time()
before_pipe=capture_surfaces();pipe_audit=pipe();pipe_ink_audit=pipe_ink(before_pipe,capture_surfaces())
audit={'pipe':pipe_audit,'pipe_ink':pipe_ink_audit,'seams':seams(C),'seam_repair':seam_repair(C),'spacing':spacing(C),'cleanup':cleanup(C),'surface':surface(C,.7)};audit['generation_seconds']=time.time()-t;(O/'generation.json').write_text(json.dumps(audit,indent=2,default=str))
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
s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.line_thickness=3840/1440;s.render.filepath=str(O/'main-4k.png');t=time.time();bpy.ops.render.render(write_still=True);(O/'render-performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[3840,2885]},indent=2))
