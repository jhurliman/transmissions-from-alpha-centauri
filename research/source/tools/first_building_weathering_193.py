"""Moderate whole-first-left-facade finish rollout; private material-only changes.
Preserves original objects/meshes/ink membership and existing material graphs.
"""
import bpy,json,sys,hashlib,array,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/first-building-weathering-193'

def finish(base,role,severity):
 m=base.copy();m.name='193 Facade40 '+role+' '+base.name;m['193 scope']='First-left facade and rear portal jamb only';m['193 severity']=severity;m['193 revision']='v2 nondegenerate XYZ weather fields'
 n=m.node_tree.nodes;l=m.node_tree.links;em=next((q for q in n if q.type=='EMISSION'),None)
 if em is None or not em.inputs[0].is_linked:raise RuntimeError('No existing painted-light signal in '+base.name)
 original=em.inputs[0].links[0].from_socket
 def node(t,label):q=n.new(t);q.label='193 '+label;return q
 def math(op,*values):
  q=node('ShaderNodeMath',op);q.operation=op
  for i,v in enumerate(values):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def mix(f,a,b,label,op='MIX'):
  q=node('ShaderNodeMixRGB',label);q.blend_type=op
  for i,v in enumerate([f,a,b]):
   if isinstance(v,(tuple,list)):q.inputs[i].default_value=v
   elif isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def remap(x,lo,hi,a=0,b=1,label='remap'):
  q=node('ShaderNodeMapRange',label);q.clamp=True;q.interpolation_type='SMOOTHSTEP';l.new(x,q.inputs[0]);q.inputs[1].default_value=lo;q.inputs[2].default_value=hi;q.inputs[3].default_value=a;q.inputs[4].default_value=b;return q.outputs[0]
 def vector(x,y,z):
  q=node('ShaderNodeCombineXYZ','gravity-oriented coordinates')
  for i,v in enumerate([x,y,z]):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def noise(position,scale,detail=2):
  q=node('ShaderNodeTexNoise','nonperiodic susceptibility');l.new(position,q.inputs['Vector']);q.inputs['Scale'].default_value=scale;q.inputs['Detail'].default_value=detail;q.inputs['Roughness'].default_value=.68;return q.outputs['Fac']
 geo=node('ShaderNodeNewGeometry','world-continuous weather field');sep=node('ShaderNodeSeparateXYZ','world position');l.new(geo.outputs['Position'],sep.inputs[0]);wx,wy,up=sep.outputs['X'],sep.outputs['Y'],sep.outputs['Z']
 tex=node('ShaderNodeTexCoord','panel bounds');local=node('ShaderNodeSeparateXYZ','panel-edge and base weights');l.new(tex.outputs['Generated'],local.inputs[0]);gx,gz=local.outputs['X'],local.outputs['Z']
 edge=math('MINIMUM',math('MINIMUM',gx,math('SUBTRACT',1,gx)),math('MINIMUM',gz,math('SUBTRACT',1,gz)));edges=remap(edge,.015,.20,1,0,'interrupted panel edges');bottom=remap(gz,.03,.43,1,0,'panel-base weighting')
 # All three world dimensions participate: projecting only Y/Z collapsed constant-Y
 # facade faces and the portal post into horizontal bands. No noise cover-up layer.
 position=geo.outputs['Position']
 # Broad connected susceptibility remains quiet; details break it up near real panel edges/bases.
 broad=noise(vector(math('MULTIPLY',wx,.37),math('MULTIPLY',wy,.37),math('MULTIPLY',up,.22)),1,2.4)
 broad=remap(broad,.30,.70,0,1,'multi-panel susceptibility')
 fine=noise(position,17,3);fray=noise(position,55,2);field=math('ADD',math('MULTIPLY',fine,.77),math('MULTIPLY',fray,.23))
 chip=remap(field,.505,.625,0,1,'fine broken coating fringe')
 support=math('MAXIMUM',math('MULTIPLY',edges,.90),math('MAXIMUM',math('MULTIPLY',bottom,.76),math('MULTIPLY',broad,.28)))
 chip=math('MULTIPLY',chip,support)
 # Ragged medium-size islands connect fine flecks; no uniform full-face noise blanket.
 medium=noise(vector(math('MULTIPLY',wx,1.15),math('MULTIPLY',wy,1.15),math('MULTIPLY',up,.80)),5.4,2.7)
 islands=remap(medium,.51,.68,0,1,'medium broken finish islands')
 weather=math('MAXIMUM',math('MULTIPLY',chip,.9),math('MULTIPLY',math('MULTIPLY',islands,support),.74))
 # Nonperiodic thin rain paths start broadly near panel tops and narrow/fade downwards.
 rain=noise(vector(math('MULTIPLY',wx,15),math('MULTIPLY',wy,15),math('MULTIPLY',up,.24)),1,1.7)
 threshold=math('ADD',.55,math('MULTIPLY',math('SUBTRACT',1,gz),.13))
 rain=remap(math('SUBTRACT',rain,threshold),0,.105,0,1,'irregular rain trails')
 rain=math('MULTIPLY',rain,remap(gz,.05,.88,.06,1,'translucent tapered lower tails'))
 rain=math('MULTIPLY',rain,math('ADD',.28,math('MULTIPLY',broad,.72)))
 body=mix(math('MULTIPLY',broad,severity*.38),original,mix(1,original,(.83,.88,.94,1),'quiet coherent age','MULTIPLY'),'shared multi-panel aging')
 shadowtone=(.58,.63,.71,1)if role!='metal'else(.52,.53,.58,1)
 body=mix(math('MULTIPLY',rain,severity*1.35),body,mix(1,body,shadowtone,'damp streak tone','MULTIPLY'),'seam-led downward moisture')
 cuttone=(.59,.63,.70,1)if role!='metal'else(1.54,1.24,1.03,1)
 body=mix(math('MULTIPLY',weather,severity*1.65),body,mix(1,body,cuttone,'exposed worn finish','MULTIPLY'),'distributed coating wear')
 chalk=math('MULTIPLY',remap(field,.44,.58),math('MULTIPLY',support,remap(medium,.31,.49,1,0)))
 lighttone=(1.24,1.20,1.14,1)if role!='metal'else(1.47,1.42,1.35,1)
 body=mix(math('MULTIPLY',chalk,severity*.92),body,mix(1,body,lighttone,'chalked edge pigment','MULTIPLY'),'lighter worn fragments between dark losses')
 l.new(body,em.inputs[0]);m['193 finish']='Full XYZ continuous multi-panel field + Generated panel-base/edge weighting + world-Z rain taper; inherits current lit source color';return m

