import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scene-completion-201';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;m=s.objects['Distant dust volume - real lighting'].active_material;t=m.node_tree
out=next(n for n in t.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output);seen=set()
def walk(n):
 if n.name in seen:return
 seen.add(n.name)
 for i in n.inputs:
  for l in i.links:walk(l.from_node)
walk(out)
rows={}
for n in t.nodes:
 if n.name.startswith(('132','136')) and n.name in seen:
  rows[n.name]={'type':n.bl_idname,'inputs':{i.name:(list(i.default_value)if hasattr(i.default_value,'__len__')else i.default_value)for i in n.inputs if hasattr(i,'default_value')and not i.is_linked and i.enabled},'links':{i.name:[l.from_node.name+':'+l.from_socket.name for l in i.links]for i in n.inputs if i.is_linked}}
(O/'haze-current-raw.json').write_text(json.dumps(rows,indent=2,default=str))
assert rows['132 Near-clear to far-dense']['inputs']['From Min']==48
assert rows['132 Near-clear to far-dense']['inputs']['From Max']==205
assert rows['132 Near-clear to far-dense']['inputs']['To Max']==5
assert rows['136 Orange source depth']['inputs']['From Min']==48
assert rows['136 Orange source depth']['inputs']['From Max']==205
assert rows['136 Rear source cutoff']['inputs']['From Min']==205
assert rows['136 Rear source cutoff']['inputs']['From Max']==225
(O/'haze-current-graph.json').write_text(json.dumps({'material':m.name,'active_volume_ancestry':rows,'all_verified':True,'note':'132 relative density field retained;136 scales neutral scattering to0.25 and adds height/depth-limited orange radiance. Relative5x field is not5x net scattering.'},indent=2,default=str))
