import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/PATH/TO/transmissions-from-alpha-centauri');O=R/'art/studies/coliseum-130/tunnels';bpy.ops.wm.open_mainfile(filepath=str(O/'geometry.blend'));s=bpy.context.scene;obs=[o for o in s.objects if o.get('130 barrel tunnel')];a=json.loads((O/'audit.json').read_text());rows=[];trees=[]
for o in obs:trees.append(BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons]))
for o,tree,r in zip(obs,trees,a['objects']):
 center=Vector(r['rear_center_world']);end=Vector(r['open_exit_center_world']);turn=-1 if r['turn']=='left'else 1;out=Vector((turn,0,0));height=3.;entry=center+Vector((0,-.2,height));exit_inside=end-out*.1+Vector((0,0,height));exit_outside=end+out*.2+Vector((0,0,height));hit=tree.ray_cast(entry,Vector((0,1,0)));back=tree.ray_cast(exit_outside,-out);outward=tree.ray_cast(exit_inside,out)
 rows.append({'object':o.name,'entry_open_until_first_bend_hit_m':hit[3],'exit_backwards_clearance_m':back[3],'exit_outward_ray_clear':outward[0]is None,'open_end_requirement':bool(hit[3]>25 and back[3]>5 and outward[0]is None)})
# BVH broad-phase overlaps are conservative. Zero pairs certifies the two distinct shell bounds don't intersect.
pairs=trees[0].overlap(trees[1]);audit={'open_ends':rows,'between_tunnels_triangle_bbox_overlap_pairs':len(pairs),'interpenetration_conclusion':'No interpenetration between tunnel shells'if not pairs else'Broadphase pairs require narrowphase check','source_scene':'129/scene.blend','new_geometry_only':[o.name for o in obs]};(O/'geometry-validation.json').write_text(json.dumps(audit,indent=2));print(audit,flush=True)
# Geometry proofs hide existing scene geometry, preserving full actual tunnel solids. No proxy caps or cutaway invented.
for o in s.objects:
 if o.type not in ['CAMERA','LIGHT']and o not in obs:o.hide_render=True
s.render.engine='BLENDER_WORKBENCH';s.render.use_compositing=False;s.render.use_freestyle=False;s.display.shading.light='STUDIO';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.58,.48,.39);s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.render.use_border=False;s.render.resolution_x=1500;s.render.resolution_y=1200;s.render.resolution_percentage=100;c=s.camera;c.data.type='ORTHO';c.data.ortho_scale=62
for label,pos,target in [('top',(0,228,80),(0,228,0)),('geometry',(24,177,38),(0,228,6)),('open-exits',(-28,267,30),(0,240,6))]:
 c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(label+'.png'));bpy.ops.render.render(write_still=True)
