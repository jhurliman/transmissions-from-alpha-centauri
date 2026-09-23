"""Only increase fine splatter coverage in the existing146 native scenes."""
import bpy,sys,json,time,array,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];scope='actual' if 'actual' in sys.argv else 'combined';O=R/f'art/studies/alley-weathering-147/{scope}';O.mkdir(parents=True,exist_ok=True)
if 'render' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene
else:
 bpy.ops.wm.open_mainfile(filepath=str(R/f'art/studies/alley-weathering-146/{scope}/scene.blend'));s=bpy.context.scene
 src=(R/'tools/scene_integration_138.py').read_text();exec(src[src.index('def objects('):src.index("if 'render' not in sys.argv:")]);before=fingerprint(s);cal=json.loads((O.parent/'coverage-calibration.json').read_text())['coverage'];cache={};edits=[]
 for ob in objects(s):
  for slot in ob.material_slots:
   m=slot.material
   if not m or not m.node_tree or not any(n.label=='146 Broad fields plus bottom-weighted fine splotches' for n in m.node_tree.nodes):continue
   if m not in cache:
    new=m.copy();new.name='147 Bottom splatter3x | '+m.name;count=0
    for n in new.node_tree.nodes:
     if n.type!='MAP_RANGE':continue
     for name,item in cal.items():
      a,b=item['old_thresholds']
      if abs(n.inputs['From Min'].default_value-a)<1e-6 and abs(n.inputs['From Max'].default_value-b)<1e-6:
       n.inputs['From Min'].default_value,n.inputs['From Max'].default_value=item['new_thresholds'];n.label='147 Fine splatter3x '+name;count+=1
    assert count==2,(m.name,count);new['147 fine_splatter_coverage_multiplier']=3.;cache[m]=new
   slot.link='OBJECT';slot.material=cache[m];edits.append(ob.name)
 assert edits
 after=fingerprint(s);assert set(before)==set(after);changes={k:[f for f in v if v[f]!=after[k][f]]for k,v in before.items()if v!=after[k]};assert all(fields==['materials']for fields in changes.values()),changes
 (O/'preservation.json').write_text(json.dumps({'source_iteration':146,'only_material_assignments_changed':changes,'geometry_normals_camera_lights_transforms_identical':True,'changed_private_materials':len(cache),'splatter_coverage_multiplier':3},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
 if scope=='combined':
  cols={bpy.data.collections[n]for n in ['145 Alley damage panel study','145 Panel detail layers','145 Clean panel master | asset']};bpy.data.libraries.write(str(O/'panel-kit.blend'),cols,fake_user=True)
filename='main-4k.png'if scope=='actual'else'combined-4k.png';s.render.filepath=str(O/filename);t=time.time();bpy.ops.render.render(write_still=True);(O/'performance.json').write_text(json.dumps({'seconds':time.time()-t,'resolution':[s.render.resolution_x,s.render.resolution_y]},indent=2))
