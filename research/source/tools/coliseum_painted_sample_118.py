"""118 sample: same117 palette, localized deposits/core treatment and cavity shade/ink."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/coliseum-118';sys.path.insert(0,str(R/'tools'))
from coliseum_weathering_117 import apply,exposed_core
from coliseum_depth_118 import cavity_shade
from intersection_ink_095 import add_intersection_ink,bake_intersection_ink
bpy.ops.wm.open_mainfile(filepath=str(O/'geometry-proof.blend'))
s=bpy.context.scene;C=bpy.data.collections['110 Coliseum detailed front ruin']
objects=[o for o in C.objects if o.type=='MESH']
regions=json.loads((R/'art/studies/coliseum-117/geometry-audit.json').read_text())['weathering_regions_original_world']
deposits=apply([o for o in objects if o.get('tier')==3],regions)
core=exposed_core();core_count=0
for ob in objects:
    attr=ob.data.attributes.get('117 Exposed core')
    if not attr:continue
    index=len(ob.data.materials);ob.data.materials.append(core)
    for face in ob.data.polygons:
        if attr.data[face.index].value>.5:face.material_index=index;core_count+=1
cavity=cavity_shade(objects)
mask_count=sum(sum(d.value>.5 for d in ob.data.attributes['118 Recess interior'].data)for ob in objects if ob.data.attributes.get('118 Recess interior'))
ink=add_intersection_ink(C,'118 Sample visible contact ink',radius=.025)
start=time.time();strokes=bake_intersection_ink(ink)
s.render.use_freestyle=True;s.render.line_thickness=.65;s.render.filepath=str(O/'sample-final.png')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'sample-final.blend'))
bpy.ops.render.render(write_still=True)
(O/'material-audit.json').write_text(json.dumps({'deposits':deposits,'core_faces':core_count,'cavity':cavity,'cavity_faces':mask_count,'contact_strokes':strokes,'seconds':time.time()-start},indent=2))
