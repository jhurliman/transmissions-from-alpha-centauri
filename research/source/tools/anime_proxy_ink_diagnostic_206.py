import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/characters-206/anime';bpy.ops.wm.open_mainfile(filepath=str(O/'clean-background.blend'));s=bpy.context.scene;rows=[]
for ob in s.objects:
 if ob.type!='GREASEPENCIL':continue
 for layer in ob.data.layers:
  for frame in layer.frames:
   for i,st in enumerate(frame.drawing.strokes):
    ps=[ob.matrix_world@p.position for p in st.points]
    if not ps:continue
    lo=[min(p[k]for p in ps)for k in range(3)];hi=[max(p[k]for p in ps)for k in range(3)]
    if not(-.5<lo[0]<=hi[0]<.5 and -6.95<lo[1]<=hi[1]<-6.05):continue
    rows.append(dict(object=ob.name,layer=layer.name,frame=frame.frame_number,stroke=i,count=len(ps),bounds=[lo,hi],points=[list(p)for p in ps],attributes=[(a.name,a.domain,a.data_type)for a in frame.drawing.attributes]))
(O/'proxy-ink-ownership.json').write_text(json.dumps(rows,indent=2));print([(r['object'],r['stroke'],r['count'],r['bounds'])for r in rows],flush=True)
