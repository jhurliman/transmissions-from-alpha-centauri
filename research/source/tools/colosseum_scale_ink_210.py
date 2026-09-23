"""Coherently scale the dedicated portable-kit GP companion; no mixed road ink edits."""
import bpy,json,sys
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/colosseum-scale-210';sys.path.insert(0,str(R/'tools'))
from coliseum_contact_clip_169 import snapshot,digest
NAME='110 Landmark contact ink'

def capture():
 gp=bpy.data.objects[NAME]
 points=[gp.matrix_world@p.position for l in gp.data.layers for f in l.frames for st in f.drawing.strokes for p in st.points]
 return {'matrix':gp.matrix_world.copy(),'points':np.array([tuple(p)for p in points]),'digest':digest(snapshot(gp))}

def validate(before,M):
 gp=bpy.data.objects[NAME];after=capture();assert after['digest']==before['digest'],'GP point/curve attributes changed'
 wanted=(np.array(M)[:3,:3]@before['points'].T).T+np.array(M)[:3,3];error=float(np.max(np.abs(after['points']-wanted)));assert error<.001,error
 return {'object':NAME,'points':len(after['points']),'world_transform_error_m':error,'all_point_and_curve_attributes_unchanged':True,'attribute_sha256':after['digest'],'matrix_world':[list(row)for row in gp.matrix_world],'provenance':'188 delivery manifest portable_kit_extra_object; dedicated landmark-only GP object at scene root','mixed_096_097_ink_unchanged':True}

def fix_saved(label):
 dest=O/label;bpy.ops.wm.open_mainfile(filepath=str(dest/'scene.blend'));scene=bpy.context.scene;gp=bpy.data.objects[NAME];before=capture();assert np.max(np.abs(np.array(before['matrix'])-np.eye(4)))<1e-8,'Already scaled or unexpected companion transform'
 outside={o.name:o.matrix_world.copy() for o in scene.objects if o!=gp};other_gp={o.name:digest(snapshot(o))for o in scene.objects if o.type=='GREASEPENCIL'and o!=gp}
 metrics=json.loads((O/'metrics.json').read_text());a=json.loads((dest/'audit.json').read_text());pivot=Vector(metrics['pivot_world']);M=Matrix.Translation(pivot)@Matrix.Scale(a['scale'],4)@Matrix.Translation(-pivot);gp.matrix_world=M@before['matrix'];bpy.context.view_layer.update();report=validate(before,M)
 changed=[n for n,m in outside.items() if max(abs(x-y)for r,q in zip(m,bpy.data.objects[n].matrix_world)for x,y in zip(r,q))>1e-5];assert not changed,changed
 assert all(digest(snapshot(bpy.data.objects[n]))==d for n,d in other_gp.items())
 report['other_object_matrices_changed']=changed;report['other_GP_owners_attributes_exact']=list(other_gp);a['companion_ink']=report;a['native_members']=3532;a['transform_roots']=860
 bpy.ops.wm.save_as_mainfile(filepath=str(dest/'scene.blend'));(dest/'audit.json').write_text(json.dumps(a,indent=2));print('210 COMPANION FIXED',label,report['points'],report['world_transform_error_m'],flush=True)

if __name__=='__main__':
 for label in sys.argv[sys.argv.index('--')+1:]:fix_saved(label)
