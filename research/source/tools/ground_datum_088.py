import bpy,sys,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from ground_heightfield_087 import Field,smooth
O=R/'art/studies/ground-088'
a=Field('A');c=Field('C');xx,yy=np.meshgrid(np.linspace(-7.35,7.35,160),np.linspace(-8.4,32.4,440))
def edge(x,y):return smooth((8.2-np.abs(x))/.85)*smooth((y+10.5)/1.4)*smooth((35-y)/2)
delta=float((c(xx,yy).mean()-a(xx,yy).mean())/edge(xx,yy).mean())
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-087/C-scene.blend'));s=bpy.context.scene
hidden=[]
for ob in s.objects:
 if ob.name=='Street foundation' or ob.name.startswith('077 broken earth lip'):
  xyz=np.array([v.co[:] for v in ob.data.vertices]);xyz[:,2]-=delta*edge(xyz[:,0],xyz[:,1]);ob.data.vertices.foreach_set('co',xyz.ravel());ob.data.update()
 if ob.name.startswith(('085 clustered low','085 trapped and bank','077 embedded stone','079 earth bank grit')):
  ob.hide_render=True;ob.hide_set(True);hidden.append(ob.name)
# Inventory any older road scatter layers for review.
possible=[ob.name for ob in s.objects if any(k in ob.name.lower() for k in ('rock','pebble','stone','gravel')) and not ob.hide_render]
(O/'datum-audit.json').write_text(json.dumps({'mean_A_m':float(a(xx,yy).mean()),'mean_C_m':float(c(xx,yy).mean()),'mean_adjusted_C_m':float((c(xx,yy)-delta*edge(xx,yy)).mean()),'lowered_m':delta,'hidden_road_scatter':hidden,'remaining_rock_named_objects':possible},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
