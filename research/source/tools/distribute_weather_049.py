import bpy,json,random,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-049';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-048/scene.blend'));s=bpy.context.scene
source=bpy.data.node_groups['048 Chromatic seam-fed runoff']
# (horizontal coordinate at start, width scale, actual source height, vertical scale, strength, direction)
profiles={
 'left_middle':[(3.4,1.1,10.871,1.65,.54,1),(9.4,1.45,4.319,1.23,.66,1)],
 'left_rear':[(22.0,1.9,8.687,2.0,.64,1)],
 'right_front':[(-5.1,.95,5.87,1.15,.50,1),(.2,.75,12.11,1.5,.46,-1)],
 'right_middle':[(17.15,1.0,2.639,1.0,.53,-1),(9.0,1.45,10.02,1.7,.55,1)],
 'right_rear':[(29.5,1.4,6.06,1.5,.68,-1),(26.0,1.6,13.33,1.4,.51,-1)],
 'side_road':[(11.0,1.1,4.3,.7,.29,1)],
 'front_left':[(-7.3,1.0,4.319,1.15,.40,1)]}
def mathnode(nt,kind,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
records=[]
for m in list(bpy.data.materials):
 family=m.name.split(' | ')[-1] if m.name.startswith('042 Street coating | ') else 'side_road' if m.name=='043 Side-road warm mineral coating' else 'front_left' if m.name.startswith('039 Layered coating | ') else None
 if family not in profiles:continue
 nt=m.node_tree;bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not bs:continue
 base=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else None
 if base is None:
  n=nt.nodes.new('ShaderNodeRGB');n.outputs[0].default_value=bs.inputs['Base Color'].default_value;base=n.outputs[0]
 geom=nt.nodes.new('ShaderNodeNewGeometry');xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Position'],xyz.inputs[0]);norm=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Normal'],norm.inputs[0]);axis='X' if family=='side_road' else 'Y';normalaxis='Y' if family=='side_road' else 'X'
 # Shelter mask: suppress top/underside surfaces and returns facing another direction.
 facing=mathnode(nt,'GREATER_THAN',mathnode(nt,'ABSOLUTE',norm.outputs[normalaxis],0),.72)
 for i,(start,sx,height,sz,strength,direction) in enumerate(profiles[family]):
  mapping=nt.nodes.new('ShaderNodeCombineXYZ');u=mathnode(nt,'DIVIDE',mathnode(nt,'MULTIPLY',mathnode(nt,'SUBTRACT',xyz.outputs[axis],start),direction),sx)
  nt.links.new(mathnode(nt,'SUBTRACT',11.6,u),mapping.inputs['Y']);nt.links.new(mathnode(nt,'ADD',mathnode(nt,'DIVIDE',mathnode(nt,'SUBTRACT',xyz.outputs['Z'],height),sz),2.639),mapping.inputs['Z'])
  node=nt.nodes.new('ShaderNodeGroup');node.node_tree=source;node.label='049 '+family+' zone '+str(i);nt.links.new(base,node.inputs['Base']);nt.links.new(mapping.outputs[0],node.inputs['Position']);nt.links.new(mathnode(nt,'MULTIPLY',facing,strength),node.inputs['Strength']);base=node.outputs[0]
 nt.links.new(base,bs.inputs['Base Color']);records.append({'material':m.name,'family':family,'zones':profiles[family]})
# A second, lighter sheet corner uses a different orientation and location.
host=bpy.data.objects['right_vertical_galleries'];kit=host.instance_collection
panel=next(o for o in kit.objects if o.type=='MESH' and any(m and m.name=='047 Seam loss and fastener stains lower' for m in o.data.materials))
T=Matrix.Translation(Vector((-2.8,.35*(1-.45),0))) @ Matrix.Diagonal(Vector((-1,.45,1,1)))
parts=[panel]+[o for o in kit.objects if o.name.startswith('047 ') and o.location.z<1.34]
newparts={}
for old in parts:
 q=old.copy();q.data=old.data.copy() if old.data else None;q.name='049 lighter mirrored | '+old.name;kit.objects.link(q);q.matrix_basis=T @ old.matrix_basis;newparts[old]=q
 if old==panel:
  for slot in q.material_slots:
   if not slot.material:continue
   mat=slot.material.copy();mat.name='049 lighter panel coating';slot.material=mat;nt=mat.node_tree
   for n in list(nt.nodes):
    if n.type=='GROUP' and n.node_tree==source:
     origin=n.inputs['Base'].links[0].from_socket
     for link in list(n.outputs[0].links):nt.links.new(origin,link.to_socket)
     nt.nodes.remove(n)
for old,q in newparts.items():
 for mod in q.modifiers:
  if mod.type=='BOOLEAN' and mod.object in newparts:mod.object=newparts[mod.object]
target=next(o for o in kit.objects if o.type=='MESH' and o.name.startswith('Gallery base panel') and abs(min(v.co.x for v in o.data.vertices)+5.589)<.01 and abs(max(v.co.z for v in o.data.vertices)-1.339)<.01)
kit.objects.unlink(target)
bpy.context.view_layer.update();q=newparts[panel];me=bpy.data.meshes.new_from_object(q.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me);audit={'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'local_volume':bm.calc_volume(),'max_corner_lift_m':.085*.45};assert audit['non_manifold_edges']==0 and abs(audit['local_volume'])>0;bm.free()
(O/'audit.json').write_text(json.dumps({'runoff_profiles':records,'additional_panel':audit,'preserved':'Approved concrete, pipe and duct geometry/materials; quiet surfaces outside bounded regions','shelter':'Normal-direction gating excludes undersides and most perpendicular returns'},indent=2))
s.render.filepath=str(O/'render.png');s.cycles.samples=32;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
main=(s.camera.location.copy(),s.camera.rotation_euler.copy(),s.camera.data.lens)
s.render.resolution_x=1200;s.render.resolution_y=1000;s.render.use_freestyle=False
for name,loc,aim,lens in [('right-detail',(1,1,5.2),(9.5,10.7,6.5),43),('left-detail',(-1,0,5.5),(-9.5,8.2,6.3),42),('lighter-panel',(5.8,15.4,1.7),(9.85,15.8,1.2),46)]:
 s.camera.location=loc;s.camera.rotation_euler=(Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
