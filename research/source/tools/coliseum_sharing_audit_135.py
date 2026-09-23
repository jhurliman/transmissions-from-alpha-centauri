"""Read-only exact mesh/material/attribute identity inventory."""
import bpy,json,hashlib,array
from pathlib import Path
from collections import defaultdict
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-135';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-134/scene.blend'));C=next(c for c in bpy.context.scene.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and not c.library)
uses=defaultdict(list)
for ob in C.all_objects:
 if ob.type=='MESH':uses[ob.data].append(ob.name)
fields={'FLOAT':('value','f',1),'INT':('value','i',1),'BOOLEAN':('value','b',1),'FLOAT_VECTOR':('vector','f',3),'FLOAT_COLOR':('color','f',4),'BYTE_COLOR':('color','f',4),'FLOAT2':('vector','f',2),'INT8':('value','b',1),'INT32_2D':('value','i',2)}
exact=defaultdict(list);shape=defaultdict(list);unknown=[]
for me,names in uses.items():
 h=hashlib.sha256()
 def add(coll,prop,typecode,width):
  v=array.array(typecode,[0])*(len(coll)*width);coll.foreach_get(prop,v);h.update(v.tobytes())
 add(me.vertices,'co','f',3);add(me.loops,'vertex_index','i',1);add(me.polygons,'loop_total','i',1);add(me.polygons,'material_index','i',1);add(me.polygons,'use_smooth','b',1);add(me.edges,'vertices','i',2);shape[h.hexdigest()].append(me.name)
 h.update(json.dumps([m.name if m else None for m in me.materials]).encode());add(me.corner_normals,'vector','f',3)
 supported=True
 for at in sorted(me.attributes,key=lambda a:a.name):
  if at.name.startswith('.select'):continue
  h.update(json.dumps([at.name,at.data_type,at.domain]).encode())
  if at.data_type not in fields:unknown.append([me.name,at.name,at.data_type]);supported=False;continue
  prop,code,w=fields[at.data_type]
  try:add(at.data,prop,code,w)
  except Exception as e:unknown.append([me.name,at.name,str(e)]);supported=False
 if supported:exact[h.hexdigest()].append(me.name)
out={'source':'134 scene','mesh_objects':sum(map(len,uses.values())),'unique_meshes':len(uses),'shared_meshes':sum(len(v)>1 for v in uses.values()),'objects_on_shared_meshes':sum(len(v)for v in uses.values()if len(v)>1),'exact_duplicate_groups':[v for v in exact.values()if len(v)>1],'same_local_shape_groups':[v for v in shape.values()if len(v)>1],'unsupported_attributes':unknown,'scope':'Raw local mesh coordinates/topology/materials/all supported rendering attributes/corner normals. Ignores only selection flags. Object transforms/modifiers not normalized; not a proof that all other geometries must be unique.'}
(O/'mesh-sharing-audit.json').write_text(json.dumps(out,indent=2));print({k:len(v)if isinstance(v,list) else v for k,v in out.items()})
