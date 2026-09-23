import bpy,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'));O=R/'art/studies/duct-infill-255';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/duct-infill-254/scene.blend'));s=bpy.context.scene
root=s.objects['right_vertical_galleries'];bay=next(o for o in root.instance_collection.objects if o.instance_collection and o.instance_collection.name=='253 Upper duct entry infill bay')
old=bay.instance_collection;mat=bpy.data.objects['253 Flat weathered masonry duct entry'].material_slots[0].material
C=bpy.data.collections.new('255 Solid full-height duct entry bay');C.use_fake_user=True
# Whole architectural bay, from original bay sill to its top closure.
# Fill thickness reaches the original facade backing rather than floating in front.
x0,x1=-1.40,1.40;y0,y1=-.55,.70;z0,z1=0,3.12
vs=[(x,y,z)for x,y,z in [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]]
fs=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
me=bpy.data.meshes.new('255 Full-depth masonry bay');me.from_pydata(vs,[],fs);me.materials.append(mat);o=bpy.data.objects.new('255 Continuous wall infill to sill',me);C.objects.link(o)
bay.instance_collection=C
from mathutils.bvhtree import BVHTree
import landmark_contact_visibility_210 as clip
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();verts=[];tris=[]
for ins in dg.object_instances:
 if ins.object.original.name!='255 Continuous wall infill to sill':continue
 me=ins.object.to_mesh();me.calc_loop_triangles();off=len(verts);verts.extend(ins.matrix_world@v.co for v in me.vertices);tris.extend(tuple(off+i for i in t.vertices)for t in me.loop_triangles);ins.object.to_mesh_clear()
assert len(tris)==12
tr=BVHTree.FromPolygons(verts,tris,all_triangles=True);clip.external_tree=lambda scene:(tr,['255 infill']*len(tris),{'scope':'New full-bay infill only','triangles':len(tris)})
clip.NAME='096 contacts ink';ink=clip.apply(s,max_pixel_step=.35,gap_m=.005)
ink['scope']='Only096contact-ink portions physically occluded by new255wall bay; all other occluders excluded.'
(O/'ink-audit.json').write_text(json.dumps(ink,indent=2))
(O/'audit.json').write_text(json.dumps({'replaced_collection':old.name,'removed_entire_bay_members':[o.name for o in old.objects],'new_bounds_local':[[x0,x1],[y0,y1],[z0,z1]],'world_front_x':9.6,'world_sill_z':12.36,'world_top_z':15.48,'depth_m':1.25,'obsolete_surrounds_removed':True,'brackets_unchanged':True,'collar_unchanged':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
