"""Material-only balance of232 walls after actual draft showed granite-like overtexture.
Preserves all67 native cuts, original transforms and successful230 native ink.
"""
import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/broken-walls-232'
def finish(old):
 m=old.copy();m.name='232 Balanced clustered mineral | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
 em=next(x for x in n if x.type=='EMISSION' and x.inputs['Color'].is_linked)
 # Start from the retained source lighting/palette, bypassing230's cloudy multiplication.
 source=next((x.outputs[0]for x in n if x.type=='GROUP'and x.node_tree and x.node_tree.name.startswith('204 Half')),em.inputs['Color'].links[0].from_socket)
 def mathn(code,a,b):
  q=n.new('ShaderNodeMath');q.operation=code
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(v,a,b):
  q=n.new('ShaderNodeMapRange');q.clamp=True;l.new(v,q.inputs[0]);q.inputs[1].default_value=a;q.inputs[2].default_value=b;return q.outputs[0]
 def mix(f,a,b,op='MIX'):
  q=n.new('ShaderNodeMixRGB');q.blend_type=op
  for i,v in enumerate((f,a,b)):
   if isinstance(v,(int,float,tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 geo=n.new('ShaderNodeNewGeometry');p=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],p.inputs[0]);norm=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],norm.inputs[0]);useY=mathn('GREATER_THAN',mathn('ABSOLUTE',norm.outputs['X'],0),.6)
 u=mathn('ADD',mathn('MULTIPLY',useY,p.outputs['Y']),mathn('MULTIPLY',mathn('SUBTRACT',1,useY),p.outputs['X']))
 def coords(su,sz):
  q=n.new('ShaderNodeCombineXYZ');l.new(mathn('MULTIPLY',u,su),q.inputs['X']);l.new(mathn('MULTIPLY',p.outputs['Z'],sz),q.inputs['Y']);return q.outputs[0]
 def noise(su,sz):
  q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=1;q.inputs['Detail'].default_value=2.5;q.inputs['Roughness'].default_value=.8;l.new(coords(su,sz),q.inputs['Vector']);return q.outputs['Fac']
 def cells(su,sz,threshold):
  q=n.new('ShaderNodeTexVoronoi');q.voronoi_dimensions='2D';q.distance='EUCLIDEAN';q.inputs['Scale'].default_value=1;l.new(coords(su,sz),q.inputs['Vector']);return mathn('LESS_THAN',q.outputs['Distance'],threshold)
 # Sharp broken coating islands, with ragged medium/fine boundary rather than a soft cloud wash.
 mid=noise(1.2,1.2);fine=noise(9.5,9.5);field=mathn('ADD',mid,mathn('MULTIPLY',fine,.075))
 flake=ramp(field,.55,.62);rim=mathn('MULTIPLY',ramp(field,.54,.555),mathn('SUBTRACT',1,ramp(field,.575,.590)))
 body=mix(mathn('MULTIPLY',flake,.56),source,mix(1,source,(.68,.72,.78,1),'MULTIPLY'))
 body=mix(mathn('MULTIPLY',rim,.26),body,mix(1,source,(1.24,1.18,1.10,1),'MULTIPLY'))
 basal=mathn('SUBTRACT',1,ramp(p.outputs['Z'],.15,2.7));density=mathn('ADD',.10,mathn('MULTIPLY',basal,.70))
 gashes=mathn('MULTIPLY',cells(5,32,.19),ramp(noise(.9,.9),.40,.55));dots=cells(21,23,.13)
 body=mix(mathn('MULTIPLY',mathn('MAXIMUM',gashes,mathn('MULTIPLY',dots,.38)),density),body,(.018,.015,.023,1))
 rain=mathn('MULTIPLY',ramp(noise(17,.36),.59,.67),ramp(noise(1.2,1.8),.39,.60))
 body=mix(mathn('MULTIPLY',rain,.58),body,mix(1,source,(.46,.43,.43,1),'MULTIPLY'))
 grit=mathn('MULTIPLY',cells(12,16,.20),basal);body=mix(mathn('MULTIPLY',grit,.17),body,mix(1,source,(1.60,1.48,1.29,1),'MULTIPLY'))
 l.new(body,em.inputs['Color']);m['232 heavy mineral']=True;return m


def apply(scene):
 targets=[o for o in bpy.data.collections['133 Ruined transition structures'].objects if o.get('230 weathered')]
 cache={};rows=[];allmesh={o.name:o.data for o in bpy.data.objects if o.type=='MESH'}
 for ob in targets:
  assigned=[]
  for sl in ob.material_slots:
   old=sl.material
   if old not in cache:cache[old]=finish(old)
   sl.link='OBJECT';sl.material=cache[old];assigned.append({'old':old.name,'balanced':sl.material.name})
  rows.append({'object':ob.name,'materials':assigned})
 assert all(bpy.data.objects[name].data==me for name,me in allmesh.items())
 return {'study':'232 balanced finish','objects':len(targets),'private_materials':len(cache),'all_geometry_exact':True,'native67cuts_retained':True,'rows':rows,'changes':{'mineral_scale':1.2,'fine_boundary_scale':9.5,'fine_weight':.075,'rim_opacity':.26,'rim_gain':[1.24,1.18,1.10],'scuff_body_weight':.10,'scuff_base_add':.70},'reason':'Actual uninked232 draft looked like evenly distributed granite; larger clustered losses and quieter intervals now replace high-frequency field','status':'Actual combined render still required'}

if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-damage-232/walls-roofs.blend'));a=apply(bpy.context.scene);(O/'balanced-finish-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'balanced-walls-roofs.blend'));print('232 BALANCED FINISH READY',a['objects'],flush=True)
