"""232: camera-verified broken-wall face erosion and structured mineral scuffs."""
import bpy,bmesh,json,sys,random,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/broken-walls-232';sys.path.insert(0,str(R/'tools'))

def finish(old):
 m=old.copy();m.name='232 Heavy fractured mineral | '+old.name;n=m.node_tree.nodes;l=m.node_tree.links
 em=next(x for x in n if x.type=='EMISSION' and x.inputs['Color'].is_linked)
 # Start from the retained source lighting/palette, bypassing230's cloudy multiplication.
 source=next((x.outputs[0]for x in n if x.type=='GROUP'and x.node_tree and x.node_tree.name.startswith('204 Half')),em.inputs['Color'].links[0].from_socket)
 def mathn(code,a,b):
  q=n.new('ShaderNodeMath');q.operation=code
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def ramp(v,a,b):
  q=n.new('ShaderNodeMapRange');q.clamp=True;l.new(v,q.inputs[0]);q.inputs[1].default_value=a;q.inputs[2].default_value=b;return q.outputs[0]
 def mix(f,a,b,op='MIX'):
  q=n.new('ShaderNodeMixRGB');q.blend_type=op
  for i,v in enumerate((f,a,b)):
   if isinstance(v,(int,float,tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 geo=n.new('ShaderNodeNewGeometry');p=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],p.inputs[0]);norm=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Normal'],norm.inputs[0]);useY=mathn('GREATER_THAN',mathn('ABSOLUTE',norm.outputs['X'],0),.6)
 u=mathn('ADD',mathn('MULTIPLY',useY,p.outputs['Y']),mathn('MULTIPLY',mathn('SUBTRACT',1,useY),p.outputs['X']))
 def coords(su,sz):
  q=n.new('ShaderNodeCombineXYZ');l.new(mathn('MULTIPLY',u,su),q.inputs['X']);l.new(mathn('MULTIPLY',p.outputs['Z'],sz),q.inputs['Y']);return q.outputs[0]
 def noise(su,sz):
  q=n.new('ShaderNodeTexNoise');q.inputs['Scale'].default_value=1;q.inputs['Detail'].default_value=2.5;q.inputs['Roughness'].default_value=.8;l.new(coords(su,sz),q.inputs['Vector']);return q.outputs['Fac']
 def cells(su,sz,threshold):
  q=n.new('ShaderNodeTexVoronoi');q.voronoi_dimensions='2D';q.distance='EUCLIDEAN';q.inputs['Scale'].default_value=1;l.new(coords(su,sz),q.inputs['Vector']);return mathn('LESS_THAN',q.outputs['Distance'],threshold)
 # Sharp broken coating islands, with ragged medium/fine boundary rather than a soft cloud wash.
 mid=noise(4.2,4.2);fine=noise(23,23);field=mathn('ADD',mid,mathn('MULTIPLY',fine,.17))
 flake=ramp(field,.57,.61);rim=mathn('MULTIPLY',ramp(field,.53,.55),mathn('SUBTRACT',1,flake))
 body=mix(mathn('MULTIPLY',flake,.72),source,mix(1,source,(.59,.64,.70,1),'MULTIPLY'))
 body=mix(mathn('MULTIPLY',rim,.7),body,mix(1,source,(1.53,1.42,1.24,1),'MULTIPLY'))
 basal=mathn('SUBTRACT',1,ramp(p.outputs['Z'],.15,2.7));density=mathn('ADD',.28,mathn('MULTIPLY',basal,.65))
 gashes=mathn('MULTIPLY',cells(5,32,.19),ramp(noise(.9,.9),.40,.55));dots=cells(21,23,.13)
 body=mix(mathn('MULTIPLY',mathn('MAXIMUM',gashes,mathn('MULTIPLY',dots,.7)),density),body,(.018,.015,.023,1))
 rain=mathn('MULTIPLY',ramp(noise(17,.36),.59,.67),ramp(noise(1.2,1.8),.39,.60))
 body=mix(mathn('MULTIPLY',rain,.58),body,mix(1,source,(.46,.43,.43,1),'MULTIPLY'))
 grit=mathn('MULTIPLY',cells(12,16,.20),basal);body=mix(mathn('MULTIPLY',grit,.38),body,mix(1,source,(1.60,1.48,1.29,1),'MULTIPLY'))
 l.new(body,em.inputs['Color']);m['232 heavy mineral']=True;return m

