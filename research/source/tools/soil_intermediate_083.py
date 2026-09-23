"""Bounded sparse intermediate relief variant; baseline remains immutable."""
import bpy,math,random
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083'
bpy.ops.wm.open_mainfile(filepath=str(O/'main-scene.blend'));s=bpy.context.scene;m=bpy.data.objects['Street foundation'].data.materials[0]
old=next(n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'height' in n.image.name.lower());W,H=old.size;pixels=np.asarray(old.pixels[:],dtype=np.float32).reshape(H,W,4);v=old.copy();v.name='083 sparse intermediate clods';h=pixels[:,:,0].copy();rng=random.Random(83104);xs=(np.arange(W)+.5)/W*3.8;ys=(np.arange(H)+.5)/H*3.8;X,Y=np.meshgrid(xs,ys)
for _ in range(95):
 cx=rng.uniform(0,3.8);cy=rng.uniform(0,3.8);rad=rng.uniform(.02,.04);a=rng.uniform(0,math.tau);aspect=rng.uniform(.7,1.3);height=rng.uniform(.001,.003)
 dx=(X-cx+1.9)%3.8-1.9;dy=(Y-cy+1.9)%3.8-1.9;u=dx*math.cos(a)+dy*math.sin(a);w=-dx*math.sin(a)+dy*math.cos(a);h+=height*np.exp(-2.2*((u/rad)**2+(w/(rad*aspect))**2))
pixels[:,:,:3]=h[:,:,None];v.pixels.foreach_set(pixels.ravel());v.filepath_raw=str(O/'intermediate-height.exr');v.file_format='OPEN_EXR';v.save();v.pack()
for n in m.node_tree.nodes:
 if n.type=='TEX_IMAGE' and n.image==old:n.image=v
bpy.ops.wm.save_as_mainfile(filepath=str(O/'intermediate-scene.blend'));s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.15;s.render.border_max_x=.5;s.render.border_min_y=.35;s.render.border_max_y=.58;s.render.filepath=str(O/'intermediate-shadow.png');bpy.ops.render.render(write_still=True)
