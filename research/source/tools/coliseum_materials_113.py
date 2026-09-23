"""Native light-driven masonry paint, no projected images."""
import bpy

def rgba(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)

def masonry(role='wall'):
 m=bpy.data.materials.new('113 Painted masonry '+role);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 def node(t,label=''):
  q=n.new(t);q.label=label;return q
 def math(op,*args):
  q=node('ShaderNodeMath');q.operation=op
  for i,x in enumerate(args):
   if isinstance(x,(int,float)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def mix(f,a,b,mode='MIX'):
  q=node('ShaderNodeMixRGB');q.blend_type=mode
  for i,x in enumerate([f,a,b]):
   if isinstance(x,(int,float,tuple,list)):q.inputs[i].default_value=x
   else:l.new(x,q.inputs[i])
  return q.outputs[0]
 def noise(sc,label,vec=None,detail=2):
  q=node('ShaderNodeTexNoise',label);q.inputs['Scale'].default_value=sc;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.7;l.new(vec or pos,q.inputs['Vector']);return q.outputs['Fac']
 def ramp(v,lo,hi):
  return math('MINIMUM',math('MAXIMUM',math('DIVIDE',math('SUBTRACT',v,lo),hi-lo),0),1)
 g=node('ShaderNodeNewGeometry');unscale=node('ShaderNodeVectorMath','Preserve authored weathering scale');unscale.operation='MULTIPLY';l.new(g.outputs['Position'],unscale.inputs[0]);unscale.inputs[1].default_value=(1/.715,)*3;offset=node('ShaderNodeVectorMath');offset.operation='ADD';l.new(unscale.outputs[0],offset.inputs[0]);offset.inputs[1].default_value=(0,-14*(1-1/.715),3.65*(1-1/.715));pos=offset.outputs[0];sep=node('ShaderNodeSeparateXYZ');l.new(pos,sep.inputs[0])
 diffuse=node('ShaderNodeBsdfDiffuse','Real light mapped into painted masonry families');diffuse.inputs['Color'].default_value=(.65,.65,.65,1);sr=node('ShaderNodeShaderToRGB');l.new(diffuse.outputs[0],sr.inputs[0]);bw=node('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);pal=node('ShaderNodeValToRGB','Warm exposed stone, violet recesses');pal.color_ramp.interpolation='EASE'
 colors=[(0,'10102c'),(.28,'28203f'),(.46,'4d3c50'),(.58,'8d6b58'),(.80,'ab8165'),(1,'bd9875')]
 for i,(p,c) in enumerate(colors):
  e=pal.color_ramp.elements[i] if i<2 else pal.color_ramp.elements.new(p);e.position=p;raw=rgba(c);e.color=tuple(v*.54 for v in raw[:3])+(1,)
 orient=node('ShaderNodeVectorMath','Broad form lighting');orient.operation='DOT_PRODUCT';l.new(g.outputs['Normal'],orient.inputs[0]);orient.inputs[1].default_value=(.38,-.67,.64);light=math('ADD',math('MULTIPLY',orient.outputs['Value'],.92),math('MULTIPLY',bw.outputs[0],.08));l.new(light,pal.inputs[0]);color=pal.outputs[0]
 # Coherent broken pigment islands, restrained coverage with quiet flat interiors.
 pigment=noise(.38,'Connected worn pigment islands');edgegrain=noise(3.6,'Broken mineral crust edges');pigment=math('ADD',pigment,math('MULTIPLY',math('SUBTRACT',edgegrain,.5),.10));mask=math('MULTIPLY',ramp(pigment,.660,.685),.38);color=mix(mask,color,rgba('242039'))
 # Fine pigment flecks/pits, subordinate to broad color regions.
 fine=noise(8.0,'Fine stone pits and dry pigment');pits=math('MULTIPLY',math('MULTIPLY',ramp(fine,.64,.75),.48),ramp(light,.30,.65));color=mix(pits,color,rgba('39323e'));fleck=math('MULTIPLY',math('MULTIPLY',math('SUBTRACT',1,ramp(fine,.24,.34)),.16),ramp(light,.35,.68));color=mix(fleck,color,rgba('b68b70'))
 # Long thin runoff follows world vertical, strongest below known structural tiers.
 v=node('ShaderNodeVectorMath','Vertical runoff scale');v.operation='MULTIPLY';l.new(pos,v.inputs[0]);v.inputs[1].default_value=(2,2,.055);run=noise(1,'Interrupted vertical runoff',v.outputs[0]);run=ramp(run,.61,.73)
 z=sep.outputs['Z'];bandmask=0
 for band in [21,39,57,72]:
  dz=math('SUBTRACT',band,z);below=math('MULTIPLY',math('GREATER_THAN',dz,0),math('LESS_THAN',dz,7));fade=math('SUBTRACT',1,math('MINIMUM',math('MAXIMUM',math('DIVIDE',dz,7),0),1));bandmask=math('MAXIMUM',bandmask,math('MULTIPLY',below,fade))
 fracturemask=0
 for x in [-43,7,60]:fracturemask=math('MAXIMUM',fracturemask,math('SUBTRACT',1,math('MINIMUM',math('DIVIDE',math('ABSOLUTE',math('SUBTRACT',sep.outputs['X'],x)),5),1)))
 upper=math('MULTIPLY',math('GREATER_THAN',z,59),math('LESS_THAN',z,77));bandmask=math('MAXIMUM',bandmask,math('MULTIPLY',upper,fracturemask))
 stain=math('MULTIPLY',math('MULTIPLY',run,bandmask),.88);color=mix(stain,color,rgba('201a30'))
 # Contact shade strengthens recessed construction without broad ambient blackening.
 ao=node('ShaderNodeAmbientOcclusion','Local crevice shade');ao.inputs['Distance'].default_value=.7;ao.inputs['Color'].default_value=(1,1,1,1);ao.inside=False;contact=math('MULTIPLY',math('SUBTRACT',1,ao.outputs['AO']),.4);color=mix(contact,color,rgba('302d38'))
 # Damaged water paths share angular locations across the complete wall height.
 # Direction is architectural/world-space, never screen-projected.
 at=node('ShaderNodeMath','Angular water paths');at.operation='ARCTAN2'
 l.new(math('SUBTRACT',sep.outputs['Y'],347),at.inputs[0]);l.new(sep.outputs['X'],at.inputs[1])
 angle=at.outputs[0];paths=0
 for a,width in [(-2.42,.027),(-2.05,.033),(-1.62,.026),(-1.30,.036),(-.91,.024),(-.46,.020)]:
  distance=math('ABSOLUTE',math('SUBTRACT',angle,a));path=math('SUBTRACT',1,ramp(distance,width*.35,width))
  paths=math('MAXIMUM',paths,path)
 # Patchy branching feather around the flow centers, with fine gritty breakup.
 flowvec=node('ShaderNodeVectorMath','Water follows gravity');flowvec.operation='MULTIPLY';l.new(pos,flowvec.inputs[0]);flowvec.inputs[1].default_value=(.9,.9,.42)
 flow=noise(1.9,'Grime branches',flowvec.outputs[0],3)
 broken=ramp(flow,.51,.57);pathmask=math('MULTIPLY',paths,broken)
 pathmask=math('MULTIPLY',pathmask,math('ADD',.12,math('MULTIPLY',bandmask,.88)))
 color=mix(math('MULTIPLY',pathmask,.90),color,rgba('100e23'))
 # Soot / mineral deposit directly at masonry recesses is stronger than exposed wall pigment.
 contactdeep=math('MULTIPLY',math('SUBTRACT',1,ao.outputs['AO']),.65)
 color=mix(contactdeep,color,rgba('191527'))
 if role=='recess':color=mix(.94,color,rgba('121020'))
 if role=='fracture':color=mix(.24,color,rgba('a27b62'))
 if role=='detail':color=mix(.18,color,rgba('574953'))
 if role in ['arch_molding','band','pier','tower']:
  gloss=node('ShaderNodeBsdfGlossy','Restrained worn edge catch');gloss.inputs['Roughness'].default_value=.54;st=node('ShaderNodeShaderToRGB');l.new(gloss.outputs[0],st.inputs[0]);b=node('ShaderNodeRGBToBW');l.new(st.outputs[0],b.inputs[0]);spec=math('MULTIPLY',ramp(b.outputs[0],.12,.50),.21);spec=math('MULTIPLY',spec,math('SUBTRACT',1,ramp(fine,.55,.70)));color=mix(spec,color,rgba('c3a082'))
 em=node('ShaderNodeEmission');l.new(color,em.inputs[0]);out=node('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs[0]);m['reference']='UCL-01';m['projected_artwork']=False;m['role']=role
 return m

def apply_materials(collection):
 cache={};counts={}
 for ob in collection.all_objects:
  if ob.type!='MESH':continue
  role=ob.get('coliseum_role','wall')
  if role not in cache:cache[role]=masonry(role)
  # Geometry agent uses one clay slot; preserve shared intact kit meshes.
  ob.data.materials.clear();ob.data.materials.append(cache[role]);counts[role]=counts.get(role,0)+1
 # Give real shallow fracture interiors a dark cavity family, avoiding bright double-line channels.
 from mathutils import Vector,Matrix
 import math
 inverse_lean=Matrix.Rotation(math.radians(-2),4,'X');anchor=Vector((0,-14,3.65));recess=masonry('recess');assigned=0
 for ob in collection.objects:
  if ob.type!='MESH' or ob.get('localized_damage')!='shallow crown-connected geometric recess':continue
  slot=len(ob.data.materials);ob.data.materials.append(recess)
  for poly in ob.data.polygons:
   w=ob.matrix_world@poly.center;auth=anchor+(w-anchor)/.715;v=inverse_lean@(auth-Vector((0,347,0)));radius=math.hypot(v.x,v.y)/(1-.055*v.z/78)
   if v.z>65 and 74.50<radius<74.94:poly.material_index=slot;assigned+=1
 counts['recess_faces']=assigned
 return counts
