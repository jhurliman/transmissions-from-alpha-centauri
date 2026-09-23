"""Surgical clean111 B10 spall recovery within authoritative127 joined wall."""
import bpy,bmesh,math,sys,json,statistics
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-128/b10-rebuild';sys.path.insert(0,str(R/'tools'))
from coliseum_crown_repair_123 import topology
from coliseum_arch_ratio_125 import mapping
TARGET='COL127 T2 continuous arcade wall';SOURCE='COL110 T2 B10 loadbearing arch tunnel'
def apply(C):
 original,world,unpack=mapping();target=bpy.data.objects[SOURCE];before=topology(target);old=target.data;ac=-math.pi+10.5*math.tau/36;half=math.tau/36*.34;amin=ac-half;amax=ac+half
 existing_angles=[unpack(target.matrix_world@v.co)[1]for v in old.vertices];amin=statistics.median(a for a in existing_angles if abs(a-amin)<2e-5);amax=statistics.median(a for a in existing_angles if abs(a-amax)<2e-5)
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-111/scene.blend'),link=False)as(src,dst):dst.objects=[SOURCE,'COL110 U4 fractured upper wall L']
 src,anchor=dst.objects;lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=anchor.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;Pi=P.inverted();coords=[]
 # Retain113's accepted deep left-shoulder cavity, replayed on the clean pre112 surface.
 C.objects.link(src);bpy.context.view_layer.update();outline=[(-4.8,61.6),(-2.2,61.6),(-2.2,60.4),(-2.65,60.2),(-2.4,59.5),(-2.95,58.9),(-2.7,58.2),(-3.15,57.7),(-2.85,56.8),(-3.10,56.1),(-2.95,55.3),(-3.5,54.4),(-3.25,53.7),(-3.9,52.3),(-4.45,52.0),(-4.8,53.2),(-4.45,54.5),(-4.9,55.7),(-4.55,57.2),(-4.85,58.5)];N=len(outline)
 vs=[P@Vector((rr*(1-.055*z/78)*math.cos(ac+u/75),rr*(1-.055*z/78)*math.sin(ac+u/75),z))for rr in [70.5,76.8]for u,z in outline];fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N)for k in range(N)]
 cm=bpy.data.meshes.new('128 exact113 shoulder');cm.from_pydata(vs,[],fs);cm.update();cut=bpy.data.objects.new('128 temporary shoulder cutter',cm);C.objects.link(cut);bpy.context.view_layer.objects.active=src;mod=src.modifiers.new('128 restore113 shoulder','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True);replaycheck=topology(src)
 if replaycheck['nonmanifold']or replaycheck['strict_crossings']:raise RuntimeError('113 clean replay unsafe '+str(replaycheck))

 for v in src.data.vertices:
  p=Pi@(src.matrix_basis@v.co);z=p.z;r=math.hypot(p.x,p.y)/(1-.055*z/78);a=math.atan2(p.y,p.x)
  if a>math.pi/2:a-=math.tau
  if abs(a-amin)<2e-5:a=amin
  if abs(a-amax)<2e-5:a=amax
  if abs(r-67)<.001:r=67.
  if abs(r-75)<.001:r=75.
  if abs(z-57.72)<.001:z=57.72
  if abs(z-51.085)<.001:z=51.085
  coords.append((r,a,z))

 faces=[tuple(f.vertices)for f in src.data.polygons];me=bpy.data.meshes.new('128 clean B10 recovered');iv=target.matrix_world.inverted();me.from_pydata([iv@world(*co)for co in coords],[],faces);me.update()
 for m in old.materials:me.materials.append(m)
 from mathutils.bvhtree import BVHTree
 tree=BVHTree.FromPolygons([v.co for v in old.vertices],[tuple(p.vertices)for p in old.polygons],all_triangles=False)
 for f in me.polygons:
  hit=tree.find_nearest(f.center)
  if hit[2]is not None:f.material_index=old.polygons[hit[2]].material_index
 at=me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');dl=me.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
 for i,(rr,a,z)in enumerate(coords):at.data[i].vector=original(rr,a,z);dl.data[i].value=max(0,min(1,(75-rr)/8))
 target.data=me;bpy.data.objects.remove(src,do_unlink=True);bpy.data.objects.remove(anchor,do_unlink=True)
 clean=topology(target)
 from coliseum_seams_127 import apply as seams
 sa=seams(C,tiers=(2,))
 import coliseum_seam_repair_127 as sr
 text=Path(sr.__file__).read_text().split("if __name__")[0].replace('for tier in [0,2]:','for tier in [2]:');ns={};exec(compile(text,sr.__file__,'exec'),dict(sr.__dict__),ns);fix=ns['apply'](C)
 return {'source_before':before,'clean_source':clean,'seams':sa,'fix':fix,'after':topology(bpy.data.objects[TARGET])}
if __name__=='__main__':
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-126/scene.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin']);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(a)