def camera_samples(scene,names):
 from landmark_contact_visibility_210 import external_tree
 tree,owners,info=external_tree(scene);cam=scene.camera;origin=cam.matrix_world.translation;frame=cam.data.view_frame(scene=scene);loX=min(p.x for p in frame);hiX=max(p.x for p in frame);loY=min(p.y for p in frame);hiY=max(p.y for p in frame);z=frame[0].z;rot=cam.matrix_world.to_3x3();samples={name:[]for name in names}
 for py in range(820,1435,10):
  for px in range(1110,2810,10):
   d=rot@Vector((loX+(hiX-loX)*px/3840,hiY-(hiY-loY)*py/2885,z));hit=tree.ray_cast(origin,d.normalized(),150)
   if hit[0] is not None and owners[hit[2]] in samples:samples[owners[hit[2]]].append({'point':list(hit[0]),'normal':list(hit[1]),'pixel':[px,py]})
 return samples,{'grid_full4k':[1110,820,2810,1435],'step_px':10,'opaque_triangles':info['triangles'],'atmosphere_ignored':True}

def profile(rng,w,h):
 # Unequal jagged boundaries of one connected peeled strip, deliberately nonradial.
 zs=[-.5,-.32,-.09,.13,.30,.5];left=[(-rng.uniform(.18,.50)*w,z*h)for z in zs];right=[(rng.uniform(.16,.50)*w,z*h)for z in reversed(zs)]
 return left+right

def apply(scene):
 from city_transition_refinement_200 import _cut,_closed,_mesh_digest
 targets=[o for o in bpy.data.collections['133 Ruined transition structures'].objects if o.get('230 weathered')];assert len(targets)==21
 before={o.name:(o.data,tuple(v for r in o.matrix_world for v in r),tuple(sl.material for sl in o.material_slots))for o in bpy.data.objects if o.type=='MESH'}
 samples,probe=camera_samples(scene,{o.name for o in targets});cache={};rows=[]
 for ob in targets:
  mats=[sl.material for sl in ob.material_slots];indices=[p.material_index for p in ob.data.polygons];ob.data=ob.data.copy();ob.data.materials.clear()
  for old in mats:
   if old not in cache:cache[old]=finish(old)
   ob.data.materials.append(cache[old])
  for sl in ob.material_slots:sl.link='DATA'
  for p,i in zip(ob.data.polygons,indices):p.material_index=i
  pts=samples[ob.name];rng=random.Random(23200+sum(map(ord,ob.name)));features=[];selected=[]
  core=ob.material_slots[0].material
  if len(pts)>10:
   # Edge emphasis from visible silhouette neighbourhood, plus a few connected interior losses.
   pixels={tuple(p['pixel'])for p in pts}
   ranked=sorted(pts,key=lambda p:(-sum((p['pixel'][0]+dx,p['pixel'][1]+dy)not in pixels for dx,dy in [(-20,0),(20,0),(0,-20),(0,20)]),rng.random()))
   for sample in ranked:
    q=Vector(sample['point']);n=Vector(sample['normal'])
    if q.z<.35 or abs(n.z)>.3 or any((q-p).length<.62 for p in selected):continue
    selected.append(q);w=rng.uniform(.35,.80);h=rng.uniform(.60,1.45)
    features.append(_cut(ob,q,n,profile(rng,w,h),rng.uniform(.025,.055),'232 ragged connected shallow mineral loss',core))
    if len(selected)>=min(10,3+len(pts)//45):break
   for sample in ranked[::max(1,len(ranked)//4)][:3]:
    q=Vector(sample['point']);n=Vector(sample['normal'])
    if q.z<.7 or abs(n.z)>.3:continue
    p=[(-.012,.56),(.040,.33),(.018,.15),(.073,-.07),(.014,-.61),(-.010,-.34),(-.046,-.13),(-.019,.12),(-.035,.31)]
    features.append(_cut(ob,q,n,p,.023,'232 irregular downward crack',core))
  health=_closed(ob);assert health['nonmanifold_edges']==0,(ob.name,health)
  rows.append({'object':ob.name,'verified_visible_grid_hits':len(pts),'projected_bounds':([min(p['pixel'][0]for p in pts),min(p['pixel'][1]for p in pts),max(p['pixel'][0]for p in pts),max(p['pixel'][1]for p in pts)]if pts else None),'native_features':features,'health':health})
 names={o.name for o in targets}
 for name,(mesh,M,mats)in before.items():
  ob=bpy.data.objects[name];assert tuple(v for r in ob.matrix_world for v in r)==M
  if name not in names:assert ob.data==mesh and tuple(sl.material for sl in ob.material_slots)==mats,name
 return {'study':232,'source':'midground-arches-231','grid_probe':probe,'rows':rows,'native_features':sum(len(r['native_features'])for r in rows),'material_objects':len(targets),'private_materials':len(cache),'all_unrelated_geometry_bindings_transforms_exact':True,'ink':'Retain successful230 atmosphere-free visible contours','references':['UCL-01','UCL-02','DP-03'],'status':'Actual combined native proof pending; no score'}

if __name__=='__main__':
 O.mkdir(exist_ok=True,parents=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/midground-arches-231/scene.blend'));a=apply(bpy.context.scene);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));print('232 WALL READY',a['native_features'],flush=True)
