"""Finite bolt/seam-origin oxide fields; private133 Y/ledge materials only."""
import bpy,random,time,hashlib,array
from mathutils import Vector

def apply(scene):
 start=time.time();host=scene.objects['Architecture | gangway_single_Y_8m'];C=host.instance_collection
 if C.get('137 rust'):raise RuntimeError('Already applied')
 rng=random.Random(137);anchors=[]
 def center(o):return host.matrix_world@o.matrix_world@(sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices))
 for o in C.objects:
  if o.name.startswith('Splice bolt'):
   p=center(o);anchors.append({'source':o.name,'point':list(p),'width':rng.uniform(.025,.052),'length':rng.uniform(.42,1.25),'radius':rng.uniform(.12,.145)})
  elif o.name.startswith('Deck cross joist web'):
   p=center(o);p.x=-6.12;p.z=4.73;anchors.append({'source':o.name+' / fascia joint','point':list(p),'width':rng.uniform(.018,.046),'length':rng.uniform(.2,.65),'radius':.045})
  elif o.name.startswith('Y arm front flange'):
   pts=[host.matrix_world@o.matrix_world@v.co for v in o.data.vertices];lo=min(v.z for v in pts);hi=max(v.z for v in pts);bottom=sum((v for v in pts if v.z<lo+.025),Vector())/sum(v.z<lo+.025 for v in pts);top=sum((v for v in pts if v.z>hi-.025),Vector())/sum(v.z>hi-.025 for v in pts);axis=(top-bottom).normalized()
   for t in [.16,.51,.86]:
    p=bottom.lerp(top,t+rng.uniform(-.03,.03));p.x=max(v.x for v in pts)-.012;anchors.append({'source':o.name+' actual flange seam','point':list(p),'kind':'seam','ty':axis.y,'tz':axis.z,'extent':rng.uniform(.26,.55),'radius':rng.uniform(.026,.044),'width':.03,'length':.3})
 mats={};rows=[]
 for o in C.objects:
  for slot in o.material_slots:
   old=slot.material
   if not old:continue
   category='bolt' if any(t in o.name for t in ['Splice','splice']) else 'trail' if any(t in o.name for t in ['stem','Foot']) else 'bearing' if 'Y arm' in o.name else 'ledge'
   key=(old.name,category)
   if key not in mats:
    m=old.copy();m.name='137 '+category+' oxide | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
    oldmix=next((q for q in n if q.label=='133 Rust over retained existing paint/light response'),None)
    if not oldmix:raise RuntimeError('Expected133 oxide input '+old.name)
    base=oldmix.inputs[1].links[0].from_socket;em=next(q for q in n if q.type=='EMISSION')
    def math(op,a,b=None):
     q=n.new('ShaderNodeMath');q.operation=op
     for i,v in enumerate([a,b] if b is not None else[a]):
      if hasattr(v,'node'):l.new(v,q.inputs[i])
      else:q.inputs[i].default_value=v
     return q.outputs[0]
    geo=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],xyz.inputs[0]);X,Y,Z=xyz.outputs
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18.;noise.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],noise.inputs['Vector']);edge=math('MULTIPLY',math('SUBTRACT',noise.outputs['Fac'],.5),.9)
    field=None
    for a in anchors:
     if category in ('bolt','trail') and not a['source'].startswith('Splice bolt'):continue
     if category=='bearing' and a.get('kind')!='seam':continue
     if category=='ledge' and '/ fascia joint' not in a['source']:continue
     x,y,z=a['point'];signedy=math('SUBTRACT',Y,y);dz=math('SUBTRACT',z,Z);dx=math('ABSOLUTE',math('SUBTRACT',X,x));gate=math('LESS_THAN',dx,.48)
     if a.get('kind')=='seam':
      vertical=math('MULTIPLY',dz,-1);longitudinal=math('ADD',math('MULTIPLY',signedy,a['ty']),math('MULTIPLY',vertical,a['tz']));across=math('ADD',math('MULTIPLY',signedy,-a['tz']),math('MULTIPLY',vertical,a['ty']));gate=math('LESS_THAN',math('ABSOLUTE',across),.085);d=math('SQRT',math('ADD',math('POWER',math('DIVIDE',math('ABSOLUTE',longitudinal),a['extent']),2),math('POWER',math('DIVIDE',dx,a['radius']),2)));f=math('SUBTRACT',1.05,math('MULTIPLY',math('MAXIMUM',0,math('SUBTRACT',d,.38)),1.6))
     else:
      dy=math('ABSOLUTE',signedy);cy=math('DIVIDE',dy,a['radius']);cz=math('DIVIDE',math('ABSOLUTE',dz),a['radius']);d=math('SQRT',math('ADD',math('MULTIPLY',cy,cy),math('MULTIPLY',cz,cz)));core=math('SUBTRACT',1.06,math('MULTIPLY',math('MAXIMUM',0,math('SUBTRACT',d,.62)),2.1))
      drift=math('MULTIPLY',math('SUBTRACT',noise.outputs['Fac'],.5),.035);dytrail=math('ABSOLUTE',math('ADD',signedy,drift));taper=math('MAXIMUM',.18,math('SUBTRACT',1,math('DIVIDE',dz,a['length'])));width=math('MULTIPLY',taper,a['width']);cross=math('DIVIDE',dytrail,width);along=math('DIVIDE',dz,a['length']);streak=math('MULTIPLY',math('SUBTRACT',.9,math('MAXIMUM',cross,along)),math('GREATER_THAN',dz,0));f=streak if category=='trail' else math('MAXIMUM',core,streak)
     f=math('MULTIPLY',f,gate);field=f if field is None else math('MAXIMUM',field,f)
    finite=math('GREATER_THAN',field,.015);field=math('MULTIPLY',math('ADD',field,edge),finite);mask=n.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.02;mask.inputs['From Max'].default_value=.15;l.new(field,mask.inputs[0])
    col=n.new('ShaderNodeValToRGB');col.label='137 Ochre rim / sienna / burnt oxide / maroon core';r=col.color_ramp;r.interpolation='CONSTANT';r.elements.remove(r.elements[1]);r.elements[0].position=0;r.elements[0].color=(.14,.055,.022,1)
    for p,c in [(.24,(.125,.036,.018,1)),(.48,(.115,.026,.016,1)),(.73,(.034,.008,.012,1)),(.95,(.017,.005,.009,1))]:r.elements.new(p).color=c
    pigment=math('MAXIMUM',math('MULTIPLY',noise.outputs['Fac'],.90),math('GREATER_THAN',field,.67));l.new(pigment,col.inputs[0]);df=n.new('ShaderNodeBsdfDiffuse');df.inputs[0].default_value=(.7,.7,.7,1);rgb=n.new('ShaderNodeShaderToRGB');l.new(df.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0]);light=n.new('ShaderNodeMapRange');light.clamp=True;light.inputs['From Max'].default_value=.9;light.inputs['To Min'].default_value=.4;light.inputs['To Max'].default_value=1.1;l.new(bw.outputs[0],light.inputs[0]);lit=n.new('ShaderNodeMixRGB');lit.blend_type='MULTIPLY';lit.inputs[0].default_value=1;l.new(col.outputs[0],lit.inputs[1]);l.new(light.outputs[0],lit.inputs[2]);mix=n.new('ShaderNodeMixRGB');mix.label='137 Finite fastener corrosion over retained steel';l.new(mask.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(lit.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color']);m['137 material']='finite bolt and structural-seam fields; noise edge breakup only';mats[key]=m
   slot.link='OBJECT';slot.material=mats[key];rows.append(o.name)
 C['137 rust']=True
 return {'anchors':anchors,'changed_objects':sorted(set(rows)),'materials':[m.name for m in mats.values()],'geometry_changed':False,'normals_changed':False,'lighting_changed':False,'seconds':time.time()-start,'references':['UCL-01','UP-03','DP-08']}
