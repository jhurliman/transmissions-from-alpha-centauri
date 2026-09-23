"""Editable 145 panel family: geometry-only losses; no production-scene mutation."""
import bpy,bmesh,math,json,sys,random
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/alley-weathering-145/geometry'
W,H,T=1.12,1.42,.024

def mat(name,color,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;return m

def mesh(name,vs,fs,C):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);return o

def box(name,lo,hi,C):
 x,y,z=lo;X,Y,Z=hi
 return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],C)

def cutter(name,rings,C):
 # Rings in XZ, successively deeper Y. Cap + side surfaces form a closed solid.
 n=len(rings[0]);vs=[p for r in rings for p in r];fs=[tuple(range(n-1,-1,-1)),tuple(range((len(rings)-1)*n,len(rings)*n))]
 for j in range(len(rings)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;fs.append((a,b,b+n,a+n))
 o=mesh(name,vs,fs,C);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();return o

def ragged(path,seed,amp=.006):
 r=random.Random(seed);out=[]
 for i,(a,b) in enumerate(zip(path,path[1:]+path[:1])):
  out.append(a);e=Vector((b[0]-a[0],b[1]-a[1]));n=Vector((-e.y,e.x)).normalized()
  if e.length>.06:
   f=r.uniform(.30,.64);off=r.uniform(-amp,amp);out.append((a[0]+e.x*f+n.x*off,a[1]+e.y*f+n.y*off))
 return out

def cut(o,c):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Editable destructive feature construction','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(c,do_unlink=True)

def apply(scene=None):
 C=bpy.data.collections.new('145 Alley damage panel study');(scene or bpy.context.scene).collection.children.link(C)
 sys.path.insert(0,str(R/'tools'));from alley_panel_material_145 import make_panel_material
 paint=make_panel_material();core=mat('145 Exposed substrate',(0.24,.175,.12));dark=mat('145 Deep unlit backing steel',(.024,.031,.041),.91)
 panels=[];footprints={}
 for i,variant in enumerate(['top loss','facing pits','impact','crack']):
  x=i*(W+.022);o=box('145 Panel %02d %s'%(i+1,variant),(x,0,0),(x+W,T,H),C);o.data.materials.append(paint);o.data.materials.append(core);o['145 variant']=variant
  footprints[o.name]=[]
  if i==0:
   path=[(.12,H+.12),(.88,H+.12),(.86,1.25),(.79,1.26),(.75,1.08),(.64,1.04),(.61,.93),(.49,.95),(.40,1.10),(.27,1.12),(.25,1.25),(.13,1.28)]
   path=ragged(path,145,.014)
   rings=[[(x+u,-.04,z)for u,z in path],[(x+u+(.007 if k%3 else -.015),.07,z+(.018 if k%2 else -.012))for k,(u,z)in enumerate(path)]];cut(o,cutter('Top missing facing volume',rings,C));footprints[o.name].append(path)
  if i==1:
   for cx,cz,rx,rz,dep,phase in [(.35,.94,.21,.17,.010,0),(.79,.45,.115,.075,.007,1.2)]:
    p=[(cx+rx*(1+.25*math.sin(k*2.1+phase))*math.cos(k*math.tau/15),cz+rz*(1+.21*math.cos(k*2.7))*math.sin(k*math.tau/15))for k in range(15)];p=ragged(p,146+int(phase),.004)
    rings=[[(x+u,-.025,z)for u,z in p],[(x+cx+(u-cx)*.82,dep,cz+(z-cz)*.8)for u,z in p]];cut(o,cutter('Unequal shallow facing spall',rings,C));footprints[o.name].append(p)
  if i==2:
   cx,cz=.48,.91;p=[(cx+.115*(1+.18*math.sin(k*2.7))*math.cos(k*math.tau/13),cz+.10*(1+.22*math.cos(k*1.9))*math.sin(k*math.tau/13))for k in range(13)]
   rings=[[(x+cx+(u-cx)*1.35,-.016,cz+(z-cz)*1.35)for u,z in p],[(x+u,.006,z)for u,z in p],[(x+cx+.017+(u-cx)*.68,.05,cz+.007+(z-cz)*.77)for u,z in p]];cut(o,cutter('Irregular through impact entry',rings,C));footprints[o.name].append(p)
  if i==3:
   p=[(.29,1.42),(.31,1.23),(.44,1.11),(.40,.97),(.51,.83),(.49,.62)]
   # overlapping shallow triangular section cuts create a continuous real groove.
   for k,((a,b),(c,d))in enumerate(zip(p,p[1:])):
    e=Vector((c-a,d-b)).normalized();q=Vector((-e.y,e.x))*.0055
    outline=[(a+q.x,b+q.y),(c+q.x,d+q.y),(c-q.x,d-q.y),(a-q.x,b-q.y)]
    rings=[[(x+u,-.01,z)for u,z in outline],[(x+u,.008,z)for u,z in outline]];cut(o,cutter('Shallow connected crack %d'%k,rings,C))
   footprints[o.name].append(p)
  # Assign true cut returns/floors only, keep intact broad enamel faces unchanged.
  for p in o.data.polygons:
   if any(T-.00001>o.data.vertices[v].co.y>1e-5 for v in p.vertices) and not all(abs(o.data.vertices[v].co.y-T)<1e-5 for v in p.vertices):p.material_index=1
  # Return folds are seated behind sheet; top-loss variant omits upper return rather than bridging missing material.
  for label,lo,hi in [('left',(x,T,0),(x+.018,.07,H)),('right',(x+W-.018,T,0),(x+W,.07,H)),('bottom',(x+.018,T,0),(x+W-.018,.07,.018))]+([] if i==0 else [('top',(x+.018,T,H-.018),(x+W-.018,.07,H))]):
   f=box(o.name+' folded '+label,lo,hi,C);f.data.materials.append(paint)
  back=box(o.name+' recessed backing',(x+.01,.16,.01),(x+W-.01,.18,H-.01),C);back.data.materials.append(dark)
  panels.append({'id':str(i+1),'object':o,'origin':(x,0,0),'u':(1,0,0),'v':(0,0,1),'across':(1,0,0),'up':(0,0,1),'normal':(0,-1,0),'width':W,'height':H,'damage_footprints_uv':[[(u/W,z/H)for u,z in p]for p in footprints[o.name]]})
 A=bpy.data.collections.new('145 Clean panel master | asset');A.use_fake_user=True;clean=box('145 Clean master sheet',(0,0,0),(W,T,H),A);clean.data.materials.append(paint)
 for label,lo,hi in [('left',(0,T,0),(.018,.07,H)),('right',(W-.018,T,0),(W,.07,H)),('bottom',(.018,T,0),(W-.018,.07,.018)),('top',(.018,T,H-.018),(W-.018,.07,H))]:
  f=box('145 Clean master folded '+label,lo,hi,A);f.data.materials.append(paint)
 A.asset_mark()
 return C,panels,A

def main():
 bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;C,panels,A=apply(s);O.mkdir(parents=True,exist_ok=True)
 audit={'dimensions':[W,H,T],'fold_depth':.07,'backing_depth':.16,'panels':[],'source_scene_untouched':True}
 for p in panels:
  o=p['object'];bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(o.data);audit['panels'].append({**{k:v for k,v in p.items()if k!='object'},'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(signed=True)});bm.free()
 s.render.engine='BLENDER_EEVEE';s.world=bpy.data.worlds.new('145 Proof world');s.render.resolution_x=2200;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.world.color=(.15,.15,.15)
 camd=bpy.data.cameras.new('145 Kit proof');cam=bpy.data.objects.new('145 Kit proof',camd);s.collection.objects.link(cam);cam.location=(5.1,-8.5,3.7);target=Vector((2.25,0,.7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=5.4;s.camera=cam
 for name,pos,power,size in [('Warm key',(-2,-4,6),950,4),('Cool fill',(5,-3,2),150,3)]:
  d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 s.view_settings.view_transform='AgX';bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.data.libraries.write(str(O/'clean-master.blend'),{A},fake_user=True)
 s.render.filepath=str(O/'painted.png');bpy.ops.render.render(write_still=True)
 clay=mat('145 Clay',(.45,.45,.45));s.view_layers[0].material_override=clay;s.render.filepath=str(O/'clay.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
