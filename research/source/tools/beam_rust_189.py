"""Edge-fed corrosion for the complete Y support family. Native editable nodes only.
Apply to a fresh188 scene, before independent189 bolt/plate pass. No render.
"""
import bpy
import numpy as np
from mathutils import Vector
HOSTS=('Architecture | gangway_single_Y_8m','Architecture | gangway_single_Y_8m.001')
def apply(scene):
 rows=[]
 for hn in HOSTS:
  host=scene.objects[hn]
  for ob in host.instance_collection.all_objects:
   if not ob.name.startswith(('Y arm','Y stem')):continue
   points=np.array([list(host.matrix_world@ob.matrix_world@v.co) for v in ob.data.vertices]);center=points.mean(0)
   values,axes=np.linalg.eigh(np.cov((points-center).T));width_axis=axes[:,np.argsort(values)[-2]];width=np.max(np.abs((points-center)@width_axis))
   for slot in ob.material_slots:
    old=slot.material
    if old.get('189 beam rust'):raise RuntimeError('189 beam rust already applied')
    m=old.copy();m.name='189 Edge-fed oxide | '+ob.name;n=m.node_tree.nodes;l=m.node_tree.links
    em=next(q for q in n if q.type=='EMISSION')
    old133=next((q for q in n if q.label=='133 Rust over retained existing paint/light response'),None)
    base=old133.inputs[1].links[0].from_socket if old133 else em.inputs['Color'].links[0].from_socket
    def node(kind,label):
     q=n.new(kind);q.label='189 '+label;return q
    def math(op,a,b=None):
     q=node('ShaderNodeMath',op);q.operation=op
     for i,v in enumerate([a] if b is None else [a,b]):
      if hasattr(v,'node'):l.new(v,q.inputs[i])
      else:q.inputs[i].default_value=v
     return q.outputs[0]
    def ramp(v,lo,hi):
     q=node('ShaderNodeMapRange','Continuous transition');q.clamp=True;q.inputs['From Min'].default_value=lo;q.inputs['From Max'].default_value=hi;l.new(v,q.inputs[0]);return q.outputs[0]
    geo=node('ShaderNodeNewGeometry','Shared world corrosion field');p=geo.outputs['Position']
    def noise(v,scale,detail=3):
     q=node('ShaderNodeTexNoise','Multiscale oxide');q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.74;l.new(v,q.inputs['Vector']);return q.outputs['Fac']
    sub=node('ShaderNodeVectorMath','Position relative to member');sub.operation='SUBTRACT';l.new(p,sub.inputs[0]);sub.inputs[1].default_value=tuple(center)
    dot=node('ShaderNodeVectorMath','Across structural member');dot.operation='DOT_PRODUCT';l.new(sub.outputs[0],dot.inputs[0]);dot.inputs[1].default_value=tuple(width_axis)
    edge=math('SUBTRACT',width,math('ABSOLUTE',dot.outputs['Value']))
    broad=noise(p,3.4);grain=noise(p,73,2);mid=noise(p,22,3)
    # Broad interruptions differ across opposite edges but remain connected to them.
    wetvec=node('ShaderNodeVectorMath','Unequal edge wetting runs');wetvec.operation='MULTIPLY';l.new(p,wetvec.inputs[0]);wetvec.inputs[1].default_value=(8.1,6.7,1.35)
    wet=noise(wetvec.outputs[0],1.0,1.5)
    active=ramp(wet,.455,.53)
    xyz=node('ShaderNodeSeparateXYZ','Structural rain receiver height');l.new(p,xyz.inputs[0]);z=xyz.outputs['Z']
    top=ramp(z,4.1,4.60)
    splice=math('MULTIPLY',ramp(z,1.20,1.65),math('SUBTRACT',1,ramp(z,1.9,2.25)))
    receiver=math('MULTIPLY',math('MAXIMUM',top,splice),ramp(broad,.43,.64))
    active=math('MAXIMUM',active,receiver)
    reach=math('ADD',.002,math('MULTIPLY',ramp(wet,.39,.67),.095))
    reach=math('ADD',reach,math('MULTIPLY',receiver,.035))
    ragged=math('MULTIPLY',math('SUBTRACT',mid,.5),.021)
    edge_mask=math('MULTIPLY',ramp(math('SUBTRACT',math('ADD',reach,ragged),edge),-.009,.014),active)
    stretched=node('ShaderNodeVectorMath','Gravity-stretched runnels');stretched.operation='MULTIPLY';l.new(p,stretched.inputs[0]);stretched.inputs[1].default_value=(31,31,1.8)
    runs=noise(stretched.outputs[0],1.0,2)
    runmask=math('MULTIPLY',ramp(runs,.57,.70),ramp(broad,.39,.60))
    coverage=math('MAXIMUM',math('MULTIPLY',edge_mask,.88),math('MULTIPLY',runmask,.67))
    # Fine isolated oxide pores interrupt the interior without broad uniform noise.
    pits=math('MULTIPLY',ramp(grain,.65,.73),ramp(mid,.47,.61))
    coverage=math('MAXIMUM',coverage,math('MULTIPLY',pits,.80))
    pigment=node('ShaderNodeValToRGB','Continuous oxide: dark roots, sienna, ochre flecks');r=pigment.color_ramp;r.interpolation='LINEAR';r.elements.remove(r.elements[1]);r.elements[0].position=.15;r.elements[0].color=(.029,.009,.006,1)
    for pos,c in [(.38,(.077,.021,.010,1)),(.55,(.15,.047,.017,1)),(.71,(.24,.094,.034,1)),(.87,(.30,.143,.061,1))]:r.elements.new(pos).color=c
    tonal=math('ADD',math('MULTIPLY',mid,.30),math('MULTIPLY',grain,.70));l.new(tonal,pigment.inputs[0])
    df=node('ShaderNodeBsdfDiffuse','Actual light on oxide');df.inputs[0].default_value=(.7,.7,.7,1);rgb=node('ShaderNodeShaderToRGB','Native light');l.new(df.outputs[0],rgb.inputs[0]);bw=node('ShaderNodeRGBToBW','Light value');l.new(rgb.outputs[0],bw.inputs[0]);light=node('ShaderNodeMapRange','Bounded oxide light response');light.clamp=True;light.inputs['From Max'].default_value=.9;light.inputs['To Min'].default_value=.48;light.inputs['To Max'].default_value=1.2;l.new(bw.outputs[0],light.inputs[0])
    lit=node('ShaderNodeMixRGB','Lit granular oxide');lit.blend_type='MULTIPLY';lit.inputs[0].default_value=1;l.new(pigment.outputs[0],lit.inputs[1]);l.new(light.outputs[0],lit.inputs[2])
    mix=node('ShaderNodeMixRGB','Edge-fed oxide over accepted steel');l.new(coverage,mix.inputs[0]);l.new(base,mix.inputs[1]);l.new(lit.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs['Color'])
    m['189 beam rust']=True;m['189 references']='RS-01 RS-02 RS-03';slot.link='OBJECT';slot.material=m
    rows.append({'host':hn,'object':ob.name,'old_material':old.name,'new_material':m.name,'width_axis':list(width_axis),'half_width':float(width),'replaced_old_corrosion':bool(old133)})
 return {'changed_slots':rows,'object_count':len(rows),'geometry_unchanged':True,'normals_unchanged':True,'references':['RS-01','RS-02','RS-03'],'scope':'Both complete Y supports; no bolts, plates, ledge or wall changes','coverage':'Procedural edge-biased; not fixed percentage. Evaluate full-render appearance.'}
