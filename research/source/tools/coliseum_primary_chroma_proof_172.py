"""Matched native before/after proof of one primary age hue correction."""
import bpy,sys,json,time,hashlib,array
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/coliseum-172/material';O.mkdir(parents=True,exist_ok=True)
src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")])
cfg=json.loads((R/'config/coliseum-primary-chroma-172.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(R/cfg['source']));s=bpy.context.scene;before=fingerprint(s);mats=material_snapshot()
C=next(c for c in bpy.data.collections if c.name=='110 Coliseum detailed front ruin' and not c.library)
def group_stamp(nt):
 return repr(([(q.name,q.bl_idname,q.label,[(v.identifier,str(v.default_value))for v in q.inputs if hasattr(v,'default_value')],getattr(q,'operation',None),getattr(q,'blend_type',None),q.node_tree.name if q.type=='GROUP' else None)for q in nt.nodes],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier)for l in nt.links]))
groups={g:group_stamp(g)for g in bpy.data.node_groups}
x0,y0,x1,y1=cfg['crop'];s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_compositing=False;s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=x0/3840;s.render.border_max_x=x1/3840;s.render.border_min_y=1-y1/2885;s.render.border_max_y=1-y0/2885
timings={}
def render(name):
 t=time.time();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True);timings[name]=time.time()-t
render('before')
from coliseum_primary_chroma_172 import apply
audit=apply(C);after=fingerprint(s);newmats=material_snapshot();changes={name:[k for k,v in row.items()if v!=after[name][k]]for name,row in before.items()if row!=after[name]}
allowed={r['object']for r in audit['assignments']};assert all(name in allowed and fields==['materials']for name,fields in changes.items()),changes
assert all(v==newmats[k]for k,v in mats.items())
assert all(v==group_stamp(g)for g,v in groups.items())
(O/'preservation.json').write_text(json.dumps({'source_objects':len(before),'only_material_slots_changed':changes,'all_native_geometry_attributes_normals_transforms_camera_lights_and_old_material_graphs_unchanged':True},indent=2)+'\n')
(O/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));render('after');(O/'performance.json').write_text(json.dumps(timings,indent=2)+'\n')
