import bpy,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-083';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));g=bpy.data.objects['083 real soil heightfield'];N=901;heights=[v.co.z for v in g.data.vertices];import numpy as np
h=np.asarray(heights,dtype=np.float32).reshape(N,N)[:-1,:-1];N-=1;w=np.sin(np.pi*(np.arange(N)+.5)/N)**2;wx=w[None,:];wy=w[:,None];h=h*wx*wy+np.roll(h,N//2,axis=1)*(1-wx)*wy+np.roll(h,N//2,axis=0)*wx*(1-wy)+np.roll(np.roll(h,N//2,axis=0),N//2,axis=1)*(1-wx)*(1-wy)
im=bpy.data.images.new('083 native procedural height',width=N,height=N,float_buffer=True);im.colorspace_settings.name='Non-Color';rgba=np.ones((N,N,4),dtype=np.float32);rgba[:,:,:3]=h[:,:,None];im.pixels.foreach_set(rgba.ravel());im.filepath_raw=str(O/'height.exr');im.file_format='OPEN_EXR';im.save();print('HEIGHT SOURCE',len(heights),'vertices; periodic blend fromsameheightfield')
