import bpy,bmesh,math,json,random
from pathlib import Path
from mathutils import Vector
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/reviews/xenon-047';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/reviews/xenon-046/scene.blend'));s=bpy.context.scene
mainloc=s.camera.location.copy();mainrot=s.camera.rotation_euler.copy();mainlens=s.camera.data.lens
# Exact before proof uses the same camera as the candidate.
def proof(name,loc=(6,9.35,1.8),aim=(9.85,10.2,1.35),lens=44):
 s.camera.location=loc;s.camera.rotation_euler=(Vector(aim)-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.lens=lens;s.render.resolution_x=1100;s.render.resolution_y=950;s.render.use_freestyle=False;s.cycles.samples=32;s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
proof('before')
host=bpy.data.objects['right_vertical_galleries'];original=host.instance_collection;kit=bpy.data.collections.new('047 | right gallery with sheet damage');kit['clean_source']=original.name
copies={}
for old in original.objects:
 q=old.copy();kit.objects.link(q);copies[old.name]=q
host.instance_collection=kit
# Preserve current world coating; append local masks using normalized, explicit panel UVs.
def op(nt,kind,a,b=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=kind
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(float,int)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def mix(nt,fac,a,b):
 n=nt.nodes.new('ShaderNodeMixRGB');nt.links.new(fac,n.inputs[0])
 for i,v in enumerate([a,b],1):
  if isinstance(v,tuple):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def material(original,upper=False):
 m=original.copy();m.name='047 Seam loss and fastener stains '+('upper' if upper else 'lower');nt=m.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');base=bs.inputs['Base Color'].links[0].from_socket if bs.inputs['Base Color'].is_linked else tuple(bs.inputs['Base Color'].default_value)
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='DamageLocal';xyz=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],xyz.inputs[0]);x=xyz.outputs['X'];z=xyz.outputs['Y']
 noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=110;noise.inputs['Detail'].default_value=3;nt.links.new(uv.outputs[0],noise.inputs[0])
 # Interrupted wear on a selected seam; width responds to fine texture and broad quiet gaps.
 edge=op(nt,'MULTIPLY',z,1.278) if upper else op(nt,'MULTIPLY',op(nt,'SUBTRACT',1,z),1.208)
 broad=nt.nodes.new('ShaderNodeTexNoise');broad.inputs['Scale'].default_value=9;nt.links.new(uv.outputs[0],broad.inputs[0])
 width=op(nt,'ADD',.0015,op(nt,'MULTIPLY',noise.outputs['Fac'],.015));chips=op(nt,'MULTIPLY',op(nt,'LESS_THAN',edge,width),op(nt,'GREATER_THAN',broad.outputs['Fac'],.62 if upper else .57))
 # Two selected fasteners, UV anchors correspond to actual added hardware.
 anchors=[(.022,.956,.20)] if upper else [(.022,.946,.27)]
 rust=None
 for ax,az,length in anchors:
  dx=op(nt,'MULTIPLY',op(nt,'SUBTRACT',x,ax),2.778);dz=op(nt,'MULTIPLY',op(nt,'SUBTRACT',az,z),1.278 if upper else 1.208)
  radius=op(nt,'SQRT',op(nt,'ADD',op(nt,'MULTIPLY',dx,dx),op(nt,'MULTIPLY',dz,dz)))
  halo=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',radius,19)),0)
  trail=op(nt,'MULTIPLY',op(nt,'GREATER_THAN',dz,0),op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'DIVIDE',dz,length)),0))
  wander=op(nt,'MULTIPLY',op(nt,'SUBTRACT',noise.outputs['Fac'],.5),.008)
  thin=op(nt,'MAXIMUM',op(nt,'SUBTRACT',1,op(nt,'MULTIPLY',op(nt,'ABSOLUTE',op(nt,'ADD',dx,wander)),85)),0)
  rust=op(nt,'MAXIMUM',op(nt,'MULTIPLY',halo,.65),op(nt,'MULTIPLY',trail,thin))
 rust=op(nt,'MULTIPLY',rust,op(nt,'MULTIPLY',noise.outputs['Fac'],.8))
 base=mix(nt,rust,base,(.125,.046,.018,1));base=mix(nt,chips,base,(.055,.048,.044,1));nt.links.new(base,bs.inputs['Base Color'])
 nt.links.new(op(nt,'ADD',.76,op(nt,'MULTIPLY',rust,.2)),bs.inputs['Roughness'])
 return m
