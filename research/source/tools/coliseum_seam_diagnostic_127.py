import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-127/seam-diagnostic';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import strict_crossings,topology
from coliseum_arch_ratio_125 import mapping
O.mkdir(exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/seams/geometry.blend'));original,world,unpack=mapping();rows=[]
for tier in [0,1,2]:
 o=bpy.data.objects[f'COL127 T{tier} continuous arcade wall'];m=o.data;m.calc_loop_triangles();pairs=strict_crossings(o,True);faces=set(i for pair in pairs for t in pair for i in[m.loop_triangles[t].polygon_index]);fd=[]
 for i in faces:
  f=m.polygons[i];co=[unpack(o.matrix_world@m.vertices[v].co)for v in f.vertices];fd.append({'face':i,'n':len(f.vertices),'v':list(f.vertices),'normal':list(f.normal),'coords':co,'material':o.material_slots[f.material_index].name if f.material_index<len(o.material_slots)else''})
 rows.append({'tier':tier,'topology':topology(o),'pairs':[{'triangles':p,'polygons':[m.loop_triangles[i].polygon_index for i in p]}for p in pairs],'faces':fd})
(O/'audit.json').write_text(json.dumps(rows,indent=2));print([(r['tier'],r['topology'],len(r['faces']))for r in rows])
