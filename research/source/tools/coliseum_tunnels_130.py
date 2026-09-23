"""User130: two open barrel-vault corridors behind actual T0 B8/B9 rear rims.
World-metre paths, parallel straight runs and diverging90degree exits. No backdrop planes.
"""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping

def apply(C,length=30.,bend_radius=6.,outlet_length=5.,wall_thickness=.65,roof_extra=.65,bays=(8,9)):
 if length<=2 or outlet_length<=0 or wall_thickness<=0:raise ValueError('Positive physical dimensions required')
 if any(o.get('130 barrel tunnel') for o in C.objects):raise RuntimeError('Tunnels already present; use fresh source')
 _,_,unpack=mapping();wall=bpy.data.objects['COL127 T0 continuous arcade wall'];dg=bpy.context.evaluated_depsgraph_get();ev=wall.evaluated_get(dg);me=ev.to_mesh();at=me.attributes.get('115 Original world position');rows=[];objects=[]
 # Existing back-return material carries real diffuse/AO, violet shadow palette and actual-depth parameter.
 source=next(slot.material for slot in wall.material_slots if slot.material and 'Two-depth interior' in slot.material.name)
 mat=source.copy();mat.name='130 Native deep-violet tunnel masonry';mat['130 tunnel material']=True
 floor_source=next(o for o in C.objects if o.get('125 inset platform') and int(o.get('tier',-1))==0 and int(o.get('bay',-1))==8).material_slots[0].material
 floor_mat=floor_source.copy();floor_mat.name='130 Native tunnel threshold floor'
 for bay,turn in zip(bays,[-1,1]):
  ac=-math.pi+(bay+.5)*math.tau/36;platform=next(o for o in C.objects if o.get('125 inset platform') and int(o.get('tier',-1))==0 and int(o.get('bay',-1))==bay);floor_z=3.08+float(platform['platform authored height']);curve=[];bottom=[]
  for v in wall.data.vertices:
   rr,aa,z=unpack(wall.matrix_world@v.co);u=(aa-ac)*75
   if abs(rr-67)>.004 or abs(u)>3.01:continue
   w=ev.matrix_world@me.vertices[v.index].co;attr=at.data[v.index].vector.copy()
   if 13<z<18.2:curve.append((u,z,w,attr,v.index))
   if abs(z-3.08)<.002 and abs(abs(u)-2.9154717)<.025:bottom.append((u,z,w,attr,v.index))
  curve.sort(key=lambda q:q[0]);bottom.sort(key=lambda q:q[0])
  if len(curve)!=25 or len(bottom)!=2:raise RuntimeError('Unexpected actual rear opening '+str((bay,len(curve),len(bottom))))
  lf=[]
  for low,high in [(bottom[0],curve[0]),(bottom[-1],curve[-1])]:
   t=(floor_z-low[1])/(high[1]-low[1]);lf.append((low[2].lerp(high[2],t),low[3].lerp(high[3],t)))
  # Clockwise section in worldX/Z: left floor, actual25point roof, right floor.
  inner=[lf[0][0]]+[q[2] for q in curve]+[lf[1][0]];attrs=[lf[0][1]]+[q[3]for q in curve]+[lf[1][1]];center=(lf[0][0]+lf[1][0])*.5
  offsets=[p-center for p in inner];width=max(p.x for p in offsets)-min(p.x for p in offsets)
  if bend_radius<=width*.5+wall_thickness:raise ValueError('Bend radius too tight for clear section')
  # Convex polygon offset in X/Z; end annuli leave the full walkable cross-section open.
  outer=[]
  for i,p in enumerate(offsets):
   prev=offsets[(i-1)%len(offsets)];nxt=offsets[(i+1)%len(offsets)];a=Vector((p.x-prev.x,p.z-prev.z)).normalized();b=Vector((nxt.x-p.x,nxt.z-p.z)).normalized();na=Vector((-a.y,a.x));nb=Vector((-b.y,b.x));bis=(na+nb).normalized();scale=(wall_thickness+roof_extra*max(0.,bis.y))/max(.25,bis.dot(na));outer.append(p+Vector((bis.x*scale,0,bis.y*scale)))
  # Negative first station embeds0.12m into actual rear wall; requested straight run stays exactly30m from rear rim.
  stations=[(-.12,Vector((0,-.12,0)),0.)]
  for k in range(16):stations.append((length*k/15,Vector((0,length*k/15,0)),0.))
  for k in range(1,25):
   a=math.pi*.5*k/24;s=length+bend_radius*a;stations.append((s,Vector((turn*bend_radius*(1-math.cos(a)),length+bend_radius*math.sin(a),0)), -turn*a))
  for k in range(1,5):
   run=outlet_length*k/4;s=length+bend_radius*math.pi*.5+run;stations.append((s,Vector((turn*(bend_radius+run),length+bend_radius,0)),-turn*math.pi*.5))
  verts=[];orig=[];count=len(inner)
  for distance,delta,angle in stations:
   rot=Matrix.Rotation(angle,3,'Z')
   for outline in [offsets,outer]:
    for i,p in enumerate(outline):
     w=center+delta+rot@p;verts.append(w);orig.append(attrs[i]+(w-inner[i])/.715)
  faces=[];mats=[]
  for k in range(len(stations)-1):
   for layer in range(2):
    for i in range(count):
     j=(i+1)%count;a=k*count*2+layer*count+i;b=k*count*2+layer*count+j;c=(k+1)*count*2+layer*count+j;d=(k+1)*count*2+layer*count+i;faces.append((a,b,c,d));mats.append(1 if i==count-1 else 0)
  for k in [0,len(stations)-1]:
   for i in range(count):j=(i+1)%count;off=k*count*2;faces.append((off+i,off+j,off+count+j,off+count+i));mats.append(0)
  mesh=bpy.data.meshes.new(f'130 B{bay} closed solid barrel walls');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat);mesh.materials.append(floor_mat)
  for f,i in zip(mesh.polygons,mats):f.material_index=i
  attr=mesh.attributes.new('115 Original world position','FLOAT_VECTOR','POINT');depth=mesh.attributes.new('120 Actual arch tunnel depth','FLOAT','POINT')
  for a,v,d in zip(attr.data,orig,depth.data):a.vector=v;d.value=1.
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume();bm.to_mesh(mesh);bm.free()
  if bad or vol<=0:raise RuntimeError('Invalid solid tunnel'+str((bad,vol)))
  ob=bpy.data.objects.new(f'COL130 T0 B{bay:02d} open bent barrel tunnel',mesh);C.objects.link(ob);ob['130 barrel tunnel']=True;ob['tier']=0;ob['bay']=bay;ob['coliseum_role']='tunnel';objects.append(ob)
  rows.append({'object':ob.name,'bay':bay,'turn':'left'if turn<0 else'right','rear_center_world':list(center),'rear_curve_source_vertex_indices':[q[4]for q in curve],'rim_match_world_max_error':0.,'connection_overlap_m':.12,'floor_authored_z':floor_z,'floor_rear_world_z_range':[lf[0][0].z,lf[1][0].z],'clear_width_world_x_m':width,'straight_centerline_m':length,'bend_radius_m':bend_radius,'bend_angle_degrees':90,'bend_centerline_m':bend_radius*math.pi/2,'exit_centerline_m':outlet_length,'total_centerline_m':length+bend_radius*math.pi/2+outlet_length,'open_exit_center_world':list(center+stations[-1][1]),'closed_solid_nonmanifold_edges':bad,'solid_volume':vol,'cross_section_points':count,'path_stations':len(stations)})
 ev.to_mesh_clear()
 return {'objects':rows,'configuration':{'length':length,'bend_radius':bend_radius,'outlet_length':outlet_length,'wall_thickness':wall_thickness,'roof_extra':roof_extra},'method':'Actual evaluated rear-rim curve; parallel+Yworldmetre paths then diverging90degree bends; closed solid shell with open end annuli.','existing_geometry_materials_changed':False,'material_source':source.name,'original_position_attribute':True,'arch_depth_attribute':1.0,'selection':'T0B8/B9 maincamera visible; T0B7partialsliver checked by separate ray audit.'}
