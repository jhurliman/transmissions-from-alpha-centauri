"""Straight structural crack axes, grain-fragmented physical lips and trapped grit."""
import bpy,bmesh,math,random,json,sys
from mathutils import Vector,noise
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from ground_surface_085 import mineral
O=R/'art/studies/ground-085'
PROFILE=[(-3.7,-9,3.5),(2.4,-4.5,11),(-1.5,10,24.2),(4,14.5,30)]
def straight(p):
 x,y,z=p
 for j,(base,a,b) in enumerate(PROFILE):
  if a<=y<=b:
   t=(y-a)/(b-a);wave=.25*math.sin(t*6+j);d=abs(x-(base+wave));w=1 if d<.16 else max(0,1-(d-.16)/.42);w=w*w*(3-2*w);x-=wave*w
 return x,y,z

def apply(s):
 rng=random.Random(85071);ground=bpy.data.objects['Street foundation'];changed=[]
 for ob in s.objects:
  if ob.type=='MESH' and (ob==ground or ob.name.startswith(('077 broken earth lip','079 earth bank grit','085 clustered low'))):
   for v in ob.data.vertices:v.co=straight(v.co)
   ob.data.update();changed.append(ob.name)
 # Give lips broken mineral lighting instead of long broad tan bars.
 mats=[mineral('085 fracture grain '+str(i),c) for i,c in enumerate([(73,54,42),(101,78,56),(58,44,34),(132,106,76)])]
 lip=mats[1].copy();lip.name='085 granular broken crack lip';n=lip.node_tree.nodes;l=lip.node_tree.links;e=next(x for x in n if x.type=='EMISSION');src=e.inputs[0].links[0].from_socket;co=n.new('ShaderNodeNewGeometry');ns=n.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=7.5;ns.inputs['Detail'].default_value=2;l.new(co.outputs['Position'],ns.inputs['Vector']);rp=n.new('ShaderNodeValToRGB');rp.color_ramp.interpolation='CONSTANT';rp.color_ramp.elements[0].position=.48;rp.color_ramp.elements[0].color=(.28,.28,.28,1);rp.color_ramp.elements[1].position=.68;rp.color_ramp.elements[1].color=(1.05,1.05,1.05,1);el=rp.color_ramp.elements.new(.57);el.color=(.62,.62,.62,1);l.new(ns.outputs['Fac'],rp.inputs[0]);mx=n.new('ShaderNodeMixRGB');mx.blend_type='MULTIPLY';mx.inputs[0].default_value=1;l.new(src,mx.inputs[1]);l.new(rp.outputs[0],mx.inputs[2]);l.new(mx.outputs[0],e.inputs[0])
 for ob in s.objects:
  if ob.name.startswith('077 broken earth lip'):ob.data.materials.clear();ob.data.materials.append(lip)
 # Every sample sits on actual ground, so intersecting voids are respected.
 bm=bmesh.new();bm.from_mesh(ground.data);edges=[]
 for ed in bm.edges:
  if len(ed.link_faces)!=2 or {f.material_index for f in ed.link_faces}!={0,1}:continue
  a,b=[v.co.copy() for v in ed.verts]
  if abs(a.z+.04)>.001 or abs(b.z+.04)>.001:continue
  mid=(a+b)*.5
  if abs(mid.x)<7.4 and -9<mid.y<34 and (b-a).length>.006:edges.append((a,b))
 bm.free();vs=[];fs=[];inds=[];stones=0;C=bpy.data.collections['085 Compacted soil granular relief']
 for a,b in edges:
  d=b-a;length=d.length;d.normalize();side=Vector((-d.y,d.x,0));steps=max(1,int(length/.11))
  for k in range(steps):
   if rng.random()<.73:continue
   t=(k+rng.random())/steps;p=a.lerp(b,t)+side*rng.gauss(0,.055)
   hit,loc,norm,idx=ground.ray_cast(Vector((p.x,p.y,.4)),Vector((0,0,-1)))
   if not hit:continue
   r=rng.uniform(.012,.048)*(1.5 if rng.random()<.1 else 1);h=rng.uniform(.2,.55)*r;N=rng.choice([4,5,6]);base=len(vs);ang=rng.random()*math.tau
   for j in range(N):
    th=j*math.tau/N+ang;rr=r*rng.uniform(.7,1.15);vs.append((p.x+math.cos(th)*rr,p.y+math.sin(th)*rr,loc.z-.003))
   for j in range(N):
    bx,by,bz=vs[base+j];f=rng.uniform(.35,.7);vs.append((p.x+(bx-p.x)*f,p.y+(by-p.y)*f,loc.z+h*rng.uniform(.65,1.05)))
   m=rng.choices(range(4),[3,2,5,1])[0]
   for j in range(N):fs.append((base+j,base+(j+1)%N,base+N+(j+1)%N,base+N+j));inds.append(m)
   fs.append(tuple(base+N+j for j in range(N)));inds.append(m)
   stones+=1
 me=bpy.data.meshes.new('085 trapped and bank grit');me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob)
 for m in mats:me.materials.append(m)
 for f,i in zip(me.polygons,inds):f.material_index=i
 return {'axis_correction':'Removed the .25m sine drift from all four longitudinal structural breaks. Small edge chips remain. Shared deformation preserves cut/lip intersections.','changed_meshes':len(changed),'boundary_segments':len(edges),'bank_and_trapped_grains':stones,'substrate':'existing native recessed geometry'}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(O/'surface-scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;rep=apply(s);(O/'break-audit.json').write_text(json.dumps(rep,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
