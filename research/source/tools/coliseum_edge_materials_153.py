import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-153/edge-diagnosis';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-150/scene.blend'));data=json.loads((O/'diagnosis-inputs.json').read_text());names=sorted(set(r['object']for r in data['rays']));rows=[]
for name in names:
 ob=bpy.data.objects.get(name)
 if not ob:continue
 mats=[]
 for sl in ob.material_slots:
  m=sl.material
  if m:mats.append({'name':m.name,'labels':[n.label for n in m.node_tree.nodes if n.label]if m.use_nodes else[],'ao_nodes':[n.name for n in m.node_tree.nodes if n.type=='AMBIENT_OCCLUSION']if m.use_nodes else[]})
 rows.append({'object':name,'materials':mats,'properties':{k:str(v)for k,v in ob.items()if not k.startswith('_')}})
gp=bpy.data.objects['110 Landmark contact ink'];(O/'materials.json').write_text(json.dumps({'receivers':rows,'gp_show_in_front':gp.show_in_front},indent=2))
