import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-160/right-repair'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-111/scene.blend'));ob=bpy.data.objects['COL110 U15 fractured upper wall R'];me=ob.data
D={'source':'111 pre112 clean mesh','target':ob.name,'matrix':list(map(list,ob.matrix_world)),'vertices':[list(v.co) for v in me.vertices],'faces':[list(p.vertices) for p in me.polygons]}
(O/'pre112-domain.json').write_text(json.dumps(D,indent=2));print(D,flush=True)
