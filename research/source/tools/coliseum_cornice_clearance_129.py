"""Leave the dentil row clear over each actual round-column capital."""
import bpy,math
from coliseum_arch_ratio_125 import mapping

def apply(C,margin=.12):
 _,_,unpack=mapping();dg=bpy.context.evaluated_depsgraph_get();columns=[];removed=[]
 def bounds(ob,capital=False):
  ev=ob.evaluated_get(dg);me=ev.to_mesh();q=[unpack(ev.matrix_world@v.co)for v in me.vertices];ev.to_mesh_clear()
  if capital:
   top=max(p[2]for p in q);q=[p for p in q if p[2]>top-.8]
  return {'umin':min(p[1]*75 for p in q),'umax':max(p[1]*75 for p in q),'zmin':min(p[2]for p in q),'zmax':max(p[2]for p in q),'rmin':min(p[0]for p in q),'rmax':max(p[0]for p in q)}
 for ob in C.all_objects:
  if ob.type=='MESH'and 'engaged round column'in ob.name:columns.append((ob.name,bounds(ob,True)))
 for ob in list(C.all_objects):
  if ob.type!='MESH' or ob.get('feature')!='shared undercornice dentil':continue
  b=bounds(ob)
  for name,c in columns:
   near_top=b['zmin']<c['zmax']+.55 and b['zmax']>c['zmax']-.8
   horizontal_overlap=b['umin']<c['umax']+margin and b['umax']>c['umin']-margin
   radial_overlap=b['rmin']<c['rmax']+.6 and b['rmax']>c['rmin']-.6
   if near_top and horizontal_overlap and radial_overlap:
    removed.append({'object':ob.name,'column':name,'dentil_bounds':b,'capital_bounds':c});bpy.data.objects.remove(ob,do_unlink=True);break
 return {'round_columns':len(columns),'removed_count':len(removed),'capital_side_clearance_authored_m':margin,'method':'Actual evaluated capital and dentil footprints after127 layout; clear the complete capital width at its cornice level','removed':removed}
