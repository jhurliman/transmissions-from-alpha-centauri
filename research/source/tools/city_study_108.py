"""Complete left city depth using the approved 107C kit."""
import bpy,json,os
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-108';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-107/C/scene.blend'));s=bpy.context.scene;C=bpy.data.collections['101 Original city layout study'];audit=[]
for mid,src,x,y,sc in [('N_L3','L03',-6.4,91,.88),('N_L4','L02',-6.7,117,1.04),('N_L5','L08',-7.0,144,1.25),('N_L6','L01',-7.3,174,.87)]:
 obs=[ob for ob in list(C.objects) if ob.get('reference_mass')==src and not ob.hide_render];body=next(ob for ob in obs if 'measured crown mass' in ob.name);ox,oy=body.location.x,body.location.y
 # Meshes may have world-space vertices, so use the recorded assembly origin.
 rec=next(r for r in json.loads((R/'art/studies/city-101/A/reconstruction.json').read_text())['masses'] if r['id']==src);ox,oy=rec['position']
 xf=Matrix.Translation((x,y,0))@Matrix.Diagonal((sc,sc,sc,1))@Matrix.Translation((-ox,-oy,0))
 for ob in obs:
  q=ob.copy();q.data=ob.data.copy();C.objects.link(q);q.name='CITY108 '+mid+' '+ob.name;q.matrix_world=xf@ob.matrix_world;q['reference_mass']=mid;q['source_mass']=src
 audit.append({'id':mid,'source':src,'position':[x,y],'scale':sc})
(O/'additions.json').write_text(json.dumps(audit,indent=2));s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.use_freestyle=True;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if os.environ.get('CITY_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=520/1440;s.render.border_max_x=980/1440;s.render.border_min_y=1-505/1082;s.render.border_max_y=1-245/1082;s.render.filepath=str(O/'preview.png')
bpy.ops.render.render(write_still=True)
