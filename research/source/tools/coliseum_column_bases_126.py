"""Visible simpler upper-arcade bases seated above actual floor bands."""
import bpy,bmesh,math,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def apply(C):
 tree=ast.parse((R/'tools/coliseum_columns_124.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='apply');oldprofile=ast.literal_eval(next(n.value for n in fn.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='profile'for t in n.targets)))
 profile=[(1.15,1.60),(1.15,1.80),(1.08,1.85),(1.08,1.98),(1.14,2.05),(1.16,2.15),(1.14,2.25),(1.04,2.34),(.95,2.46),(.92,2.57)]+[(r,z)for r,z in oldprofile if z>=5.0]
 cache={};rows=[]
 for ob in C.objects:
  if ob.type!='MESH'or ob.get('tier')not in[1,2]or'COL124'not in ob.name or'engaged round column'not in ob.name:continue
  old=ob.data
  if old not in cache:
   N=32;v=[(r*math.cos(i*math.tau/N),r*math.sin(i*math.tau/N),z)for r,z in profile for i in range(N)];f=[tuple(range(N-1,-1,-1))]
   for k in range(len(profile)-1):
    for i in range(N):f.append((k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i))
   f.append(tuple((len(profile)-1)*N+i for i in range(N)));off=len(v);v.extend([(x,y,z)for z in[17.45,18.]for x,y in[(-1.27,-1.05),(1.27,-1.05),(1.27,1.05),(-1.27,1.05)]]);f.extend(tuple(off+i for i in face)for face in[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
   me=bpy.data.meshes.new('126 Upper arcade simplified round base');me.from_pydata(v,[],f);me.update()
   for p in me.polygons:p.use_smooth=len(p.vertices)==4 and min(p.vertices)<off
   for m in old.materials:me.materials.append(m)
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(me);bm.free()
   if bad or volume<=0:raise RuntimeError('Invalid upper column base')
   cache[old]=(me,bad,volume)
  me,bad,volume=cache[old];ob.data=me;ob['126 upper base']='One torus ring instead of two; foot sits at visible floorband top';rows.append({'object':ob.name,'tier':ob['tier'],'foot_authored_z':2.73+ob['tier']*18.33+1.6,'capital_height_unchanged':True,'nonmanifold_edges':bad,'volume':volume})
 return {'upper_columns':len(rows),'shared_meshes':len(cache),'lower_level_unchanged':True,'upper_profile':profile,'base_torus_rings':1,'lower_base_torus_rings':2,'rows':rows}
