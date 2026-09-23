"""Future123 repair proof: clean111 bay8 source through E/yaw, replay119 authored features.
Does not mutate current121/122 integrations. Reject any replay cut that increases strict crossings.
"""
import bpy,bmesh,math,json,sys,types,time
from pathlib import Path
from mathutils import Matrix,Vector,geometry
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-123/repair';NAMES=['COL110 U8 fractured upper wall L','COL110 U8 fractured upper wall R']
def strict_crossings(ob,details=False):
 me=ob.data;me.calc_loop_triangles();vs=[ob.matrix_world@v.co for v in me.vertices];ts=list(me.loop_triangles);fs=[tuple(t.vertices)for t in ts];tree=BVHTree.FromPolygons(vs,fs,all_triangles=True);pairs=[]
 for i,j in tree.overlap(tree):
  if i>=j or set(fs[i])&set(fs[j]):continue
  A=[vs[k]for k in fs[i]];B=[vs[k]for k in fs[j]];na=(A[1]-A[0]).cross(A[2]-A[0]);nb=(B[1]-B[0]).cross(B[2]-B[0])
  if na.length<1e-10 or nb.length<1e-10 or abs(na.normalized().dot(nb.normalized()))>.99999:continue
  found=False
  for V,W in [(A,B),(B,A)]:
   n=(W[1]-W[0]).cross(W[2]-W[0]).normalized()
   for k in range(3):
    a,b=V[k],V[(k+1)%3];d=b-a;d0=(a-W[0]).dot(n);d1=(b-W[0]).dot(n)
    if not(min(d0,d1)<-.00001 and max(d0,d1)>.00001)or d.length<1e-8:continue
    h=geometry.intersect_ray_tri(*W,d.normalized(),a,True)
    if h is None:continue
    distance=(h-a).dot(d.normalized())
    if not .00001<distance<d.length-.00001:continue
    e0,e1,q=W[1]-W[0],W[2]-W[0],h-W[0];aa,bb,cc,dd,ee=e0.dot(e0),e0.dot(e1),e1.dot(e1),q.dot(e0),q.dot(e1);den=aa*cc-bb*bb
    if abs(den)<1e-20:continue
    u=(cc*dd-bb*ee)/den;v=(aa*ee-bb*dd)/den
    if min(u,v,1-u-v)>1e-5:found=True;break
   if found:break
  if found:pairs.append([i,j])
 return pairs if details else len(pairs)
