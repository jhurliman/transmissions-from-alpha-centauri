"""Current captured native-stroke 3D visibility diagnosis; read-only."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-156/regression';strokes=json.loads((O/'native-strokes.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-156/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.type=='MESH'and(ob.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();origin=s.camera.matrix_world.translation;boxes={'left':[125,889,181,908],'right':[3534,891,3589,915],'crack':[125,1810,235,1870]};rows=[]
for stroke in strokes:
 for a,b in zip(stroke['points'],stroke['points'][1:]):
  midpoint=[(a['pixel'][i]+b['pixel'][i])/2 for i in [0,1]];regions=[key for key,box in boxes.items()if box[0]<=midpoint[0]<=box[2]and box[1]<=midpoint[1]<=box[3]]
  if not regions:continue
  hits=[]
  for f in [0,.5,1]:
   p=Vector(a['world']).lerp(Vector(b['world']),f);delta=p-origin;ok,loc,n,face,owner,M=s.ray_cast(dg,origin,delta.normalized(),distance=delta.length+.01);hits.append({'fraction':f,'hit':owner.name if ok else None,'gap_m':delta.length-(loc-origin).length if ok else None})
  rows.append({'regions':regions,'shape':a['shape'],'lineset':stroke['lineset'],'nature':a['nature'],'pixels':[a['pixel'],b['pixel']],'world':[a['world'],b['world']],'currently_visible':a['visible'],'samples':hits})
(O/'native-stroke-occlusion.json').write_text(json.dumps(rows,indent=2));from collections import Counter
for key in boxes:
 rr=[r for r in rows if key in r['regions']];print(key,Counter(r['shape']for r in rr),'hidden',sum(all(h['gap_m']is not None and h['gap_m']>.02 for h in r['samples'])for r in rr),'/ ',len(rr))
