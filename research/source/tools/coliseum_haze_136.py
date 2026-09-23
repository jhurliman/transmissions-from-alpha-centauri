"""Native depth-local orange atmospheric radiance studies; no image overlays."""
import bpy,json,time,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]; O=R/'art/studies/coliseum-136/haze'
VARIANTS={'E':{'scatter':.25,'radiance':1.0,'height':29,'rear_cut':[205,225]},'D':{'scatter':.25,'radiance':1.0,'height':29},'A':{'scatter':.65,'radiance':.8,'height':24},'B':{'scatter':.55,'radiance':1.5,'height':27},'C':{'scatter':.4,'radiance':2.3,'height':30}}
def apply(scene,variant='E'):
 p=VARIANTS[variant];o=scene.objects['Distant dust volume - real lighting'];m=o.active_material.copy();m.name='136 Orange depth atmosphere '+variant;o.active_material=m;n=m.node_tree.nodes;l=m.node_tree.links;scatter=n.get('Volume Scatter');field=scatter.inputs['Density'].links[0].from_socket
 def mul(a,b,name):
  q=n.new('ShaderNodeMath');q.operation='MULTIPLY';q.name=name
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(sock,lo,hi,a,b,name):
  q=n.new('ShaderNodeMapRange');q.name=name;q.interpolation_type='SMOOTHERSTEP';q.clamp=True
  for k,v in [('From Min',lo),('From Max',hi),('To Min',a),('To Max',b)]:q.inputs[k].default_value=v
  l.new(sock,q.inputs['Value']);return q.outputs[0]
 l.new(mul(field,p['scatter'],'136 Reduced neutral scatter'),scatter.inputs['Density'])
 scatter.inputs['Color'].default_value=(.78,.27,.09,1)
 xyz=n.get('Separate XYZ');dep=ramp(xyz.outputs['Y'],48,205,0,1,'136 Orange source depth');ht=ramp(xyz.outputs['Z'],2,p['height'],1,0,'136 Orange source height')
 if p.get('rear_cut'):
  dep=mul(dep,ramp(xyz.outputs['Y'],*p['rear_cut'],1,0,'136 Rear source cutoff'),'136 Finite source depth')
 power=mul(mul(dep,ht,'136 Spatial source'),.004*p['radiance'],'136 Radiance per metre')
 em=n.new('ShaderNodeEmission');em.name='136 Orange atmospheric radiance';em.inputs['Color'].default_value=(1,.18,.045,1);l.new(power,em.inputs['Strength']);add=n.new('ShaderNodeAddShader');l.new(scatter.outputs[0],add.inputs[0]);l.new(em.outputs[0],add.inputs[1]);l.new(add.outputs[0],n.get('Material Output').inputs['Volume'])
 return dict(p,variant=variant,depth=[48,205],source_rgb_linear=[1,.18,.045],source_scale=.004,geometry_unchanged=True)
if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:];kind=args[0];O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));s=bpy.context.scene;a=apply(s,kind) if kind!='baseline' else {};s.render.resolution_x=1440;s.render.resolution_y=1082;s.render.resolution_percentage=100;s.render.use_border=False;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.filepath=str(O/(kind+'.png'));t=time.time();bpy.ops.render.render(write_still=True);a['seconds']=time.time()-t;(O/(kind+'.json')).write_text(json.dumps(a,indent=2))
