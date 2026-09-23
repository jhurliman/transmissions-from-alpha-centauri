"""Compare actual nonlandmark geometry, camera, ink and material graphs across candidate revisions."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-116'
def digest(v):return hashlib.sha256(repr(v).encode()).hexdigest()
def value(v):
 if isinstance(v,(int,float,str,bool)):return v
 try:return tuple(v)
 except:return repr(v)
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin'];excluded=set(C.all_objects);data={};mats={}
 for o in s.objects:
  if o in excluded or o.name.startswith('110 Landmark'):continue
  d=[o.type,o.hide_render,[tuple(r) for r in o.matrix_world]]
  if o.type=='CAMERA':d.append([(k,value(getattr(o.data,k))) for k in ['type','lens','sensor_width','sensor_height','shift_x','shift_y','clip_start','clip_end','ortho_scale']])
  if o.type=='LIGHT':d.append([(k,value(getattr(o.data,k))) for k in ['type','energy','color','use_shadow']])
  if o.type=='MESH':d.extend([[(tuple(v.co)) for v in o.data.vertices],[(tuple(p.vertices),p.material_index) for p in o.data.polygons]])
  if o.type=='GREASEPENCIL':d.append([[(f.frame_number,[[(tuple(p.position),p.radius,p.opacity) for p in st.points] for st in f.drawing.strokes]) for f in l.frames] for l in o.data.layers])
  if hasattr(o.data,'materials'):
   d.append([m.name if m else None for m in o.data.materials])
   for m in o.data.materials:
    if not m or m.name in mats:continue
    md=[tuple(m.diffuse_color),m.use_nodes]
    if m.use_nodes:
     for n in m.node_tree.nodes:
      nd=[n.name,n.bl_idname,[(i.name,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]]
      for prop in ['operation','blend_type','interpolation','noise_dimensions','normalize','distribution']:
       if hasattr(n,prop):nd.append((prop,value(getattr(n,prop))))
      if hasattr(n,'color_ramp'):nd.append([(e.position,tuple(e.color)) for e in n.color_ramp.elements])
      if hasattr(n,'image') and n.image:nd.append(n.image.filepath)
      md.append(nd)
     md.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
    mats[m.name]=digest(md)
  data[o.name]=digest(d)
 if s.world and s.world.use_nodes:
  wt=s.world.node_tree
  data['__world_graph__']=digest(([(n.name,n.bl_idname,[(i.name,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in wt.nodes],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in wt.links]))
 return data,mats
x,xm=snapshot(R/'art/studies/coliseum-115/E/scene.blend');y,ym=snapshot(O/'scene.blend')
r={'baseline':'115E','candidate':'116','nonlandmark_objects_compared':len(x),'object_changes':[k for k in x if x[k]!=y.get(k)],'unexpected_objects':sorted(set(y)-set(x)),'materials_compared':len(xm),'material_graph_changes':[k for k in xm if xm[k]!=ym.get(k)]};(O/'preservation.json').write_text(json.dumps(r,indent=2));print(r)
