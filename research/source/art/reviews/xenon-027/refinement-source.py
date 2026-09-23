import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-027';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-026/scene.blend'));s=bpy.context.scene
C=bpy.data.collections['026 Reviewed architecture assembly'];C.name='027 Reviewed architecture assembly'
assets={c.get('part_id'):c for c in bpy.data.collections if c.get('part_id')};new_masters=[assets[k] for k in ['gangway_single_Y_8m','buttress_45','column_recessed_4m8']]
paint=bpy.data.materials['Cladding | slate enamel'];steel=bpy.data.materials['Structure | charcoal steel'];dark=bpy.data.materials['Recess | dark backing']
def box(n,p,d,m):
 x,y,z=p;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);C.objects.link(ob);be=ob.modifiers.new('Edge radius','BEVEL');be.width=.008;be.segments=2;return ob
# Continuous side wall bounds the road beyond the shallow facade return.
box('Side road north building wall',(19.5,6.08,10.5),(20,.20,21),paint)
for zz in range(1,21,2):box('Side road north floor band',(19.5,5.95,zz),(20,.10,.09),steel)
for xx in range(11,30,3):box('Side road north vertical seam',(xx,5.94,10.5),(.06,.08,21),steel)

s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
