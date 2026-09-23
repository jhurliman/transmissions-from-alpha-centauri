import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-043';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-042/scene.blend'));s=bpy.context.scene
restored=[];warmed=[]
# Restore original service masters; leave architectural coating families untouched.
for o in s.objects:
 c=o.instance_collection
 if c and c.name.startswith('042 services | '):
  source=c.name[len('042 services | '):];orig=bpy.data.collections.get(source)
  if orig:o.instance_collection=orig;restored.append(o.name)
# Side road surface treatment is a warm, quieter contrast to the alley-facing blue cladding.
def rgb(h):
 v=[int(h[i:i+2],16)/255 for i in (1,3,5)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v)+(1,)
warm=bpy.data.materials['Cladding | warm neutral insert'].copy();warm.name='043 Side-road warm mineral coating'
nt=warm.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED')
for link in list(bs.inputs['Base Color'].links):nt.links.remove(link)
bs.inputs['Base Color'].default_value=rgb('#b29a81');bs.inputs['Roughness'].default_value=.9
# Recessed side-road elevation at y≈6 plus far return; do not change glazing, structural iron or pipes.
prefixes=('Side road far facade','Side road north building wall','Road-facing','Road window','Road elevation','Road portal','Side road broad','End wall upper','Loading portal')
for ob in s.objects:
 if ob.hide_render or ob.type!='MESH':continue
 if ob.name.startswith(prefixes):
  ob.data=ob.data.copy()
  for slot in ob.material_slots:
   if slot.material and (slot.material.name.startswith(('Cladding','042 Street coating'))):slot.material=warm;warmed.append(ob.name)
# The middle building's exposed end return faces the side road and must share its warm identity.
col=bpy.data.collections.get('042 right_middle | FAC | right_vertical_galleries')
if col:
 for ob in col.objects:
  if ob.type=='MESH' and ob.name.startswith('Gallery end return'):
   # local +X end corresponds to world y=6.
   avg=sum(v.co.x for v in ob.data.vertices)/len(ob.data.vertices)
   if avg>5:
    ob.data=ob.data.copy()
    for slot in ob.material_slots:slot.material=warm
    warmed.append(ob.name)
(O/'audit.json').write_text(json.dumps({'services_restored':restored,'warm_side_elevation_objects':warmed,'geometry_camera_lighting':'unchanged','service_weathering':'Facade flaking removed; specialized metal wear deferred'},indent=2))
s.render.use_freestyle=True;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
