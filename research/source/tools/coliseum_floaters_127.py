"""Remove two verified detached legacy aggregate meshes; no crown reconstruction."""
import bpy
NAMES=('COL112 embedded aggregate31','COL112 embedded aggregate32')
def apply(C):
 removed=[]
 for name in NAMES:
  ob=C.objects.get(name)
  if ob is not None:
   removed.append({'object':name,'vertices':len(ob.data.vertices),'reason':'Detached legacy aggregate displaced independently from tower by grouped layout. Landmark-only BVH rays identify native126 dark marks at(1628,423)/(1717,409).'});bpy.data.objects.remove(ob,do_unlink=True)
 return {'removed':removed,'source_pixel_coordinates_3840x2885':[[1628,423],[1717,409]],'scope':'Only two named native meshes; regenerate contact ink after removal. No primary structure edits.'}
