"""Surgical snap of inserted nearly-collinear front seam vertices; no remesh."""
import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-127/seam-diagnostic';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import strict_crossings,topology
from coliseum_arch_ratio_125 import mapping

def apply(C):
 original,world,unpack=mapping();rows=[]
 for tier in [0,2]:
  ob=bpy.data.objects[f'COL127 T{tier} continuous arcade wall'];m=ob.data;m.calc_loop_triangles();pairs=strict_crossings(ob,True);fs=set(m.loop_triangles[i].polygon_index for p in pairs for i in p);moves=[]
  for fi in fs:
   f=m.polygons[fi]
   if len(f.vertices)<5:continue
   if not all(abs(unpack(ob.matrix_world@m.vertices[i].co)[0]-75)<.001 for i in f.vertices):continue
   ids=list(f.vertices)
   for k,i in enumerate(ids):
    a=m.vertices[ids[k-1]].co;b=m.vertices[ids[(k+1)%len(ids)]].co;p=m.vertices[i].co;v=b-a;t=(p-a).dot(v)/v.length_squared;h=a+v*t;d=(p-h).length
    if 1e-4<t<1-1e-4 and 1e-8<d<.001:
     m.vertices[i].co=h;at=m.attributes.get('115 Original world position')
     if at:at.data[i].vector=original(*unpack(ob.matrix_world@h))
     moves.append({'vertex':i,'distance':d,'face':fi})
  m.update();rows.append({'tier':tier,'moves':moves,'after':topology(ob)})
 return rows
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/seams/geometry.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'snap-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'snap.blend'));print(a)
