"""210 native uniform landmark selection study; never modifies canonical209."""
import bpy,sys,json,time,importlib
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/colosseum-scale-210'
from colosseum_scale_metrics_210 import collect,apparent_top,nearest_plan,visibility
from colosseum_scale_ink_210 import capture as ink_capture,validate as ink_validate
GUARDS=['coliseum_ink_regression_149','coliseum_foreground_visibility_156','coliseum_foreground_visibility_161','architecture_ink_visibility_192','architecture_ink_visibility_205','architecture_ink_visibility_207']

def guards(scene,embed=True):
 for module in GUARDS:importlib.import_module(module).apply(scene,embed=embed)

def apply(scene,fraction):
 report=json.loads((O/'metrics.json').read_text());C,members,dg,rows,P,T,E=collect(scene)
 ink_before=ink_capture();original_top=apparent_top(scene,P,rows)
 assert abs(original_top['pixel'][1]-report['baseline']['pixel'][1])<.01,'209 landmark differs from measured205'
 outside={o.name:o.matrix_world.copy() for o in scene.objects if o not in members}
 roots=[o for o in members if o.parent not in members];initial={o.name:o.matrix_world.copy() for o in roots}
 scale=next((v['uniform_scale']for v in report['variants'] if abs(v['sky_gap_fraction']-fraction)<1e-7),1.)
 pivot=Vector(report['pivot_world']);M=Matrix.Translation(pivot)@Matrix.Scale(scale,4)@Matrix.Translation(-pivot)
 for ob in roots:ob.matrix_world=M@initial[ob.name]
 bpy.context.view_layer.update()
 changed_outside=[n for n,m in outside.items() if max(abs(a-b)for row1,row2 in zip(m,bpy.data.objects[n].matrix_world)for a,b in zip(row1,row2))>1e-5]
 assert not changed_outside,changed_outside
 _,_,dg,rows,Q,TT,EE=collect(scene)
 assert P.shape==Q.shape
 error=float(np.max(np.abs(Q-(np.array(M)[:3,:3]@P.T).T-np.array(M)[:3,3])))
 assert error<.001,error
 top=apparent_top(scene,Q,rows);top['visibility']=visibility(scene,dg,top['world']);assert top['visibility']['visible'],top
 target=report['baseline']['pixel'][1]*(1-fraction);assert abs(top['pixel'][1]-target)<.02,(top,target)
 plan=nearest_plan(Q,EE,np.array(scene.camera.matrix_world.translation));assert abs(plan['distance']-report['anchor']['distance'])<.001
 wire_rows=[r for r in rows if any(w in r['name'].lower()for w in ['col123','wire','armature','bent','rebar'])]
 wire=None
 if wire_rows:
  ids=np.concatenate([np.arange(r['first'],r['last'])for r in wire_rows]);from colosseum_scale_metrics_210 import project
  xy=project(scene,Q);i=int(ids[np.argmin(xy[ids,1])]);wire={'object':next(r['name']for r in wire_rows if r['first']<=i<r['last']),'pixel':xy[i].tolist(),'world':Q[i].tolist()}
 ink_audit=ink_validate(ink_before,M)
 if fraction:
  from landmark_contact_visibility_210 import apply as clip_contacts
  ink_audit['external_visibility']=clip_contacts(scene)
 return {'companion_ink':ink_audit,'fraction':fraction,'scale':scale,'full4K_top':top,'full4K_top_wire':wire,'target_top_y':target,'native_members':len(members),'transform_roots':len(roots),'uniform_transform_error_m':error,'outside_objects_changed':changed_outside,'nearest_plan_distance_m':plan['distance'],'ground_z':float(Q[:,2].min()),'source':bpy.data.filepath,'approved':False}

def build(label):
 source=R/'art/studies/scene-completion-209/scene.blend';assert source.exists(),source
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 fraction={'baseline':0.,'10':.1,'20':.2,'70':.7}[label];audit=apply(s,fraction);guards(s)
 s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=50;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_compositing=True;s.render.use_freestyle=True
 # Blender render-percentage already scales Freestyle widths. Keep the source global width.
 audit['source_line_thickness']=s.render.line_thickness;audit['preview_line_thickness']=s.render.line_thickness
 s.render.filepath=str(O/label/'preview.png');dest=O/label;dest.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'));(dest/'audit.json').write_text(json.dumps(audit,indent=2));print('210 BUILT',label,flush=True)

def render(label):
 dest=O/label;bpy.ops.wm.open_mainfile(filepath=str(dest/'scene.blend'));s=bpy.context.scene;guards(s,False);start=time.time();bpy.ops.render.render(write_still=True);
 # Retain the native render result for future layer-level diagnosis.
 original_format=s.render.image_settings.file_format;original_media=s.render.image_settings.media_type
 try:
  s.render.image_settings.media_type='MULTI_LAYER_IMAGE';s.render.image_settings.file_format='OPEN_EXR_MULTILAYER';bpy.data.images['Render Result'].save_render(str(dest/'native-render.exr'),scene=s)
 finally:
  s.render.image_settings.media_type=original_media;s.render.image_settings.file_format=original_format
 (dest/'performance.json').write_text(json.dumps({'seconds':time.time()-start,'native_render':True,'guards':GUARDS},indent=2));print('210 RENDERED',label,flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:];mode,label=args
 {'build':build,'render':render}[mode](label)
