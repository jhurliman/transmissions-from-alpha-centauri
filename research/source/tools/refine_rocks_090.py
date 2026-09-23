import bpy,bmesh,sys,random,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from rock_masters_090 import create_rock
O=R/'art/studies/rocks-090';bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;rng=random.Random(9033)
colors={'090 earth stone ':['634737','71513d','5d4638'],'090 bank fragment ':['89765f','716a70','625e69','9b8267']}
for pre,hexes in colors.items():
 for i,h in enumerate(hexes):
  m=bpy.data.materials[pre+str(i)];n=m.node_tree.nodes;l=m.node_tree.links;ra=next(q for q in n if q.type=='VALTORGB');r=ra.color_ramp
  while len(r.elements)>2:r.elements.remove(r.elements[-1])
  base=tuple(((int(h[j:j+2],16)/255+.055)/1.055)**2.4 for j in (0,2,4));r.elements[0].position=.03;r.elements[0].color=(*(v*.32 for v in base),1);r.elements[1].position=1.1 if False else 1;r.elements[1].color=(*(v*1.18 for v in base),1)
  bw=next(q for q in n if q.type=='RGBTOBW');mu=n.new('ShaderNodeMath');mu.operation='MULTIPLY';mu.inputs[1].default_value=.5;l.new(bw.outputs[0],mu.inputs[0]);l.new(mu.outputs[0],ra.inputs[0])
for ob in s.objects:
 if ob.type=='MESH' and ob.get('rock_family'):
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
g=s.objects['Street foundation'].evaluated_get(bpy.context.evaluated_depsgraph_get());C=bpy.data.collections['090 Larger fractured debris']
for side in [-1,1]:
 for j,y in enumerate([-3.0,3.8,9.6,16.8,24.7]):
  for k in range(2):
   x=side*(7.70+k*.37);yy=y+k*.60;hit,p,no,ind=g.ray_cast((x,yy,2),(0,0,-1))
   if not hit:continue
   ob=create_rock('090 lodged foundation slab','slab' if k==0 else 'shard',90400+j*11+k+(0 if side<0 else 70),(.55 if k==0 else .34,.98 if k==0 else .62,.39 if k==0 else .21))
   for c in list(ob.users_collection):c.objects.unlink(ob)
   C.objects.link(ob);ob.rotation_euler=(.28*side,rng.uniform(-.2,.2),rng.uniform(-1,1));ob.location=(x,yy,p.z-.065);ob.data.materials.append(bpy.data.materials['090 bank fragment '+str(j%4)])
s.render.threads_mode='FIXED';s.render.threads=4;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));bpy.ops.render.render(write_still=True)
s.render.use_freestyle=False;s.render.resolution_percentage=200;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.03;s.render.border_max_x=.42;s.render.border_min_y=.14;s.render.border_max_y=.52;s.render.filepath=str(O/'road-detail.png');bpy.ops.render.render(write_still=True)
