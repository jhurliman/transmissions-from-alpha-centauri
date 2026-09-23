import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-102'
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;out={};body={}
 for ob in s.objects:
  if ob.get('reference_mass'):
   if 'measured crown mass' in ob.name or 'low single-story block' in ob.name:
    body[ob.name]=(list(sum((list(row) for row in ob.matrix_world),[])),[(tuple(v.co)) for v in ob.data.vertices])
   continue
  if ob.name.startswith('CITY102 '):continue
  data=[ob.type,ob.hide_render,list(sum((list(row) for row in ob.matrix_world),[]))]
  if ob.type=='MESH':data+=[[(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[m.name if m else None for m in ob.data.materials]]
  if ob.type=='GREASEPENCIL':data+=[[(layer.name,[(f.frame_number,[[tuple(p.position) for p in st.points] for st in f.drawing.strokes]) for f in layer.frames]) for layer in ob.data.layers]]
  out[ob.name]=hashlib.sha256(repr(data).encode()).hexdigest()
 return out,body
before,bodies_a=snapshot(R/'art/studies/city-101/A/scene.blend');after,bodies_b=snapshot(O/'scene.blend');changes=[k for k in before if before[k]!=after.get(k)];result={'noncity_objects_compared':len(before),'noncity_changes':changes,'selected_body_count':len(bodies_a),'selected_body_vertices_and_transforms_unchanged':bodies_a==bodies_b,'extra_noncity_objects':sorted(set(after)-set(before))};(O/'preservation.json').write_text(json.dumps(result,indent=2));print('PRESERVATION',result)
