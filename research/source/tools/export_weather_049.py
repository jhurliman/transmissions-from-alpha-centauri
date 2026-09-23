import bpy,bmesh,json
from pathlib import Path
O=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/xenon-049');bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'))
col=bpy.data.collections.new('DAMAGE | light mirrored folded panel');col.asset_mark()
for o in bpy.data.objects:
 if o.name.startswith('049 lighter mirrored |'):col.objects.link(o)
bpy.data.libraries.write(str(O/'light-panel-kit.blend'),{col},fake_user=True)
q=next(o for o in col.objects if o.type=='MESH' and any(m and m.name.startswith('049 lighter panel') for m in o.data.materials));me=bpy.data.meshes.new_from_object(q.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me);unseen=set(bm.verts);cc=0
while unseen:
 todo=[unseen.pop()];cc+=1
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in unseen:unseen.remove(w);todo.append(w)
assert cc==1
p=O/'audit.json';d=json.loads(p.read_text());d['additional_panel']['connected_components']=cc;d['additional_panel']['asset']='light-panel-kit.blend';p.write_text(json.dumps(d,indent=2));bm.free()
