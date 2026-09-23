"""Shared source114 intact meshes with native per-instance GeometryNodes ring deformation."""
import bpy,json,math,sys,os
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-116/linked';O.mkdir(parents=True,exist_ok=True)
def source_world(ob):
 return source_world(ob.parent)@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_basis.copy()
def edge_marks(me):
 return {a.name:[getattr(d,'value',None)for d in a.data]for a in me.attributes if a.domain=='EDGE' and ('freestyle'in a.name.lower()or 'sharp'in a.name.lower())}
def group():
 g=bpy.data.node_groups.new('116 Shared intact ring warp','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 for prefix in ['Auth','Original','Final']:
  for suffix in ['0','1','2','T']:g.interface.new_socket(name=prefix+suffix,in_out='INPUT',socket_type='NodeSocketVector')
 n=g.nodes;l=g.links;i=n.new('NodeGroupInput');o=n.new('NodeGroupOutput');pos=n.new('GeometryNodeInputPosition')
 def mathn(op,a,b=None):
  q=n.new('ShaderNodeMath');q.operation=op
  for k,v in enumerate([a,b]):
   if v is None:continue
   if isinstance(v,(float,int)):q.inputs[k].default_value=v
   else:l.new(v,q.inputs[k])
  return q.outputs[0]
 def transform(v,p):
  c=n.new('ShaderNodeCombineXYZ')
  for k in range(3):
   d=n.new('ShaderNodeVectorMath');d.operation='DOT_PRODUCT';l.new(v,d.inputs[0]);l.new(i.outputs[p+str(k)],d.inputs[1]);l.new(d.outputs['Value'],c.inputs[k])
  a=n.new('ShaderNodeVectorMath');a.operation='ADD';l.new(c.outputs[0],a.inputs[0]);l.new(i.outputs[p+'T'],a.inputs[1]);return a.outputs[0]
 authored=transform(pos.outputs[0],'Auth');sep=n.new('ShaderNodeSeparateXYZ');l.new(authored,sep.inputs[0]);x,y,z=[sep.outputs[k]for k in range(3)]
 radius=mathn('SQRT',mathn('ADD',mathn('MULTIPLY',x,x),mathn('MULTIPLY',y,y)));theta=mathn('ARCTAN2',y,x);theta=mathn('SUBTRACT',theta,mathn('MULTIPLY',mathn('GREATER_THAN',theta,math.pi/2),math.tau));theta=mathn('SUBTRACT',mathn('MULTIPLY',mathn('ADD',theta,math.pi/2),.68),math.pi/2)
 outer=mathn('MULTIPLY',mathn('SUBTRACT',1,mathn('MULTIPLY',z,.055/78)),75);offset=mathn('SUBTRACT',radius,outer);radius=mathn('ADD',outer,mathn('ADD',mathn('MAXIMUM',offset,0),mathn('MULTIPLY',mathn('MINIMUM',offset,0),.55)));c=n.new('ShaderNodeCombineXYZ');l.new(mathn('MULTIPLY',radius,mathn('COSINE',theta)),c.inputs[0]);l.new(mathn('MULTIPLY',radius,mathn('SINE',theta)),c.inputs[1]);l.new(z,c.inputs[2]);final=transform(c.outputs[0],'Final')
 store=n.new('GeometryNodeStoreNamedAttribute');store.data_type='FLOAT_VECTOR';store.domain='POINT';store.inputs['Name'].default_value='115 Original world position';l.new(i.outputs['Geometry'],store.inputs['Geometry']);l.new(transform(pos.outputs[0],'Original'),store.inputs['Value']);setp=n.new('GeometryNodeSetPosition');l.new(store.outputs['Geometry'],setp.inputs['Geometry']);l.new(final,setp.inputs['Position']);l.new(setp.outputs['Geometry'],o.inputs['Geometry']);return g
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];targets={o.name:o for o in C.objects if o.type=='MESH'}
with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):
 requested=[name for name in src.objects if name in targets and (os.environ.get('LINK_ALL')=='1' or (targets[name].get('bay') in [4,5,6] and targets[name].get('coliseum_role') in ['arch_molding','pier','band','detail']) or (targets[name].get('bay')==4 and 'fractured upper wall L' in name))];dst.objects=list(requested)
