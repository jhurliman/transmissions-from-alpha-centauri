import bpy,json,collections
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/material';bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'));s=bpy.context.scene;ob=bpy.data.objects['COL120 bay8 arcade2 dentil05'];m=ob.material_slots[0].material;n,l=m.node_tree.nodes,m.node_tree.links
reachable={}
for q in n:
 if q.type=='TEX_NOISE'and q.label in ['Fine stone pits and dry pigment','Connected worn pigment islands']:
  seen=set();todo=[q]
  while todo:
   v=todo.pop()
   if v.name in seen:continue
   seen.add(v.name);todo.extend(link.to_node for out in v.outputs for link in out.links)
  reachable[q.label]=[x.name for x in n if x.type=='EMISSION'and x.name in seen]
gate=next(q for q in n if q.type=='MATH'and q.label=='153 finite pigment gate'and q.operation=='MULTIPLY'and q.inputs[1].is_linked and q.inputs[1].links[0].from_node.type=='MATH'and q.inputs[1].links[0].from_node.operation=='MAXIMUM')
# Temporary diagnostic only: emission represents actual shader field coverage.
em=n.new('ShaderNodeEmission');l.new(gate.outputs[0],em.inputs['Color']);output=next(q for q in n if q.type=='OUTPUT_MATERIAL');l.new(em.outputs[0],output.inputs['Surface']);s.render.use_compositing=False;s.render.use_freestyle=False;s.render.border_min_x=1918/3840;s.render.border_max_x=1950/3840;s.render.border_min_y=1-625/2885;s.render.border_max_y=1-585/2885;s.render.filepath=str(O/'dentil-gate-debug.png');bpy.ops.render.render(write_still=True)
for o in s.objects:
 if o.type=='MESH'and('volume'in o.name.lower()or o.hide_render):o.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;inv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation;hits=[]
for y in range(585,625):
 for x in range(1918,1950):
  q=inv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,nn,fi,obj,mat=s.ray_cast(dg,org,di)
  if ok and obj.name==ob.name:hits.append({'pixel':[x,y],'face':fi,'world_normal':list(nn),'world':list(p)})
(O/'dentil-gate-debug.json').write_text(json.dumps({'reachable_emission_nodes':reachable,'gate_node':gate.name,'faces':dict(collections.Counter(r['face']for r in hits)),'visible_hits':hits},indent=2));print('FACES',collections.Counter(r['face']for r in hits),reachable)
