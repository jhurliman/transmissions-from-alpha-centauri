import bpy,json,sys,collections
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));from coliseum_contact_clip_169 import snapshot,digest
O=R/'art/studies/coliseum-186';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-173/scene.blend'));s=bpy.context.scene
for ob in s.objects:
 if ob.hide_render or (ob.type=='MESH' and any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in ob.material_slots)):ob.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();origin=cam.matrix_world.translation;rows=[];cache={};faces={}
for y in range(600,645):
 for x in range(2135,2170):
  q=iv@Vector((2*(x+.5)/3840-1,1-2*(y+.5)/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-origin).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,origin,di)
  if not ok:continue
  if ob.name not in cache:
   ev=ob.evaluated_get(dg);cache[ob.name]=(ev,ev.to_mesh())
  me=cache[ob.name][1];f=me.polygons[fi];mat=ob.material_slots[f.material_index].material;key=f'{ob.name}:{fi}';rows.append({'pixel':[x,y],'object':ob.name,'face':fi,'material':mat.name if mat else None,'slot':f.material_index,'world':list(p),'normal':list(n)})
  if key not in faces:faces[key]={'object':ob.name,'face':fi,'material':mat.name if mat else None,'slot':f.material_index,'normal':list(n),'vertices_world':[list(ob.matrix_world@me.vertices[i].co)for i in f.vertices],'pixels':[]}
  faces[key]['pixels'].append([x,y])
gp=bpy.data.objects['110 Landmark contact ink'];snap=snapshot(gp);strokes=[]
for rec in snap:
 for idx,st in enumerate(rec['strokes']):
  points=[gp.matrix_world@Vector(p)for p in st['point']['position']];uv=[world_to_camera_view(s,cam,p)for p in points];xy=[(p.x*3840,(1-p.y)*2885)for p in uv];segments=[]
  for i,(a,b)in enumerate(zip(xy,xy[1:])):
   if max(a[0],b[0])<2135 or min(a[0],b[0])>2170 or max(a[1],b[1])<600 or min(a[1],b[1])>645:continue
   segments.append({'segment':i,'pixel_endpoints':[a,b],'world_endpoints':[list(points[i]),list(points[i+1])]})
  if segments:strokes.append({'layer':rec['layer'],'frame':rec['frame'],'stroke':idx,'segments':segments})
counts=collections.Counter(r['object']for r in rows);summary=[{'object':n,'pixels':c,'materials':dict(collections.Counter(r['material']for r in rows if r['object']==n))}for n,c in counts.most_common()]
(O/'ownership.json').write_text(json.dumps({'source':'173','roi':[2135,600,2170,645],'rays':rows,'faces':list(faces.values()),'summary':summary,'gp_projected_segments':strokes,'gp_digest':digest(snap),'limitations':'Pixel-center first-hit solid surfaces; GP segment bounding overlap is inventory only, not rendered coverage or visibility certificate. Freestyle not raycast.'},indent=2));print(summary)
