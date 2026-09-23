"""239 private road pigment refinement; preserve pale banks, relief, cracks and AO."""
import bpy,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/road-paint-239'

def apply(scene):
 ob=bpy.data.objects['Street foundation'];old=ob.material_slots[0].material;assert not old.get('239 road paint'),'Apply239 once'
 before={o.name:(o.data,tuple(v for row in o.matrix_world for v in row),tuple(sl.material for sl in o.material_slots))for o in bpy.data.objects if o.type=='MESH'}
 m=old.copy();m.name='239 Deliberate dark earth fields | '+old.name;m['239 road paint']=True;old.use_fake_user=True;n=m.node_tree.nodes;l=m.node_tree.links
 region=n['Mix (Legacy).008'];receiver=n['Mix (Legacy).012'];tex=n['Image Texture'];uv=tex.inputs['Vector'].links[0].from_socket;original=tex.outputs['Color'];assert receiver.inputs[1].links[0].from_node==tex
 pale=[(x.from_node.name,x.from_socket.name)for x in region.inputs[2].links];mask=[(x.from_node.name,x.from_socket.name)for x in region.inputs[0].links]
 def mathn(op,a,b=0,label=''):
  q=n.new('ShaderNodeMath');q.operation=op;q.label='239 '+label
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(v,a,b):
  q=n.new('ShaderNodeMapRange');q.clamp=True;q.interpolation_type='SMOOTHSTEP';q.label='239 ragged field falloff';l.new(v,q.inputs[0]);q.inputs[1].default_value=a;q.inputs[2].default_value=b;return q.outputs[0]
 def mix(f,a,b,op='MIX',label=''):
  q=n.new('ShaderNodeMixRGB');q.blend_type=op;q.label='239 '+label
  for i,v in enumerate((f,a,b)):
   if isinstance(v,(float,int,tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 geo=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],sep.inputs[0]);x,y=sep.outputs['X'],sep.outputs['Y']
 def noise(sx,sy,detail=2):
  v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(sx,sy,0);l.new(geo.outputs['Position'],v.inputs[0]);q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=1;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.68;l.new(v.outputs[0],q.inputs['Vector']);return q.outputs['Fac']
 boundary=mathn('SUBTRACT',noise(.85,1.8),.5);fine=mathn('SUBTRACT',noise(3.2,4.7),.5)
 rough=mathn('ADD',mathn('MULTIPLY',boundary,.70),mathn('MULTIPLY',fine,.10))
 def length_gate(start,end,fade):return mathn('MULTIPLY',ramp(y,start,start+fade),mathn('SUBTRACT',1,ramp(y,end-fade,end)))
 def lane(center,width,start,end,fade):
  distance=mathn('ABSOLUTE',mathn('SUBTRACT',x,center));edge=mathn('ADD',distance,rough)
  return mathn('MULTIPLY',mathn('SUBTRACT',1,ramp(edge,width*.38,width)),length_gate(start,end,fade))
 # The fields are intentionally unequal and curve gently with the open route.
 compcenter=mathn('ADD',-2.25,mathn('ADD',mathn('MULTIPLY',y,.125),mathn('MULTIPLY',mathn('SINE',mathn('MULTIPLY',y,.17)),.30)))
 compact=lane(compcenter,2.25,-7,29,5)
 dustcenter=mathn('ADD',4.2,mathn('ADD',mathn('MULTIPLY',y,-.095),mathn('MULTIPLY',mathn('SINE',mathn('ADD',mathn('MULTIPLY',y,.25),.7)),.45)))
 dust=lane(dustcenter,1.8,-3,25,4)
 mineralcenter=mathn('ADD',-4.8,mathn('MULTIPLY',y,.08));mineral=lane(mineralcenter,2.0,7,34,5)
 # Native9-tap sampling softens dense packed-image flecks only in selected fields.
 average=original;offsets=[(.14,0),(-.14,0),(0,.21),(0,-.21),(.10,.15),(-.10,.15),(.10,-.15),(-.10,-.15)]
 for i,(dx,dy)in enumerate(offsets,2):
  v=n.new('ShaderNodeVectorMath');v.operation='ADD';v.inputs[1].default_value=(dx/16.4,dy/45.5,0);l.new(uv,v.inputs[0]);t=n.new('ShaderNodeTexImage');t.image=tex.image;t.extension=tex.extension;t.interpolation=tex.interpolation;t.label='239 Native local pigment average';l.new(v.outputs[0],t.inputs['Vector']);average=mix(1/i,average,t.outputs['Color'],label='native texture averaging')
 quiet=mathn('MAXIMUM',mathn('MULTIPLY',compact,.78),mathn('MULTIPLY',mineral,.44))
 body=mix(quiet,original,average,label='selective quiet compacted pigment')
 body=mix(mathn('MULTIPLY',compact,.90),body,mix(1,body,(.76,.79,.84,1),'MULTIPLY'),label='darker compacted sweeping field')
 body=mix(mathn('MULTIPLY',dust,.76),body,mix(1,body,(1.24,1.17,1.08,1),'MULTIPLY'),label='unequal warm dust drift')
 body=mix(mathn('MULTIPLY',mineral,.72),body,mix(1,body,(.91,1.01,1.14,1),'MULTIPLY'),label='cool mineral-loaded shoulder field')
 # A low-strength broken pigment fringe gives boundary nuance without adding another blanket noise layer.
 fringe=mathn('MULTIPLY',dust,mathn('MULTIPLY',mathn('SUBTRACT',1,dust),4));grain=ramp(noise(6,10),.52,.67)
 body=mix(mathn('MULTIPLY',mathn('MULTIPLY',fringe,grain),.11),body,mix(1,body,(1.19,1.11,1.02,1),'MULTIPLY'),label='selective mineral fringe')
 l.new(body,receiver.inputs[1]);ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=m
 assert [(x.from_node.name,x.from_socket.name)for x in region.inputs[2].links]==pale
 assert [(x.from_node.name,x.from_socket.name)for x in region.inputs[0].links]==mask
 for name,(mesh,M,mats)in before.items():
  o=bpy.data.objects[name];assert o.data==mesh and tuple(v for row in o.matrix_world for v in row)==M
  if o!=ob:assert tuple(sl.material for sl in o.material_slots)==mats,name
 return {'study':239,'source':'rubble-variation-237','object':ob.name,'private_material':m.name,'original_material':old.name,'scope':'Only mainroad ImageTexture color feeding Mix(Legacy).012 input1, before retained18%AO','fields':['Unequal curved dark compaction y−7..29m','Warm rightward dust drift y−3..25m','Cool mineral left shoulder y7..34m'],'original_packed_image_unchanged':tex.image.name,'native_selective_quiet_filter':'9shadertexture taps,0.1–0.21m radii; no altered image asset','pale_branch_exact':pale,'road_bank_mask_exact':mask,'all_geometry_cracks_rocks_transforms_exact':True,'all_other_material_bindings_exact':True,'lighting_note':'Original road branch is emission pigment plus18%ambient occlusion; no native diffuse direct-shadow term added. Parent owns scoped character shadow response.','references':['UCL-01','DP-03','DP-08'],'status':'CPU-ready; actual native combined comparison required'}

if __name__=='__main__':
 O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/rubble-variation-237/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('239 ROAD READY',flush=True)
