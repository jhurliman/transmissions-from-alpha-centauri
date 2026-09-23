from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
exec((R/'tools/validate_coliseum_116.py').read_text().split('x,xm=snapshot(')[0])
before,bm=snapshot(R/'art/studies/coliseum-123/scene.blend')
for k in ['A','B','C']:
 O=R/'art/studies/coliseum-124'/k;after,am=snapshot(O/'scene.blend')
 result={'baseline':'123','candidate':'124'+k,'nonlandmark_objects_compared':len(before),'object_changes':[n for n,v in before.items() if after.get(n)!=v],'unexpected_objects':sorted(set(after)-set(before)),'material_graphs_compared':len(bm),'material_changes':[n for n,v in bm.items() if am.get(n)!=v]}
 (O/'preservation.json').write_text(json.dumps(result,indent=2));print(k,json.dumps(result));assert not any(result[n] for n in ['object_changes','unexpected_objects','material_changes'])
 bpy.data.libraries.write(str(O/'kit.blend'),{bpy.data.collections['110 Coliseum detailed front ruin']},fake_user=True,compress=True)
