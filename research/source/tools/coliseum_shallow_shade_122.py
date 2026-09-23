"""Relate additional panel shade to modeled depth instead of a binary dark mask."""
import math
from mathutils import Vector,Matrix

def apply(C):
 anchor=Vector((0,-14,3.65));unlean=Matrix.Rotation(math.radians(-2),4,'X');rows=[]
 for ob in C.objects:
  if ob.type!='MESH' or ob.get('tier')!=3 or ob.get('coliseum_role')!='wall':continue
  me=ob.data;mask=me.attributes.get('118 Recess interior');pos=me.attributes.get('115 Original world position')
  if not mask or not pos:continue
  radial=[]
  for v in pos.data:
   q=unlean@(anchor+(v.vector-anchor)/.715-Vector((0,347,0)));radial.append(math.hypot(q.x,q.y)/(1-.055*q.z/78))
  shallow=deep=0
  for face in me.polygons:
   if mask.data[face.index].value<=0:continue
   depth=max(0.,75-sum(radial[k]for k in face.vertices)/len(face.vertices))
   span=max(radial[k]for k in face.vertices)-min(radial[k]for k in face.vertices)
   if depth<.65 and span<.10:mask.data[face.index].value=.12;shallow+=1
   else:deep+=1
  if shallow:rows.append({'object':ob.name,'shallow_faces':shallow,'deeper_faces_retained':deep})
 return {'objects':rows,'shallow_mask':.12,'authored_depth_threshold_m':.65,'intention':'Shallow field floors receive slight additional shade; narrow returns, deep niches and holes retain depth','geometry_changed':False}
