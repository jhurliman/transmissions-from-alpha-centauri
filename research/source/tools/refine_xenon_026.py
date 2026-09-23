import bpy,json,math,sys
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-026';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-025/scene.blend'));s=bpy.context.scene
C=bpy.data.collections['025 Reviewed architecture assembly'];C.name='026 Reviewed architecture assembly'
assets={c.get('part_id'):c for c in bpy.data.collections if c.get('part_id')};new_masters=[assets[k] for k in ['gangway_single_Y_8m','buttress_45','column_recessed_4m8']]
paint=bpy.data.materials['Cladding | slate enamel'];steel=bpy.data.materials['Structure | charcoal steel'];dark=bpy.data.materials['Recess | dark backing']
def box(n,p,d,m):
 x,y,z=p;a,b,c=[v/2 for v in d];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]);me.materials.append(m);ob=bpy.data.objects.new(n,me);C.objects.link(ob);be=ob.modifiers.new('Edge radius','BEVEL');be.width=.008;be.segments=2;return ob
# Support positions vary along the same unscaled platform to suit each frontage.
for key,shift in [('gangway_single_Y_left',1.6),('gangway_single_Y_right',-1.6)]:
 col=bpy.data.collections.new('FAC | '+key);col['part_id']=key;col.asset_mark()
 meta=json.loads(assets['gangway_single_Y_8m']['assembly_rules']);meta['support_offset_along_platform']=shift;col['assembly_rules']=json.dumps(meta)
 for original in assets['gangway_single_Y_8m'].objects:
  ob=original.copy();col.objects.link(ob)
  if ob.name.startswith(('Y stem','Y arm','Y splice','Foot plate','Splice bolt')):ob.location.x+=shift
 assets[key]=col;new_masters.append(col)

for ob in list(C.objects):
 if ob.instance_collection and ob.instance_collection.get('part_id')=='gangway_single_Y_8m':
  if ob.location.y>0:
   bpy.data.objects.remove(ob,do_unlink=True);continue
  else:ob.instance_collection=assets['gangway_single_Y_left' if ob.location.x<0 else 'gangway_single_Y_right']
 if ob.name.startswith(('Service bay portal jamb','Service bay lintel')):
  for v in ob.data.vertices:v.co.x+=1.40
 # The U-return's two legs are uniquely at these coordinates, isolated from other trunks.
 if ob.instance_collection and abs(ob.location.x+8)<.001 and (abs(ob.location.y-5.5)<.01 or abs(ob.location.y-6.5)<.01):ob.location.z-=1.2
# Far side-road facade supplies spatial depth instead of an unlit world-background slit.
box('Side road far facade',(19.0,3.2,10.5),(.3,5.6,21),paint)
for yy in [.48,1.8,3.2,4.6,5.92]:box('Side road vertical seam',(18.83,yy,10.5),(.055,.055,21),steel)
for zz in range(1,21,2):
 box('Side road floor joint',(18.80,3.2,zz),(.12,5.6,.08),steel)
 for yy in [1.65,4.6]:box('Side road recessed service panel',(18.79,yy,zz+.65),(.09,.8,.85),dark)

bpy.context.view_layer.update()
kit=R/'art/components/facades/v015';bpy.data.libraries.write(str(kit/'architectural-extensions.blend'),set(new_masters),fake_user=True)
(kit/'interfaces.json').write_text(json.dumps({c['part_id']:json.loads(c['assembly_rules']) for c in new_masters},indent=2))
s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
