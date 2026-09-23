"""Exact affine assembly transform using a shared SVD parent chain; retain linked meshes."""
import bpy,numpy as np
from mathutils import Matrix,Vector

def apply_affine(collection,transform):
 M=Matrix(transform);members=list(collection.objects);original={o:o.matrix_world.copy() for o in members};u,scale,vt=np.linalg.svd(np.array(M.to_3x3()))
 if np.linalg.det(u)<0:u[:,-1]*=-1;scale[-1]*=-1
 if np.linalg.det(vt)<0:vt[-1,:]*=-1;scale[-1]*=-1
 chain=[]
 for name,mat in [('orientation',Matrix(u.tolist()).to_4x4()),('depth',Matrix.Diagonal(tuple(scale)+(1,))),('obliquity',Matrix(vt.tolist()).to_4x4())]:
  e=bpy.data.objects.new('115 Coliseum '+name,None);collection.objects.link(e)
  if chain:e.parent=chain[-1]
  else:mat.translation=M.translation
  e.matrix_basis=mat;chain.append(e)
 for o in members:o.parent=chain[-1];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=original[o]
 bpy.context.view_layer.update();err=max((o.matrix_world@Vector(c)-M@original[o]@Vector(c)).length for o in members if o.type=='MESH' for c in o.bound_box)
 assert err<.002,err
 return {'maximum_corner_error_m':err,'linked_meshes_preserved':True,'world_transform':[list(r)for r in M]}
