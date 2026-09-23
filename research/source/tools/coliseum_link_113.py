"""Share congruent intact additions in bay-local space, preserving world geometry."""
import bpy,math,hashlib
from mathutils import Matrix,Vector

def link_intact_additions(collection):
 anchor=next(o for o in collection.objects if o.get('bay')==4 and 'fractured upper wall L' in o.name)
 lean=Matrix.Rotation(math.radians(2),4,'X');base=Matrix.Translation(Vector((0,347,0)))@lean
 delta=anchor.matrix_world@(base@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z')).inverted()
 pool={};linked=0;max_error=0;processed=0
 for ob in list(collection.objects):
  bay=int(ob.get('bay',-1))
  if ob.type!='MESH' or not ob.name.startswith('COL111 ') or bay<0 or bay==10 or ob.get('localized_breakage'):continue
  M=delta@base@Matrix.Rotation(-math.pi+(bay+.5)*math.tau/36,4,'Z');inv=M.inverted()
  world=[ob.matrix_world@v.co for v in ob.data.vertices];coords=[inv@v for v in world]
  key=hashlib.sha256(repr((ob.get('coliseum_role'),[tuple(round(x,4) for x in v) for v in coords],[(tuple(p.vertices),p.material_index) for p in ob.data.polygons],[m.name if m else None for m in ob.data.materials])).encode()).hexdigest()
  if key in pool:
   me=pool[key];linked+=1
  else:
   me=ob.data.copy();me.name=ob.name+' reusable local mesh';me.transform(inv@ob.matrix_world);me.update();pool[key]=me
  error=max(((M@v.co)-old).length for v,old in zip(me.vertices,world)) if world else 0
  if error>.0005:raise RuntimeError(f'Canonicalization changed geometry: {ob.name} {error}')
  max_error=max(max_error,error);ob.data=me;ob.matrix_world=M;ob['kit_mesh_key']=key[:12];processed+=1
 return {'processed_intact_additions':processed,'linked_instances':linked,'unique_meshes':len(pool),'max_world_error_m':max_error,'damaged_bay10_excluded':True}
