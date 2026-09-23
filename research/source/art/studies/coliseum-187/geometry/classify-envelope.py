import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];O=R/'art/studies/coliseum-187/geometry';a=json.load(open(O/'audit.json'));bpy.ops.wm.open_mainfile(filepath=str(O/'fixed-shape-technical.blend'));out=[]
for row in a['targets']:
 ob=bpy.data.objects[row['object']];me=ob.data;verts={tuple(v.co):v.index for v in me.vertices}
 for c in row.get('source_envelope_exception_certificate',[]):
  if c['inside']:continue
  out.append(dict(object=ob.name,**c,vertex=verts.get(tuple(c['point_local']))))
(O/'envelope-classification.json').write_text(json.dumps(out,indent=2));print(out)