def apply(scene=None):
 s=scene or bpy.context.scene;cfg=json.loads((R/'config/first-building-weathering-193.json').read_text());host=bpy.data.objects[cfg['primary_host']];C=host.instance_collection;dg=bpy.context.evaluated_depsgraph_get();targets=[o for o in C.all_objects if o.type=='MESH'and not any(x in o.name for x in ['Deep structural core','Slot deep shadow','Access cover fastener'])]
 names={o.name for o in targets};sharing={n:set()for n in names}
 for ins in dg.object_instances:
  if ins.object.original.name in names:sharing[ins.object.original.name].add(ins.parent.original.name if ins.parent else '(direct)')
 assert all(parents<= {host.name}for parents in sharing.values()),'193 target object shared outside first facade'
 targets.append(bpy.data.objects[cfg['rear_vertical_member']]);cache={};rows=[]
 for ob in targets:
  assert not ob.get('193 facade40'),'Apply193 once to a fresh scene'
  role='metal'if ob.name==cfg['rear_vertical_member']or ob.name.startswith('Slot louver')else'facade';changed=[]
  for sl in ob.material_slots:
   base=sl.material
   if base is None or 'Recess | dark backing'in base.name:continue
   # Existing fracture ink carries its own high-contrast edge signal and remains intact.
   if any(term in base.name for term in ['Projected fracture','fracture depth']):continue
   key=(base.name,role)
   if key not in cache:cache[key]=finish(base,role,cfg['severity'])
   sl.link='OBJECT';sl.material=cache[key];changed.append({'slot':sl.slot_index,'source':base.name,'private':sl.material.name})
  if changed:ob['193 facade40']=True;rows.append({'object':ob.name,'role':role,'slots':changed})
 return {'source_family':C.name,'host':host.name,'severity':cfg['severity'],'target_objects':len(rows),'private_materials':len(cache),'assignments':rows,'sharing_verified':'Every facade member appears only under Front-left section instance; no object/collection copies or name changes required','rear_vertical_identity':cfg['rear_vertical_identity'],'old_graphs_unchanged':True,'geometry_transforms_ink_membership_render_layers_unchanged':True,'exclusions':cfg['fixed'],'revision':'v2 nondegenerate XYZ weather fields','status':'CPU material candidate; integrated native render pending','user_approved':False}

if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(R/'tools'));src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")]);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/plate-runoff-192/candidate.blend'));s=bpy.context.scene;before=fingerprint(s);oldm=material_snapshot();result=apply(s);after=fingerprint(s);newm=material_snapshot();allowed={r['object']for r in result['assignments']};changes={k:[f for f,v in before[k].items()if after[k][f]!=v]for k in before if before[k]!=after[k]};assert set(before)==set(after);assert all(k in allowed and v==['materials']for k,v in changes.items()),changes;assert all(v==newm[k]for k,v in oldm.items()),'Existing material graph changed';result['preservation']={'existing_entries':len(before),'changed_material_only_objects':changes,'existing_graph_changes':[],'geometry_normals_camera_lights_transforms_instances_unchanged':True};(O/'audit.json').write_text(json.dumps(result,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'candidate.blend'));print('193 READY',len(changes),'objects',result['private_materials'],'private materials')
