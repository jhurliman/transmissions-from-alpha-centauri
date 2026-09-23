import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-125/fracture'
bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'));rows=[]
for name in ['COL110 U8 fractured upper wall L','COL110 U8 fractured upper wall R']:
 ob=bpy.data.objects[name];m=ob.data;mask=m.attributes.get('117 Exposed core');idx=next(i for i,ma in enumerate(m.materials)if ma and ma.name.startswith('117 Exposed masonry core'));n=0
 if mask:
  for f in m.polygons:
   if mask.data[f.index].value>.5 and f.material_index!=idx:f.material_index=idx;n+=1
 rows.append({'object':name,'core_material':m.materials[idx].name,'reassigned_legacy_core_faces':n})
bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));(O/'material-audit.json').write_text(json.dumps(rows,indent=2))
