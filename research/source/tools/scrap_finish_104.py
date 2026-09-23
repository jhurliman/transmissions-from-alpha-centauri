import bpy,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/scrap-104';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-103/scene.blend'));s=bpy.context.scene
cache={};changed=[]
def rgba(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)+(1,)
def grade(src):
 if src in cache:return cache[src]
 m=src.copy();m.name='104 Blue rust scrap | '+src.name;cache[src]=m
 n=m.node_tree.nodes;l=m.node_tree.links
 def noise(scale,label):
  q=n.new('ShaderNodeTexNoise');q.label=label;q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=2.8;q.inputs['Roughness'].default_value=.72;l.new(geom.outputs['Position'],q.inputs[0]);return q.outputs['Fac']
 def ramp(sock,lo,hi,c0,c1):
  q=n.new('ShaderNodeValToRGB');q.color_ramp.elements[0].position=lo;q.color_ramp.elements[0].color=c0;q.color_ramp.elements[1].position=hi;q.color_ramp.elements[1].color=c1;l.new(sock,q.inputs[0]);return q.outputs[0]
 def mix(f,a,b):
  q=n.new('ShaderNodeMixRGB')
  for i,v in enumerate((f,a,b)):
   if isinstance(v,tuple):q.inputs[i].default_value=v
   elif isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 geom=n.new('ShaderNodeNewGeometry');paint=n.get('077 rust bodies cool cavities');rim='rim' in src.name.lower()
 if paint:
  dif=n.new('ShaderNodeBsdfDiffuse');dif.label='104 actual lighting drives warm and cool';dif.inputs['Color'].default_value=(.65,.65,.65,1)
  sr=n.new('ShaderNodeShaderToRGB');l.new(dif.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0])
  palette=n.new('ShaderNodeValToRGB');palette.label='104 steel blue shade to warm rust light';palette.color_ramp.interpolation='EASE'
  for i,(pos,col) in enumerate([(0,'1b1b27'),(.22,'222435'),(.40,'343950'),(.55,'515168'),(.73,'977065'),(1.0,'b18a76')]):
   e=palette.color_ramp.elements[i] if i<2 else palette.color_ramp.elements.new(pos);e.position=pos;e.color=rgba(col)
  l.new(bw.outputs[0],palette.inputs[0]);body=palette.outputs[0]
  # Small pits vary the surface, never determine broad warm/cool coverage.
  grit=noise(65,'104 fine corrosion pits');pit=ramp(grit,.59,.69,(0,0,0,1),(.58,.58,.58,1));body=mix(pit,body,rgba('272631'))
  chips=ramp(noise(24,'104 scattered small surface chips'),.62,.71,(0,0,0,1),(.38,.38,.38,1));body=mix(chips,body,rgba('323142'))
  fleck=ramp(grit,.27,.35,(.16,.16,.16,1),(0,0,0,1));body=mix(fleck,body,rgba('997565'))
  stain=ramp(noise(13,'104 subtle grime within lit and shaded planes'),.50,.63,(0,0,0,1),(.38,.38,.38,1));tonal=n.new('ShaderNodeMixRGB');tonal.blend_type='MULTIPLY';tonal.inputs[0].default_value=1;tonal.inputs[2].default_value=(.53,.53,.53,1);l.new(body,tonal.inputs[1]);body=mix(stain,body,tonal.outputs[0])
  cap=n.get('077 reserve bright values for specular strips')
  if cap:l.new(body,cap.inputs[0]);cap.inputs[1].default_value=(.42,.30,.32)
  else:
   for link in list(paint.outputs[0].links):l.new(body,link.to_socket)
 for q in list(n):
  if q.label=='078 long worn interruptions':q.inputs['Scale'].default_value=9;q.inputs['Detail'].default_value=3;q.inputs['Roughness'].default_value=.78
  if q.type=='BSDF_GLOSSY':
   bump=n.new('ShaderNodeBump');bump.label='104 worn reflective surface';bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.018;l.new(noise(18,'104 shallow pitting'),bump.inputs['Height']);l.new(bump.outputs[0],q.inputs['Normal']);q.inputs['Roughness'].default_value=.26 if rim else .31
 # Corrosion interrupts the entire painted edge, including its diffuse base.
 out=next(q for q in n if q.type=='OUTPUT_MATERIAL' and q.is_active_output);em=out.inputs[0].links[0].from_node
 if rim and em.type=='EMISSION':
  old=em.inputs[0].links[0].from_socket;wear=ramp(noise(13,'104 edge corrosion interruptions'),.50,.64,(0,0,0,1),(.85,.85,.85,1));l.new(mix(wear,old,rgba('3a3b4d')),em.inputs[0])
 return m
for ob in bpy.data.collections['075 Scrap integration'].all_objects:
 if ob.type!='MESH' or ob.get('zone')!='near':continue
 ob.data=ob.data.copy()
 for i,m in enumerate(ob.data.materials):
  if m:ob.data.materials[i]=grade(m)
 changed.append(ob.name)
(O/'changes.json').write_text(json.dumps({'objects':changed,'materials':[m.name for m in cache.values()],'scope':'near scrap material slots only','geometry':'unchanged'},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if os.environ.get('SCRAP_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=0;s.render.border_max_x=1;s.render.border_min_y=0;s.render.border_max_y=.23;s.render.filepath=str(O/'preview.png')
bpy.ops.render.render(write_still=True)
