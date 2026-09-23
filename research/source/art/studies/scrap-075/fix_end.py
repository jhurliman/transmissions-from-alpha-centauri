import bpy
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;C=bpy.data.collections['075 Scrap integration']
for o in C.objects:
 if o.get('zone')=='end' and 'torn hollow casing' in o.name:o.rotation_euler.x=1.35
for o in C.objects:
 if o.get('family')=='hero anchor' and 'torn hollow casing' in o.name:
  if abs(o.location.x+.5)<.01:o.scale=(.87,.87,.87);o.rotation_euler.x=-2.6;o.location.z=.40
  elif abs(o.location.x-4.2)<.01:o.scale=(1.2375,)*3;o.rotation_euler.x=-2.4;o.location.z=.65
K=bpy.data.collections.get('KIT | 075 battered scrap masters')
if K is None:
 with bpy.data.libraries.load(str(O/'kit.blend'),link=False) as (a,b):b.collections=['KIT | 075 battered scrap masters']
 K=b.collections[0]
bpy.data.libraries.write(str(O/'kit.blend'),{C,K},fake_user=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
