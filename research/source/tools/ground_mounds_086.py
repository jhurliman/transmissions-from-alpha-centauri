"""Sparse finite soil deposits: actual mesh relief, with subordinate fine bump."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-086'
# x/y, ellipse radii, deposited height, angle; clustered lobes, not tiled noise.
M=[(-5.4,-5.8,1.55,2.05,.14,.4),(-4.65,-5.05,.82,1.15,.055,-.4),(3.35,-6.2,2.05,1.6,.12,-.65),(4.6,-5.8,.85,1.05,.045,.2),(-1.2,5.3,1.7,2.1,.105,.75),(-.35,6.35,.9,1.15,.05,-.3),(5.5,6.7,1.6,2.4,.18,-.2),(-5.65,13.1,1.75,2.15,.15,.4),(2.75,15.9,2.0,2.35,.11,-.4),(-2.6,22.5,1.7,2.5,.12,.3),(5.3,25.3,1.9,2.2,.14,-.6),(-5.25,29,1.8,2.5,.17,.5)]
def height(x,y):
 z=0
 for j,(cx,cy,rx,ry,h,a) in enumerate(M):
  dx=x-cx;dy=y-cy
  if abs(dx)>rx+ry or abs(dy)>rx+ry:continue
  u=(dx*math.cos(a)+dy*math.sin(a))/rx;v=(-dx*math.sin(a)+dy*math.cos(a))/ry
  phi=math.atan2(v,u);r2=(u*u+v*v)/(1+.10*math.sin(3*phi+j*.7)+.055*math.cos(5*phi+j))**2
  if r2<1:z+=h*(1-r2)**2.2
 return z

def apply(s):
 g=bpy.data.objects['Street foundation'];m=g.data.materials[0].copy();m.name='086 soil: quiet grit and broad deposit lighting';g.data.materials[0]=m;n=m.node_tree.nodes;l=m.node_tree.links
 for nd in n:
  if nd.type=='MIX_RGB' and nd.blend_type=='MULTIPLY' and abs(nd.inputs[0].default_value-.52)<.001:nd.inputs[0].default_value=.16
  if nd.type=='BUMP' and abs(nd.inputs['Distance'].default_value-.12)<.001:nd.inputs['Distance'].default_value=.035
 em=next(q for q in n if q.type=='EMISSION');base=em.inputs[0].links[0].from_socket;geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.47,-.55,.69);l.new(geo.outputs['Normal'],dot.inputs[0]);r=n.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.50;r.inputs['From Max'].default_value=.88;r.inputs['To Min'].default_value=.65;r.inputs['To Max'].default_value=1.35;l.new(dot.outputs['Value'],r.inputs[0]);mx=n.new('ShaderNodeMixRGB');mx.blend_type='MULTIPLY';mx.inputs[0].default_value=1;l.new(base,mx.inputs[1]);l.new(r.outputs[0],mx.inputs[2]);l.new(mx.outputs[0],em.inputs[0])
 C=bpy.data.collections.new('086 Sparse deposited soil mounds');s.collection.children.link(C)
 step=.09;nx=int(16.4/step)+1;ny=int(43.5/step)+1;vs=[];hs=[];fs=[]
 for j in range(ny):
  y=-9.5+j*step
  for i in range(nx):
   x=-8.2+i*step;h=height(x,y);vs.append((x,y,-.043+h));hs.append(h)
 for j in range(ny-1):
  for i in range(nx-1):
   a=j*nx+i;ids=(a,a+1,a+1+nx,a+nx)
   if max(hs[k] for k in ids)>.001:fs.append(ids)
 me=bpy.data.meshes.new('086 finite deposits height surface');me.from_pydata(vs,[],fs);me.materials.append(m);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob)
 for p in me.polygons:p.use_smooth=True
 # Existing grains move onto deposited soil. Grain scale and materials stay intact.
 shifted=[]
 for ob in s.objects:
  if ob.type!='MESH':continue
  if ob.name.startswith(('085 clustered low','085 trapped and bank grit')):
   for v in ob.data.vertices:v.co.z+=height(v.co.x,v.co.y)
   ob.data.update();shifted.append(ob.name)
  elif ob.name.startswith(('077 embedded stone','079 earth bank grit')):
   if not ob.data.vertices:continue
   p=ob.matrix_world@(sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices));h=height(p.x,p.y)
   if h>.001:ob.location.z+=h;shifted.append(ob.name)
 for ls in s.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE' and C.name not in ls.collection.children:ls.collection.children.link(C)
 return {'mound_lobes':len(M),'height_max_m':max(hs),'mesh_faces':len(fs),'moved_grain_and_stone_objects':len(shifted),'grain_objects':shifted,'fine_bump_strength_reduction':'.52→.16 color influence; .12→.035 height scale','actual_mesh_displacement':True,'covered_cracks':'Deposited soil naturally covers local portions of underlying cracks; no crack centerlines altered','mounds':M}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/ground-085/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;stats=apply(s);(O/'audit.json').write_text(json.dumps(stats,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
