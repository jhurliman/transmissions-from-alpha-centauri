import bpy,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';sys.path.insert(0,str(R/'tools'));from soil_relief_083 import material
bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;g=bpy.data.objects['083 real soil heightfield'];g.data.materials[0]=material();sun=next(o for o in s.objects if o.type=='LIGHT' and o.data.type=='SUN')
for label,d in [('A',(.35,.65,-.7)),('B',(-.65,-.2,-.7))]:
 sun.rotation_euler=Vector(d).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