def topology(ob):
 bm=bmesh.new();bm.from_mesh(ob.data);d={'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume(),'strict_crossings':strict_crossings(ob)};bm.free();return d

def apply_prepared(C):
 """Load validated repaired L/R data only; keep current transforms and material treatments."""
 targets={name:bpy.data.objects[name]for name in NAMES}
 with bpy.data.libraries.load(str(O/'geometry.blend'),link=False)as(src,dst):dst.objects=list(NAMES)
 out=[]
 for name,loaded in zip(NAMES,dst.objects):
  target=targets[name];mats=list(target.data.materials);target.data=loaded.data.copy();target.data.materials.clear()
  for m in mats:target.data.materials.append(m)
  for f in target.data.polygons:f.material_index=min(f.material_index,max(0,len(mats)-1))
  target['123 repaired crown base']=True;out.append({'object':name,**topology(target)});bpy.data.objects.remove(loaded,do_unlink=True)
 return out

def run():
 O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-111/scene.blend'));source={};check={};anchor=next(o for o in bpy.data.objects if o.get('bay')==4 and 'fractured upper wall L'in o.name);lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');delta=anchor.matrix_world@auth.inverted();P=delta@Matrix.Translation(Vector((0,347,0)))@lean;Pi=P.inverted()
 for name in NAMES:
  ob=bpy.data.objects[name];source[name]={'vertices':[ob.matrix_world@v.co for v in ob.data.vertices],'faces':[tuple(f.vertices)for f in ob.data.polygons]};check[name]={'111_source':topology(ob)}
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix'])
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-116/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin']
 for name,d in source.items():
  ob=bpy.data.objects[name];check[name]['116_old']=topology(ob);old=ob.data;iv=ob.matrix_world.inverted();vv=[]
  for w in d['vertices']:
   p=Pi@w;r=math.hypot(p.x,p.y);theta=math.atan2(p.y,p.x);outer=75*(1-.055*p.z/78)
   if r<outer:r=outer+.55*(r-outer)
   if theta>math.pi/2:theta-=math.tau
   theta=-math.pi/2+.68*(theta+math.pi/2);p.x=r*math.cos(theta);p.y=r*math.sin(theta);vv.append(iv@(Y@A@P@p))
  me=bpy.data.meshes.new('123 clean111 '+name);me.from_pydata(vv,[],d['faces']);me.update()
  for m in old.materials:me.materials.append(m)
  attr=me.attributes.new('115 Original world position','FLOAT_VECTOR','POINT')
  for i,w in enumerate(d['vertices']):attr.data[i].vector=w
  ob.data=me;ob['123 clean crossing-free base']=True;check[name]['123_warped_clean']=topology(ob)
  if check[name]['123_warped_clean']['strict_crossings']or check[name]['123_warped_clean']['nonmanifold']:raise RuntimeError('Clean warp failed '+name)
 # Execute exact119 source definitions with an extra strict per-cut guard, not a changed aperture design.
 text=(R/'tools/coliseum_structure_119.py').read_text().split("if __name__=='__main__':")[0]
 text=text.replace('du=.14*math.sin(k*2.17+ring*1.3)*math.sin(math.pi*t);dz=.16*math.cos(k*1.71-ring*.8)*math.sin(math.pi*t)','du=0.;dz=0.')
 text=text.replace("old=ob.data;ob.data=old.copy();before=", "old=ob.data;before_cross=strict_crossings(ob);ob.data=old.copy();before=")
 text=text.replace("if bad or (after[0]and volume<=0):", "after_cross=strict_crossings(ob)\n   if bad or (after[0]and volume<=0) or after_cross>before_cross:")
 text=text.replace("'volume':volume});continue", "'volume':volume,'strict_before':before_cross,'strict_after':after_cross});continue")
 text=text.replace("'outside_cutter_max_error_m':outside_error", "'outside_cutter_max_error_m':outside_error,'strict_before':before_cross,'strict_after':after_cross")
 namespace={'__file__':str(R/'tools/coliseum_structure_119.py'),'__name__':'coliseum_119_replay123','strict_crossings':strict_crossings};exec(compile(text,'<123 strict replay119>','exec'),namespace);replay=namespace['build_visible_bay'](C)
 for name in NAMES:check[name]['123_replayed119']=topology(bpy.data.objects[name])
 audit={'method':'Clean111 source, exact115E+116yaw, guarded replay of119 authored features','source_checks':check,'replay':replay,'current_scenes_unchanged':True,'new_fine_chips':False};(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'geometry.blend'));print(json.dumps(audit),flush=True)
 # Reuse119 fixed bay view and lighting, substituting only repaired object data and native feature replay.
 repaired={o.name:(o.data.copy(),o.matrix_world.copy())for o in C.objects if o.name in NAMES};bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-119/geometry-proof.blend'))
 # Copies do not survive file-open; reload final objects as local library after opening proof.
 with bpy.data.libraries.load(str(O/'geometry.blend'),link=False)as(src,dst):dst.objects=list(NAMES)
 for new in dst.objects:
  target=bpy.data.objects[new.name.removesuffix('.001')] if new.name.endswith('.001')else None
  if target:target.data=new.data.copy();bpy.data.objects.remove(new,do_unlink=True)
 s=bpy.context.scene;s.render.resolution_x=1600;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.use_freestyle=False;s.render.threads_mode='FIXED';s.render.threads=4;s.use_nodes=False;mat=bpy.data.materials.new('123 neutral repair');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.38,.38,.38,1);bs.inputs['Roughness'].default_value=.85
 for ob in bpy.data.collections['110 Coliseum detailed front ruin'].objects:
  if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(mat)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'proof.blend'));s.render.filepath=str(O/'after-clay.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':run()
