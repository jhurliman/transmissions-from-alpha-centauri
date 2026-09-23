"""Full-scene native Line Art rollout of user-approved 095 controls.
Re-run for the chosen camera after geometry changes; never edit approved meshes.
"""
import bpy,sys,json,time
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
import os
O=R/os.environ.get('INK_OUTPUT','art/studies/lines-096');O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/os.environ.get('INK_BASE','art/studies/soil-094/scene-C.blend')));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
original=[(o,o.lineart.usage) for o in bpy.data.objects if hasattr(o,'lineart')]
placements=json.loads((R/'art/reviews/xenon-069/placements.json').read_text());damage={p['part'] for p in placements}
# Approved damage material slots also identify hosts added after placement inventory.
for o in bpy.data.objects:
 if o.type=='MESH' and any(m and ('crack' in m.name.lower() or 'fracture' in m.name.lower()) for m in o.data.materials) and o.name!='Street foundation':damage.add(o.name)
def screen_width(o,pixels):
 right=s.camera.matrix_world.to_quaternion()@Vector((1,0,0))
 for f in o.data.layers[0].frames:
  for st in f.drawing.strokes:
   for p in st.points:
    pos=Vector(p.position);a=world_to_camera_view(s,s.camera,pos);b=world_to_camera_view(s,s.camera,pos+right);p.radius=pixels/max(abs(b.x-a.x)*s.render.resolution_x,1)
audit={'base':'soil-094C','damage_hosts':sorted(damage),'passes':[]};start=time.time()
for key,px in [('contacts',.6),('damage',.45)]:
 for o,_ in original:
  if o.type!='MESH':continue
  reserved=any(t in o.name.lower() for t in ['dome','sky','cloud','sun'])
  o.lineart.usage='OCCLUSION_ONLY' if reserved or (key=='damage' and o.name not in damage) else 'INCLUDE'
 ink=add_intersection_ink(s.collection,'096 '+key+' ink',radius=.004);m=ink.modifiers[0];m.source_type='SCENE';m.use_intersection=key=='contacts';m.use_material=key=='damage'
 print('BAKE_START',key,time.time()-start,flush=True)
 n=bake_intersection_ink(ink);screen_width(ink,px)
 # Structural contacts use the approved heavier 095 width near ground-footing areas.
 if key=='contacts':
  contacts=json.loads((R/'art/studies/lines-095/contacts.json').read_text())
  for f in ink.data.layers[0].frames:
   for st in f.drawing.strokes:
    for p in st.points:
     pos=p.position
     if any(all(a['min'][k]-.03<=pos[k]<=a['max'][k]+.03 for k in range(3)) for a in contacts):p.radius*=.8/.6
 audit['passes'].append({'pass':key,'strokes':n,'screen_radius_px':px,'elapsed_s':time.time()-start});(O/'audit.json').write_text(json.dumps(audit,indent=2));print('BAKE_END',key,n,time.time()-start,flush=True)
from contact_filter_096 import filter_contact_ink
audit['contact_filter']=filter_contact_ink(bpy.data.objects['096 contacts ink']);(O/'audit.json').write_text(json.dumps(audit,indent=2))
for o,u in original:o.lineart.usage=u
s.render.use_border=False;s.render.resolution_percentage=100;s.render.use_freestyle=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
