import bpy,math,random
import numpy as np
from pathlib import Path
from mathutils import Vector
O=Path('/PATH/TO/transmissions-from-alpha-centauri/art/studies/soil-083');bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;g=bpy.data.objects['083 real soil heightfield'];a=np.empty(len(g.data.vertices)*3,dtype=np.float32);g.data.vertices.foreach_get('co',a);a=a.reshape(-1,3);rng=random.Random(83104)
for _ in range(95):
 cx=rng.uniform(0,3.8);cy=rng.uniform(0,3.8);rad=rng.uniform(.02,.04);ang=rng.uniform(0,math.tau);aspect=rng.uniform(.7,1.3);height=rng.uniform(.001,.003);dx=(a[:,0]+1.9-cx+1.9)%3.8-1.9;dy=(a[:,1]+1.9-cy+1.9)%3.8-1.9;u=dx*math.cos(ang)+dy*math.sin(ang);w=-dx*math.sin(ang)+dy*math.cos(ang);a[:,2]+=height*np.exp(-2.2*((u/rad)**2+(w/(rad*aspect))**2))
g.data.vertices.foreach_set('co',a.ravel());g.data.update();sun=next(o for o in s.objects if o.type=='LIGHT');sun.rotation_euler=Vector((.35,.65,-.7)).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'intermediate-A.png');bpy.ops.render.render(write_still=True)
