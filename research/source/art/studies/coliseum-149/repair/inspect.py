import bpy,sys,json
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri');sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
from coliseum_crown_repair_123 import topology,strict_crossings
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-148/scene.blend'))
_,_,unpack=mapping();out=[]
for name in ['COL110 U9 aperture head','COL110 U9 fractured upper wall R']:
 o=bpy.data.objects[name];me=bpy.data.meshes.new_from_object(o.evaluated_get(bpy.context.evaluated_depsgraph_get()),depsgraph=bpy.context.evaluated_depsgraph_get());t=bpy.data.objects.new('inspect',me);t.matrix_world=o.matrix_world;me.calc_loop_triangles();coords=[list(unpack(o.matrix_world@v.co))for v in me.vertices];pairs=strict_crossings(t,True);tris=[list(p.vertices)for p in me.loop_triangles];ids=sorted(set(i for pair in pairs for i in pair));types={}
 for i in ids:
  rs=[coords[v][0]for v in tris[i]];kind='front'if min(rs)>74.9 else'rear'if max(rs)<67.1 else'return';types[kind]=types.get(kind,0)+1
 d={'name':name,'modifiers':[(m.name,m.type)for m in o.modifiers],'topology':topology(t),'crossing_face_classes':types,'verts':coords,'local':[list(v.co)for v in me.vertices],'tris':tris,'pairs':pairs,'attributes':[(a.name,a.domain,a.data_type)for a in me.attributes]};out.append(d);bpy.data.objects.remove(t)
(R/'art/studies/coliseum-149/repair/current-source.json').write_text(json.dumps(out));print('DIAG',[(d['name'],d['modifiers'],d['topology'],d['crossing_face_classes'])for d in out])