source_by_target=dict(zip(requested,dst.objects))
anchor=next(o for name,o in source_by_target.items()if targets[name].get('bay')==4 and 'fractured upper wall L'in name);lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=source_world(anchor)@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean
A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);warpgroup=group();identifiers={s.name:s.identifier for s in warpgroup.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'}
# Share only identical original datablocks; damaged meshes and topology-cleaned shapes are not included.
groups={}
for name,src in source_by_target.items():
 target=targets[name]
 if target.get('coliseum_role')not in ['arch_molding','pier','band','detail']:continue
 if len(src.data.vertices)!=len(target.data.vertices)or len(src.data.polygons)!=len(target.data.polygons):continue
 key=(src.data.as_pointer(),tuple(m.name if m else''for m in target.data.materials));groups.setdefault(key,[]).append((target,src))
eligible=[g for g in groups.values()if len(g)>1];proof_only=os.environ.get('LINK_ALL')!='1';chosen=eligible[:3]if proof_only else eligible;records=[];pending=[];deps=bpy.context.evaluated_depsgraph_get()
for members in chosen:
 shared=members[0][1].data;shared.materials.clear()
 for m in members[0][0].data.materials:shared.materials.append(m)
 for target,src in members:
  prior=target.data;expected=[v.co.copy()for v in prior.vertices];attr=prior.attributes.get('115 Original world position');expected_attr=[d.vector.copy()for d in attr.data]if attr else None;indices=[p.material_index for p in prior.polygons];smooth=[p.use_smooth for p in prior.polygons];marks=edge_marks(prior);target.data=shared;mod=target.modifiers.new('116 Instance-specific ring warp','NODES');mod.node_group=warpgroup
  matrices={'Auth':P.inverted()@source_world(src),'Original':source_world(src),'Final':target.matrix_world.inverted()@yaw@A@P}
  for prefix,M in matrices.items():
   for k in range(3):getattr(mod.properties.inputs,identifiers[prefix+str(k)]).value=tuple(M[k][j]for j in range(3))
   getattr(mod.properties.inputs,identifiers[prefix+'T']).value=tuple(M.translation)
  target.update_tag();pending.append((target,prior,mod,expected,expected_attr,indices,smooth,marks))
bpy.context.view_layer.update()
for target,prior,mod,expected,expected_attr,indices,smooth,marks in pending:
 ev=target.evaluated_get(deps);me=ev.to_mesh();err=max((v.co-p).length for v,p in zip(me.vertices,expected));at=me.attributes.get('115 Original world position');err_attr=max((d.vector-p).length for d,p in zip(at.data,expected_attr))if at and expected_attr else None;match=indices==[p.material_index for p in me.polygons];smooth_match=smooth==[p.use_smooth for p in me.polygons];marks_match=marks==edge_marks(me);ev.to_mesh_clear();accepted=smooth_match and marks_match and err<.003 and err_attr is not None and err_attr<.003 and match
 records.append({'object':target.name,'local_vertex_max_error_m':err,'original_position_max_error_m':err_attr,'material_indices_match':match,'smooth_flags_match':smooth_match,'freestyle_marks_match':marks_match,'accepted':accepted})
 if not accepted:target.modifiers.remove(mod);target.data=prior
accepted=sum(r['accepted']for r in records);audit={'eligible_shared_groups':len(eligible),'eligible_instances':sum(map(len,eligible)),'tested_instances':len(records),'accepted':accepted,'records':records};(O/('audit-proof.json'if proof_only else'audit-all.json')).write_text(json.dumps(audit,indent=2));print(json.dumps(audit))
# Appended originals remain unlinked library data; remove their objects while used shared meshes survive.
bpy.data.batch_remove(ids=[o for o in dst.objects if o]);bpy.ops.wm.save_as_mainfile(filepath=str(O/('proof.blend'if proof_only else'scene.blend')))
