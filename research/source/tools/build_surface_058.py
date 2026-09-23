import bpy,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-058'
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-057/scene.blend'))
src=(R/'tools/build_finish_054.py').read_text();exec(src[src.index('def rgb('):src.index('# Sky:')])
def noise(nt,pos,scale,detail):
 n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=detail;nt.links.new(pos,n.inputs['Vector']);return n
records=[]
for m in bpy.data.materials:
 if not m.use_nodes:continue
 nt=m.node_tree;old=next((n for n in nt.nodes if n.label=='057 Surface-interior tonal islands'),None)
 if not old:continue
 if 'PIP |' in m.name or 'DUCT |' in m.name:
  records.append({'material':m.name,'action':'057 retained'});continue
 base=old.inputs['Base'].links[0].from_socket;dest=[l.to_socket for l in old.outputs['Color'].links];nt.nodes.remove(old)
 for d in dest:nt.links.new(base,d)
 facade=any(n.type=='GROUP' and n.node_tree.name.startswith('051 Facade') for n in nt.nodes)
 if not facade or m.name.startswith(('Ruin depth','045 ','046 ')):
  records.append({'material':m.name,'action':'057 removed'});continue
 geo=nt.nodes.new('ShaderNodeNewGeometry');co=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(co.outputs['Generated'],sep.inputs[0])
 # Median of three distances to bounding planes: ignores the surface's own plane.
 ds=[op(nt,'MINIMUM',sep.outputs[k],op(nt,'SUBTRACT',1,sep.outputs[k])) for k in ['X','Y','Z']]
 lo=op(nt,'MINIMUM',op(nt,'MINIMUM',ds[0],ds[1]),ds[2]);hi=op(nt,'MAXIMUM',op(nt,'MAXIMUM',ds[0],ds[1]),ds[2]);med=op(nt,'SUBTRACT',op(nt,'SUBTRACT',op(nt,'ADD',op(nt,'ADD',ds[0],ds[1]),ds[2]),lo),hi)
 edge=op(nt,'MAXIMUM',0,op(nt,'SUBTRACT',1,op(nt,'DIVIDE',med,.14)))
 warp=noise(nt,geo.outputs['Position'],.7,2);v=nt.nodes.new('ShaderNodeVectorMath');v.operation='SCALE';nt.links.new(warp.outputs['Color'],v.inputs[0]);v.inputs['Scale'].default_value=1.4;add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';nt.links.new(geo.outputs['Position'],add.inputs[0]);nt.links.new(v.outputs[0],add.inputs[1]);field=noise(nt,add.outputs[0],.65,2)
 # Broad, uncommon regions; edge preference lets small remnants reach interiors.
 threshold=op(nt,'SUBTRACT',.66,op(nt,'MULTIPLY',edge,.12));mask=op(nt,'GREATER_THAN',field.outputs['Fac'],threshold)
 boundary=noise(nt,geo.outputs['Position'],6,2);mask=op(nt,'MULTIPLY',mask,op(nt,'GREATER_THAN',boundary.outputs['Fac'],.36))
 colorsep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(base,colorsep.inputs[0]);warm=op(nt,'GREATER_THAN',colorsep.outputs[0],colorsep.outputs[2]);variation=noise(nt,geo.outputs['Position'],.23,1);which=op(nt,'GREATER_THAN',variation.outputs['Fac'],.50)
 cool=mix(nt,rgb('#484860'),rgb('#777582'),which);warmcol=mix(nt,rgb('#8d625b'),rgb('#bd8063'),which);palette=mix(nt,cool,warmcol,warm)
 result=mix(nt,base,palette,op(nt,'MULTIPLY',mask,.32))
 for d in dest:nt.links.new(result,d)
 records.append({'material':m.name,'action':'058 sparse edge-biased palette','mix':.32})
s=bpy.context.scene;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'materials.json').write_text(json.dumps(records,indent=2));bpy.ops.render.render(write_still=True)
s.render.resolution_x=4320;s.render.resolution_y=3240;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=1100/1440;s.render.border_max_x=1;s.render.border_min_y=1-830/1080;s.render.border_max_y=1-330/1080;s.render.filepath=str(O/'facade-detail.png');bpy.ops.render.render(write_still=True)
