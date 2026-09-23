"""Exact scene preservation check for material-only128."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
# Reuse the expanded127 validator definitions, excluding its execution block.
source=(R/'tools/coliseum_validate_127.py').read_text().split("before,bm=snapshot(")[0];exec(source)
def landmark_geometry():
 rows={}
 for ob in bpy.data.collections['110 Coliseum detailed front ruin'].all_objects:
  d=[ob.type,[tuple(r)for r in ob.matrix_world],ob.hide_render]
  if ob.type=='MESH':
   d += [[tuple(v.co)for v in ob.data.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth)for p in ob.data.polygons]]
   for at in ob.data.attributes:
    if at.name.startswith('.') or at.data_type not in ['FLOAT','FLOAT_VECTOR','INT','BOOLEAN']:continue
    d.append([at.name,at.domain,at.data_type,[tuple(a.vector)if hasattr(a,'vector')else a.value for a in at.data]])
   d.append([(m.name,m.type,m.show_render,m.node_group.name if m.type=='NODES'and m.node_group else None)for m in ob.modifiers])
  rows[ob.name]=digest(d)
 return rows
before,bm=snapshot(R/'art/studies/coliseum-127/scene.blend');bg=cloud_geometry();bw=protected_world();bp=selected_pipe_dimensions();bl=landmark_geometry();lights={o.name:digest([o.data.type,o.data.energy,tuple(o.data.color),[tuple(r)for r in o.matrix_world]])for o in bpy.context.scene.objects if o.type=='LIGHT'}
after,am=snapshot(R/'art/studies/coliseum-128/scene.blend');ag=cloud_geometry();aw=protected_world();ap=selected_pipe_dimensions();al=landmark_geometry();lights2={o.name:digest([o.data.type,o.data.energy,tuple(o.data.color),[tuple(r)for r in o.matrix_world]])for o in bpy.context.scene.objects if o.type=='LIGHT'}
a={'source':'127','candidate':'128','nonlandmark_objects_compared':len(before),'changed_nonlandmark_objects':[k for k,v in before.items()if after.get(k)!=v],'added_nonlandmark_objects':sorted(set(after)-set(before)),'changed_nonlandmark_materials':[k for k,v in bm.items()if am.get(k)!=v],'added_nonlandmark_materials':sorted(set(am)-set(bm)),'changed_landmark_geometry_or_transforms':[k for k,v in bl.items()if al.get(k)!=v],'added_landmark_objects':sorted(set(al)-set(bl)),'clouds_unchanged':bg==ag,'world_unchanged':bw==aw,'lights_unchanged':lights==lights2,'pipe_unchanged':bp==ap,'landmark_objects_compared':len(bl),'scope':'Only object-linked landmark material graphs are changed; all geometry, ink, scene lights, world and nonlandmark materials fixed.'}
(R/'art/studies/coliseum-128/preservation.json').write_text(json.dumps(a,indent=2));assert all(not a[k]for k in ['changed_nonlandmark_objects','added_nonlandmark_objects','changed_nonlandmark_materials','added_nonlandmark_materials','changed_landmark_geometry_or_transforms','added_landmark_objects']);assert all(a[k]for k in ['clouds_unchanged','world_unchanged','lights_unchanged','pipe_unchanged']);print(json.dumps(a))
