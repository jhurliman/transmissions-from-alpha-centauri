"""Clean only newly collapsed numerical fracture slivers in C; broad faces unchanged."""
import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def cleanup_slivers(collection, variant="C"):
 records=json.loads((R/f'art/studies/coliseum-perspective-115/{variant}/new-slivers.json').read_text());groups={}
 for name,index,*_ in records:groups.setdefault(name,[]).append(index)
 audit=[]
 for name,indices in groups.items():
  ob=collection.objects.get(name)
  if not ob or ob.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(ob.data);bm.faces.ensure_lookup_table();before_open=sum(not e.is_manifold for e in bm.edges);before_v=len(bm.verts);before_f=len(bm.faces)
  targets=[bm.faces[i]for i in indices if i<len(bm.faces) and bm.faces[i].calc_area()<1e-9];edges=list({e for f in targets for e in f.edges});bmesh.ops.dissolve_degenerate(bm,dist=1e-5,edges=edges);bm.normal_update();after_open=sum(not e.is_manifold for e in bm.edges)
  accepted=after_open<=before_open
  row={'object':name,'target_faces':len(targets),'removed_vertices':before_v-len(bm.verts),'removed_faces':before_f-len(bm.faces),'nonmanifold_before':before_open,'nonmanifold_after':after_open,'accepted':accepted}
  if accepted:bm.to_mesh(ob.data);ob.data.update()
  bm.free();audit.append(row)
 return audit
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-perspective-115/C/scene.blend'));print('SLIVER_AUDIT',json.dumps(cleanup_slivers(bpy.data.collections['110 Coliseum detailed front ruin'])))
