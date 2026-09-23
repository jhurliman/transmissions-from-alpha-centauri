"""Shared engaged arcade columns, preserving structural pier cores and approved pose."""
import bpy,bmesh,math,json,ast,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1]
def apply(C):
 t=time.time()
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 a=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=a.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(a)
 A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);yaw=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=yaw@A@P
 tree=ast.parse((R/'tools/coliseum_linked_116.py').read_text());factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='group');ns={'bpy':bpy,'math':math};exec(compile(ast.Module(body=[factory],type_ignores=[]),'<column warp>','exec'),ns);g=ns['group']();g.name='124 Shared engaged column warp'
 # Radius/height profile: broad plinth, torus, scotia, torus, tapered shaft, neck, echinus and cap.
 profile=[(1.15,0),(1.15,.21),(1.08,.27),(1.08,.43),(1.17,.51),(1.20,.63),(1.17,.75),(1.04,.85),(.99,.99),(.99,1.18),(1.06,1.29),(1.07,1.41),(1.01,1.52),(.92,1.65),(.92,2.20),(.94,5.0),(.90,10.0),(.84,16.53),(.90,16.58),(.94,16.67),(.94,16.80),(.89,16.87),(.91,16.97),(.94,17.06),(1.00,17.14),(1.08,17.22),(1.15,17.28),(1.19,17.34),(1.20,17.46)]
 v=[(rad*math.cos(i*math.tau/32),rad*math.sin(i*math.tau/32),z)for rad,z in profile for i in range(32)];f=[tuple(range(31,-1,-1))]
 for k in range(len(profile)-1):
  for i in range(32):f.append((k*32+i,k*32+(i+1)%32,(k+1)*32+(i+1)%32,(k+1)*32+i))
 f.append(tuple((len(profile)-1)*32+i for i in range(32)))
 off=len(v);v.extend([(x,y,z)for z in [17.45,18.00]for x,y in [(-1.27,-1.05),(1.27,-1.05),(1.27,1.05),(-1.27,1.05)]]);f.extend([tuple(off+i for i in inds)for inds in [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]])
 me=bpy.data.meshes.new('124 Shared round shaft base and capital');me.from_pydata(v,[],f);me.update()
 for p in me.polygons:p.use_smooth=len(p.vertices)==4 and min(p.vertices)<off
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume();bm.to_mesh(me);bm.free()
 added=[];removed=[];masters={};targets=[o for o in C.objects if ' pier pilaster' in o.name and o.type=='MESH']
 for old in targets:
  j=old.get('bay');tier=old.get('tier');mat=old.data.materials[0];key=mat.name
  if key not in masters:
   m=me.copy();m.materials.clear();m.materials.append(mat);masters[key]=m
  ang=-math.pi+(j+1)*math.tau/36;z=2.73+tier*18.33;rad=74.62;batter=1-.055*z/78;rv=Vector((math.cos(ang),math.sin(ang),0));tv=Vector((-math.sin(ang),math.cos(ang),0));M=Matrix.Identity(4)
  for c,vec in enumerate([tv*batter,rv*batter,Vector((0,0,1))-rv*(rad*.055/78)]):
   for rr in range(3):M[rr][c]=vec[rr]
  M.translation=rv*(rad*batter)+Vector((0,0,z))
  ob=bpy.data.objects.new(f'COL124 T{tier} B{j:02d} engaged round column',masters[key]);C.objects.link(ob);ob['coliseum_role']='pier';ob['bay']=j;ob['tier']=tier;ob['feature']='round engaged shaft with torus scotia base and echinus capital';mod=ob.modifiers.new('124 Shared native column warp','NODES');mod.node_group=g
  for prefix,T in [('Auth',M),('Original',P@M),('Final',F)]:
   for suffix,value in [(str(i),tuple(T[i][k]for k in range(3)))for i in range(3)]+[('T',tuple(T.translation))]:
    socket=next(s for s in g.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'and s.name==prefix+suffix);getattr(mod.properties.inputs,socket.identifier).value=value
  added.append(ob)
  prefix=f'COL110 T{tier} B{j:02d} pier '
  for x in list(C.objects):
   if x.name.startswith(prefix)and any(s in x.name for s in ['pilaster','plinth capital','bedding joint']):removed.append(x.name);bpy.data.objects.remove(x,do_unlink=True)
 audit={'new_objects':[o.name for o in added],'removed_facing_objects':removed,'shared_meshes_by_existing_material':len(masters),'master_nonmanifold_edges':bad,'master_volume':volume,'profile_radius_height':profile,'structural_scope':'Only decorative pier pilaster, base/capital and bedding facing removed; solid pier cores, arch tunnels and projecting towers unchanged. Shaft foot heights and boundary angles fixed.','coordinates':'Shared native GeometryNodes original-world attribute with same E angular/radial warp and116 yaw.','seconds':time.time()-t}
 return added,audit
if __name__=='__main__':
 O=R/'art/studies/coliseum-124/columns';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-123/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];added,audit=apply(C);(O/'audit.json').write_text(json.dumps(audit,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
 s=bpy.context.scene;s.render.use_freestyle=False
 for o in bpy.data.objects:
  if 'Landmark contact ink'in o.name:o.hide_render=True
 s.render.resolution_x=2880;s.render.resolution_y=2164;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.37;s.render.border_max_x=.65;s.render.border_min_y=.59;s.render.border_max_y=.90;s.render.filepath=str(O/'main-crop.png');bpy.ops.render.render(write_still=True)
