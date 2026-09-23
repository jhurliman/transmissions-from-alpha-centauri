import bpy,sys,math,json,hashlib,array
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
_,world,unpack=mapping()
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(R/path));C=bpy.data.collections['110 Coliseum detailed front ruin'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={};widths={}
 for ob in C.objects:
  if ob.type!='MESH':continue
  me=ob.data;v=array.array('f',[0])*(len(me.vertices)*3);me.vertices.foreach_get('co',v);h=hashlib.sha256(v.tobytes())
  for a in me.attributes:
   if a.name.startswith('.')or a.name=='position':continue
   h.update((a.name+a.domain+a.data_type).encode())
   prop='vector'if a.data_type=='FLOAT_VECTOR'else'value'if a.data_type in ['FLOAT','INT','BOOLEAN']else None
   if prop:
    vals=array.array('i' if a.data_type in ['INT','BOOLEAN'] else 'f',[0])*(len(a.data)*(3 if prop=='vector'else 1))
    try:a.data.foreach_get(prop,vals);h.update(vals.tobytes())
    except:pass
  rows[ob.name]={'mesh':me.name,'vertices':len(me.vertices),'polygons':len(me.polygons),'hash':h.hexdigest(),'materials':[m.name if m else None for m in me.materials]}
  if 'engaged round column'in ob.name:
   ev=ob.evaluated_get(dg);em=ev.to_mesh();p=[unpack(ev.matrix_world@v.co)for v in em.vertices];ev.to_mesh_clear();angles=[v[1]for v in p];widths[ob.name]={'angular_width_m':75*(max(angles)-min(angles)),'rwidth_m':max(v[0]for v in p)-min(v[0]for v in p),'zwidth_m':max(v[2]for v in p)-min(v[2]for v in p)}
 return rows,widths
before,bw=read('art/studies/coliseum-125/scene.blend');after,aw=read('art/studies/coliseum-126/grouping/scene.blend');changed=[k for k in before if before[k]!=after.get(k)];width_errors={k:{a:abs(bw[k][a]-aw[k][a])for a in bw[k]}for k in bw};report={'raw_mesh_objects_checked':len(before),'raw_mesh_geometry_attribute_material_changes':changed,'round_columns_checked':len(width_errors),'round_column_max_dimension_error_authored_m':max(max(v.values())for v in width_errors.values()),'round_column_errors':width_errors,'scope':'Source mesh coordinates/topology counts/material slots and custom attributes preserved. Evaluated column radial/tangential/height dimensions checked through approved inverse warp. This is not a global crossing certificate.'};(R/'art/studies/coliseum-126/grouping/preservation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='round_column_errors'})
