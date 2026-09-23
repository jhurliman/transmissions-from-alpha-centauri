"""Isolated clean B10 recovery; preserve authoritative127 modifiers and materials."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-128/b10-rebuild';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
from coliseum_arch_ratio_125 import mapping
NAME='COL127 T2 continuous arcade wall'
def apply(C):
 ob=bpy.data.objects[NAME];old=ob.data;before=topology(ob);_,_,unpack=mapping()
 with bpy.data.libraries.load(str(O/'geometry.blend'),link=False)as(src,dst):dst.objects=[NAME]
 imported=dst.objects[0];new=imported.data.copy();bpy.data.objects.remove(imported)
 # Resolve source slot roles through the authoritative127 slot layout. The live
 # scene may carry newer128/129 material datablocks; keep those exact slots.
 import re
 canonical=lambda m:re.sub(r"\.\d{3}$",'',m.name)if m else ''
 if Path(bpy.data.filepath)==R/'art/studies/coliseum-127/scene.blend':baseline_names=[canonical(m)for m in old.materials]
 else:
  with bpy.data.libraries.load(str(R/'art/studies/coliseum-127/scene.blend'),link=False)as(src,dst):dst.objects=[NAME]
  reference=dst.objects[0];baseline_names=[canonical(m)for m in reference.data.materials];bpy.data.objects.remove(reference)
 oldmaterials=list(old.materials);newmaterials=list(new.materials);names=[m.name if m else ''for m in oldmaterials];lookup={}
 if len(oldmaterials)<len(baseline_names):raise RuntimeError('Live material role slots differ from127; explicit mapping required')
 for i,ma in enumerate(newmaterials):
  name=canonical(ma)
  if name not in baseline_names:raise RuntimeError('Unrecognized source material role '+name)
  lookup[i]=baseline_names.index(name)
 ids=[lookup[p.material_index]for p in new.polygons];new.materials.clear()
 for m in oldmaterials:new.materials.append(m)
 for p,i in zip(new.polygons,ids):p.material_index=i
 # Both joined meshes use identity matrix and absolute accepted coordinates.
 ac=-math.pi+10.5*math.tau/36;half=math.tau/36*.34;lo=ac-half;hi=ac+half
 tree=BVHTree.FromPolygons([v.co for v in new.vertices],[tuple(p.vertices)for p in new.polygons]);distance=[];exact=0;newset={tuple(v.co)for v in new.vertices}
 for v in old.vertices:
  aa=unpack(ob.matrix_world@v.co)[1]
  if lo-3e-5<=aa<=hi+3e-5:continue
  exact+=tuple(v.co)in newset;distance.append(tree.find_nearest(v.co)[3])
 ob.data=new;after=topology(ob)
 if after['nonmanifold']or after['strict_crossings']:ob.data=old;raise RuntimeError('Unsafe prepared mesh')
 audit={'before':before,'after':after,'outside_B10_old_vertices':len(distance),'outside_B10_exact_positions':exact,'outside_B10_max_surface_distance':max(distance),'material_names':names,'modifiers_preserved':[m.name for m in ob.modifiers]}
 return audit
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'prepared-audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'prepared.blend'));print(a)
