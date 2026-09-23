"""CPU topology/removed-volume audit for198 native panel losses."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-198';bpy.ops.wm.open_mainfile(filepath=str(O/'candidate.blend'));a=json.loads((O/'audit.json').read_text());rows=[]
def stats(me):
 bm=bmesh.new();bm.from_mesh(me);out={'volume':abs(bm.calc_volume(signed=True)),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'zero_area_faces':sum(f.calc_area()<1e-12 for f in bm.faces)};bm.free();return out
for r in a['native_damage']:
 o=bpy.data.objects[r['object']];old=bpy.data.meshes[o['198 source mesh']];b=stats(old);n=stats(o.data);row={'object':o.name,'before':b,'after':n,'removed_volume':b['volume']-n['volume'],'additional_edge_loss':r['additional_edge_loss']};assert row['removed_volume']>1e-7,row;assert n['nonmanifold_edges']==0,row;rows.append(row)
(O/'mesh-quality.json').write_text(json.dumps({'panels':rows,'all_removed_real_positive_volume':True,'all_closed_manifold':True,'total_panels':len(rows)},indent=2));print('198 MESH QUALITY PASS',len(rows))
