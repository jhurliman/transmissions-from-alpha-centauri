"""Read-only native receiver/material graph inventory, no render or scene save."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from collections import Counter
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-164/diagnosis';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-163/scene.blend'));s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH'and(o.hide_render or any(sl.material and sl.material.use_nodes and any(n.type=='OUTPUT_MATERIAL'and n.inputs['Volume'].is_linked for n in sl.material.node_tree.nodes)for sl in o.material_slots)):o.hide_set(True)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cam=s.camera;iv=cam.calc_matrix_camera(dg,x=3840,y=2885).inverted();org=cam.matrix_world.translation
boxes={'left_core':[1450,455,1625,605],'central_core':[1930,435,2085,605],'right_contacts':[2080,540,2330,810]};rows=[];mats={}
for label,(x0,y0,x1,y1) in boxes.items():
 for y in range(y0,y1,15):
  for x in range(x0,x1,15):
   q=iv@Vector((2*x/3840-1,1-2*y/2885,-1,1));q/=q.w;di=(cam.matrix_world@q.to_3d()-org).normalized();ok,p,n,fi,ob,_=s.ray_cast(dg,org,di)
   if not ok:continue
   ev=ob.evaluated_get(dg);me=ev.to_mesh();idx=me.polygons[fi].material_index if 0<=fi<len(me.polygons)else None;mat=ob.material_slots[idx].material if idx is not None and idx<len(ob.material_slots)else None;ev.to_mesh_clear()
   rows.append({'region':label,'pixel':[x,y],'object':ob.name,'face':fi,'material':mat.name if mat else None,'world':list(p),'normal':list(n)})
   if mat:mats[mat.name]=mat
G={}
for name,m in mats.items():
 if not m.use_nodes:continue
 ns=[]
 for n in m.node_tree.nodes:
  ins=[]
  for i in n.inputs:
   val=getattr(i,'default_value',None)
   try:val=list(val)
   except TypeError:pass
   if not isinstance(val,(str,float,int,list,type(None))):val=str(val)
   ins.append({'name':i.name,'value':val,'links':[{'node':l.from_node.name,'socket':l.from_socket.name}for l in i.links]})
  z={'name':n.name,'label':n.label,'type':n.type,'inputs':ins}
  for a in ['operation','blend_type','data_type','attribute_name']:
   if hasattr(n,a):z[a]=getattr(n,a)
  if hasattr(n,'color_ramp'):z['ramp']=[{'position':v.position,'color':list(v.color)}for v in n.color_ramp.elements];z['interpolation']=n.color_ramp.interpolation
  ns.append(z)
 G[name]=ns
(O/'material-native-graphs.json').write_text(json.dumps(G,indent=2));(O/'material-receivers.json').write_text(json.dumps(rows,indent=2));print({k:Counter(r['material']for r in rows if r['region']==k)for k in boxes},flush=True)