bounds={};changed=[]
for nm,upper in [('Gallery base panel.012',False),('Gallery base panel.013',True)]:
 q=copies[nm];q.data=q.data.copy();xmin,xmax=[f(v.co.x for v in q.data.vertices) for f in (min,max)];zmin,zmax=[f(v.co.z for v in q.data.vertices) for f in (min,max)];bounds[nm]=(xmin,xmax,zmin,zmax)
 mat=material(q.data.materials[0],upper)
 if not upper:
  # Open-backed folded tray: continuous front and returns, solidified as thin metal.
  nx,nz=44,24;vs=[]
  def bend(x,z):return -.085*max(0,1-(xmax-x)/.36-(zmax-z)/.32)
  for j in range(nz+1):
   for i in range(nx+1):
    x=xmin+(xmax-xmin)*i/nx;z=zmin+(zmax-zmin)*j/nz;vs.append((x,.35,z))
  fs=[]
  for j in range(nz):
   for i in range(nx):a=j*(nx+1)+i;fs.append((a,a+1,a+nx+2,a+nx+1))
  rim=list(range(nx+1))+[j*(nx+1)+nx for j in range(1,nz+1)]+[nz*(nx+1)+i for i in range(nx-1,-1,-1)]+[j*(nx+1) for j in range(nz-1,0,-1)]
  back=[]
  for a in rim:x,y,z=vs[a];back.append(len(vs));vs.append((x,.43,z))
  for i,a in enumerate(rim):b=(i+1)%len(rim);fs.append((a,back[i],back[b],rim[b]))
  me=bpy.data.meshes.new('047 continuous thin folded tray');me.from_pydata(vs,[],fs);me.update();q.data=me
  # Cut the grid at the exact crease before deforming; every resulting face remains planar.
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=Vector((xmax-.36,0,zmax)),plane_no=Vector((1/.36,0,1/.32)),dist=1e-7)
  for v in bm.verts:v.co.y+=bend(v.co.x,v.co.z)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  q.modifiers.clear();solid=q.modifiers.new('Six millimeter folded sheet','SOLIDIFY');solid.thickness=.006;solid.offset=1
  bevel=q.modifiers.new('Fold edge catchlight','BEVEL');bevel.width=.0015;bevel.segments=2
 q.data.materials.clear();q.data.materials.append(mat)
 uv=q.data.uv_layers.new(name='DamageLocal')
 for face in q.data.polygons:
  for idx in face.loop_indices:
   v=q.data.vertices[q.data.loops[idx].vertex_index].co;uv.data[idx].uv=((v.x-xmin)/(xmax-xmin),(v.z-zmin)/(zmax-zmin))
 changed.append(q)
# Hardware and empty screw bore share the same native module coordinates.
steel=bpy.data.materials.new('047 dark weathered fixing');steel.diffuse_color=(.075,.068,.06,1);steel.use_nodes=True;bs=steel.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=steel.diffuse_color;bs.inputs['Metallic'].default_value=.55;bs.inputs['Roughness'].default_value=.65
for nm,(xmin,xmax,zmin,zmax) in bounds.items():
 for side,x in enumerate([xmin+.061,xmax-.061]):
  for top,z in enumerate([zmin+.065,zmax-.065]):
   missing=nm.endswith('012') and side==1 and top==1
   y=.35+(-.085*max(0,1-(xmax-x)/.36-(zmax-z)/.32) if nm.endswith('012') else 0)
   bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.011 if missing else .018,depth=.02,location=(x,y-.006,z),rotation=(math.pi/2,0,0));bolt=bpy.context.object
   for c in list(bolt.users_collection):c.objects.unlink(bolt)
   kit.objects.link(bolt);bolt.name='047 empty fixing bore' if missing else '047 captive panel fixing';bolt.data.materials.append(steel)
   if missing:
    # Bore cuts the thin front only; hidden cutter preserves editability.
    bolt.hide_render=True;panel=copies['Gallery base panel.012'];mod=panel.modifiers.new('Missing fixing bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=bolt
   else:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y-.017,z));slot=bpy.context.object
    for c in list(slot.users_collection):c.objects.unlink(slot)
    kit.objects.link(slot);slot.name='047 fixing slot';slot.scale=(.016,.0015,.003);slot.data.materials.append(bpy.data.materials['Recess | dark backing'])
# Geometry audit includes the evaluated tray after the missing-fixing cut.
bpy.context.view_layer.update();audit=[]
for q in changed:
 me=bpy.data.meshes.new_from_object(q.evaluated_get(bpy.context.evaluated_depsgraph_get()));bm=bmesh.new();bm.from_mesh(me);me.calc_loop_triangles();entry={'panel':q.name,'triangles':len(me.loop_triangles),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume':bm.calc_volume()};audit.append(entry);assert entry['non_manifold_edges']==0 and abs(entry['volume'])>0,entry;bm.free()
(O/'audit.json').write_text(json.dumps({'panels':audit,'scope':'One ground-level bay, two panels; existing coating retained','missing_fixings':1,'added_fixings':7,'corner_lift_m':.085,'sheet_thickness_m':.006},indent=2))
s.camera.location=mainloc;s.camera.rotation_euler=mainrot;s.camera.data.lens=mainlens;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.use_freestyle=True;s.render.filepath=str(O/'render.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
proof('panel-detail');proof('corner-detail',(8.3,9.8,1.75),(9.82,8.94,1.3),60)
s.camera.location=mainloc;s.camera.rotation_euler=mainrot;s.camera.data.lens=mainlens;s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.use_freestyle=True;s.render.filepath=str(O/'render.png');bpy.ops.render.render(write_still=True)
