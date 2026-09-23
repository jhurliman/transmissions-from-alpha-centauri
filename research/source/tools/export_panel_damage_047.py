import bpy,bmesh,json
from pathlib import Path
O=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-047')
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
source=bpy.data.collections['047 | right gallery with sheet damage'];asset=bpy.data.collections.new('DAMAGE | folded panel bay 047');asset.asset_mark();asset['scope']='Two-panel bay with one lifted corner, localized seam wear and seven fixings plus an empty bore';asset['anchor']='Gallery-local coordinates; front y=.35; x=.011..2.789; z=.131..2.639'
for o in source.objects:
 if o.name.startswith('047 ') or (o.type=='MESH' and any(m and m.name.startswith('047 Seam') for m in o.data.materials)):asset.objects.link(o)
bpy.data.libraries.write(str(O/'panel-damage-kit.blend'),{asset},fake_user=True)
d=json.loads((O/'audit.json').read_text())
for e in d['panels']:
 o=bpy.data.objects[e['panel']];me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me);unseen=set(bm.verts);n=0
 while unseen:
  stack=[unseen.pop()];n+=1
  while stack:
   v=stack.pop()
   for ed in v.link_edges:
    u=ed.other_vert(v)
    if u in unseen:unseen.remove(u);stack.append(u)
 e['connected_components']=n;assert n==1;e['volume_positive']=e['volume']>0;bm.free()
d['reusable_asset']='panel-damage-kit.blend';(O/'audit.json').write_text(json.dumps(d,indent=2))
