import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-057'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-055/scene.blend'))
src=(R/'tools/build_finish_054.py').read_text();exec(src[src.index('def rgb('):src.index('# Sky:')])
with bpy.data.libraries.load(str(R/'art/reviews/surface-056/connected-tonal-islands.blend'),link=False) as (a,b):b.node_groups=['056 Connected tonal islands']
g=bpy.data.node_groups['056 Connected tonal islands'];records=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;wear=next((n for n in nt.nodes if n.type=='GROUP' and n.node_tree.name.startswith('051 ')),None)
 architectural=wear or m.name.startswith(('Dome oxidized','Sun-worn','Recessed structural','Weathered street','Oxidized edges'))
 if not architectural:continue
 em=next((n for n in nt.nodes if n.type=='EMISSION' and n.outputs[0].is_linked and n.inputs[0].is_linked),None)
 if not em:continue
 base=em.inputs[0].links[0].from_socket
 pipe='PIP |' in m.name;service=wear and 'Services' in wear.node_tree.name
 if pipe and any(k in m.name for k in ['blue-gray enamel','worn edge steel','dark machined steel']):
  sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(base,sep.inputs[0]);cool=op(nt,'GREATER_THAN',sep.outputs[2],sep.outputs[0]);gray=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,gray.inputs[0]);base=mix(nt,base,gray.outputs[0],op(nt,'MULTIPLY',cool,.82))
 strength=.90 if pipe else .72 if service else .55
 if m.name.startswith(('Ruin depth','Dome oxidized','Weathered street')):strength=.30
 geo=nt.nodes.new('ShaderNodeNewGeometry');tex=nt.nodes.new('ShaderNodeGroup');tex.node_tree=g;tex.label='057 Surface-interior tonal islands';nt.links.new(geo.outputs['Position'],tex.inputs['Position']);nt.links.new(base,tex.inputs['Base']);tex.inputs['Strength'].default_value=strength;nt.links.new(tex.outputs['Color'],em.inputs[0]);records.append({'material':m.name,'strength':strength,'neutralized_round_metal':bool(pipe and any(k in m.name for k in ['blue-gray enamel','worn edge steel','dark machined steel']))})
s=bpy.context.scene;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'materials.json').write_text(json.dumps(records,indent=2));bpy.ops.render.render(write_still=True)
# Native high-resolution camera crops, not enlarged preview pixels.
s.render.resolution_x=4320;s.render.resolution_y=3240;s.render.use_border=True;s.render.use_crop_to_border=True
for name,box in [('pipes',(280,120,560,670)),('facade',(1100,330,1440,830))]:
 x0,y0,x1,y1=box;s.render.border_min_x=x0/1440;s.render.border_max_x=x1/1440;s.render.border_min_y=1-y1/1080;s.render.border_max_y=1-y0/1080;s.render.filepath=str(O/(name+'-detail.png'));bpy.ops.render.render(write_still=True)
