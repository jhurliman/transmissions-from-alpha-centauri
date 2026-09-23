import bpy,sys,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from ground_heightfield_087 import Field
O=R/'art/studies/ground-087'
for variant in 'ABC':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-085/scene.blend'))
 s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4
 g=bpy.data.objects['Street foundation'];mats=list(g.data.materials)
 data=np.load(O/f'{variant}-ground.npz');me=bpy.data.meshes.new(f'087 {variant} continuous terrain');me.from_pydata(data['vertices'],[],data['faces']);me.update()
 for m in mats:me.materials.append(m)
 for p,mi,sm in zip(me.polygons,data['materials'],data['smooth']):p.material_index=int(mi);p.use_smooth=bool(sm)
 g.data=me
 # Reuse exactly the quieter fine grain / macro slope shading of 086.
 path=str(R/'art/studies/ground-086/scene.blend')
 with bpy.data.libraries.load(path,link=False) as (src,dst):dst.materials=['086 soil: quiet grit and broad deposit lighting']
 me.materials[0]=dst.materials[0]
 field=Field(variant)
 for ob in s.objects:
  if ob.type!='MESH':continue
  if ob.name.startswith(('085 clustered low','085 trapped and bank grit','077 broken earth lip')):
   xyz=np.array([v.co[:] for v in ob.data.vertices]);
   if len(xyz):
    xyz[:,2]+=field(xyz[:,0],xyz[:,1]);ob.data.vertices.foreach_set('co',xyz.ravel());ob.data.update()
  elif ob.name.startswith(('077 embedded stone','079 earth bank grit')):
   if len(ob.data.vertices):
    p=ob.matrix_world@(sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices));ob.location.z+=float(field(p.x,p.y))
 bpy.ops.wm.save_as_mainfile(filepath=str(O/f'{variant}-scene.blend'))
 s.render.filepath=str(O/f'{variant}-main.png');bpy.ops.render.render(write_still=True)
 print('DONE',variant,flush=True)
