"""Correct235 construction courses to actual outer face, replacing isolated mini ledges."""
import bpy,json,sys,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ruined-wall-structure-235';sys.path.insert(0,str(R/'tools'))

def apply(scene):
 from ruined_wall_structure_235 import ledge
 from city_transition_refinement_200 import _cut,_closed
 def safe_cut(ob,c,n,profile,depth,label,core):
  original=ob.data.copy();attempts=[]
  for dz,dn in [(0,0),(.007,.003),(-.009,.004),(.016,.006)]:
   ob.data=original.copy();q=Vector(c)+Vector((0,0,dz))+Vector(n)*dn
   row=_cut(ob,q,n,profile,depth+dn,label,core);health=_closed(ob);attempts.append(health)
   if health['nonmanifold_edges']==0:
    row['boolean_robustness_attempts']=len(attempts);return row
  ob.data=original
  raise RuntimeError((ob.name,label,attempts))
 audit=json.loads((O/'audit.json').read_text());rows=[];removed=[];additions=[]
 for ob in list(bpy.data.collections['133 Ruined transition structures'].objects):
  if ob.name.startswith('235 Interrupted slab remnant'):
   ob.hide_render=True;ob.hide_viewport=True;removed.append(ob.name)
 for idx,row in enumerate(audit['rows']):
  ob=bpy.data.objects[row['object']];n=Vector(row['major_face_normal']);u=n.cross(Vector((0,0,1))).normalized();pts=[ob.matrix_world@v.co for v in ob.data.vertices];outer=max(v.dot(n)for v in pts);lo=min(v.dot(u)for v in pts);hi=max(v.dot(u)for v in pts)
  core=next(sl.material for sl in ob.material_slots if sl.material and sl.material.get('235 wall role')=='core');lip=next(sl.material for sl in ob.material_slots if sl.material and sl.material.get('235 wall role')=='lip')
  oldplanes=[{'label':f['label'],'offset_below_outer_plane_m':outer-Vector(f['center']).dot(n)}for f in row['construction_joints']]
  levels=sorted(set(round(f['center'][2],5)for f in row['construction_joints']if 'horizontal'in f['label']));features=[]
  ob.data=ob.data.copy()
  for j,z in enumerate(levels):
   c=n*outer+u*((lo+hi)/2)+Vector((0,0,z));width=hi-lo+.12
   features.append(safe_cut(ob,c,n,[(-width/2,-.026),(width/2,-.026),(width/2,.026),(-width/2,.026)],.034,'235 V2 true outer face construction course',core))
   # An offset panel seam between surviving horizontal courses, with no fine repeated pattern.
   if j<len(levels)-1:
    h=levels[j+1]-z;column=lo+(hi-lo)*(.36 if (j+idx)%2 else .67);cc=n*outer+u*column+Vector((0,0,z+h/2))
    features.append(safe_cut(ob,cc,n,[(-.022,-h/2),(.022,-h/2),(.022,h/2),(-.022,h/2)],.028,'235 V2 connected panel tie joint',core))
  if ob.name in ('133 L2 broken camera-facing cross wall','133 R4 broken camera-facing cross wall') and levels:
   z=levels[min(1,len(levels)-1)]+.10;width=(hi-lo)*.90;center_u=lo+width*.5-.025;c=n*outer+u*center_u+Vector((0,0,z))
   new=ledge(scene,ob,c,n,u,width,.205,lip,100+idx);new.name='235 Edge-connected floor layer '+ob.name;new['235 course revision']=2;health=_closed(new);assert health['nonmanifold_edges']==0 and len(new.data.polygons)>0;additions.append({'object':new.name,'host':ob.name,'length_m':width,'height_m':.205,'host_edge_connected':True,'health':health})
  health=_closed(ob);assert health['nonmanifold_edges']==0,(ob.name,health);rows.append({'object':ob.name,'old_joint_plane_diagnosis':oldplanes,'outer_plane':outer,'new_courses':features,'health':health})
 return {'study':'235 V2 course repair','source':'235 structureV1','hidden_isolated_ledge_islands':removed,'rows':rows,'new_edge_connected_floor_layers':additions,'all_other_geometry_materials_unchanged':True,'status':'Native proof required; no render launched'}

if __name__=='__main__':
 src=O/'scene.blend';held=O/'held-v1';held.mkdir(exist_ok=True)
 for fn in ['scene.blend','audit.json']:
  if not(held/fn).exists():shutil.copy2(O/fn,held/fn)
 bpy.ops.wm.open_mainfile(filepath=str(held/'scene.blend'));a=apply(bpy.context.scene);(O/'course-v2-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene-v2.blend'));print('235 COURSE V2 READY',len(a['rows']),len(a['new_edge_connected_floor_layers']),flush=True)
