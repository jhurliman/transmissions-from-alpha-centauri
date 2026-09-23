import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-139/weathering';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.use_freestyle=False;s.render.use_compositing=False;s.render.threads_mode='FIXED';s.render.threads=4;rows=[]
for m in bpy.data.materials:
 if m.library or not m.use_nodes:continue
 n,l=m.node_tree.nodes,m.node_tree.links;out=next((n for n in n if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
 if not out or out.inputs['Volume'].is_linked:continue
 q=next((q for q in n if q.label=='139 Connected sheltered violet-brown age field'),None);e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(0,0,0,1)
 if q and q.inputs[0].is_linked:l.new(q.inputs[0].links[0].from_socket,e.inputs[0]);rows.append(m.name)
 l.new(e.outputs[0],out.inputs['Surface'])
s.render.filepath=str(O/'deposit-mask.png');bpy.ops.render.render(write_still=True);(O/'mask-diagnostic.json').write_text(json.dumps({'materials_showing_mask':rows,'scope':'White actual finite deposit strength at shader on current saved geometry; other surface outputs black; no source save'},indent=2));print('DONE')
