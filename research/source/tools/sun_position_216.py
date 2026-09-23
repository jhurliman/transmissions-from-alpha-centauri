"""Exact projected translation of the existing native camera-only world sun.
The source sun is an angular procedural disc at infinity, not a finite-depth object.
No color, light, cloud, geometry or camera changes; no image projection.
"""
import bpy,math,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

def measure(scene):
 nt=scene.world.node_tree;dot=next(n for n in nt.nodes if n.label=='075 Sun angular distance');cut=next(n for n in nt.nodes if n.label=='075 GREATER_THAN' and any(l.from_node==dot for l in n.inputs[0].links))
 raw_direction=Vector(dot.inputs[1].default_value);raw_threshold=float(cut.inputs[1].default_value);c=raw_threshold/raw_direction.length;direction=-raw_direction.normalized();cam=scene.camera;basis=cam.matrix_world.to_3x3();R=(basis@Vector((1,0,0))).normalized();U=(basis@Vector((0,1,0))).normalized();F=(basis@Vector((0,0,-1))).normalized();sx,sy,sz=[direction.dot(v)for v in (R,U,F)]
 A=c*c-sx*sx;B=-sx*sy;C=c*c-sy*sy;D=-sx*sz;E=-sy*sz;G=c*c-sz*sz;det=A*C-B*B
 assert det>0
 ixx,ixy,iyy=C/det,-B/det,A/det;ux,uy=-(ixx*D+ixy*E),-(ixy*D+iyy*E);k=A*ux*ux+2*B*ux*uy+C*uy*uy-G;ex,ey=math.sqrt(k*ixx),math.sqrt(k*iyy)
 origin=cam.matrix_world.translation
 def pixel(u,v):
  p=world_to_camera_view(scene,cam,origin+(F+u*R+v*U)*1000)
  return [p.x*scene.render.resolution_x,(1-p.y)*scene.render.resolution_y]
 center=pixel(ux,uy);left=pixel(ux-ex,uy)[0];right=pixel(ux+ex,uy)[0];top=pixel(ux,uy+ey)[1];bottom=pixel(ux,uy-ey)[1]
 return {'center_full_resolution_px':center,'horizontal_diameter_px':right-left,'vertical_diameter_px':bottom-top,'bounds_full_resolution_px':[left,top,right,bottom],'normalized_camera_plane_center':[ux,uy],'normalized_camera_plane_diameter':2*ex,'angular_threshold':raw_threshold,'effective_unit_direction_threshold':c,'sun_direction_input':list(dot.inputs[1].default_value),'camera_right':list(R),'camera_forward':list(F),'native_depth':'Infinity: procedural world disc'},dot,cut

def apply(scene,move_right=True):
 before,dot,cut=measure(scene);audit={'variant':'right-one-diameter'if move_right else'original','before':before,'source_world':scene.world.name,'native_representation':'Existing camera-only procedural angular world disc','reference_config':'config/sun-position-216.json','approved':False}
 if not move_right:
  audit['after']=dict(before);audit['horizontal_shift_px']=0.;return audit
 if any(n.name.startswith('216 ')for n in scene.world.node_tree.nodes):raise RuntimeError('216 must start from original sun mapping; do not apply twice')
 matrices={o.name:[list(row)for row in o.matrix_world]for o in scene.objects};lights={o.name:{'matrix':matrices[o.name],'data':o.data.name,'color':list(o.data.color),'energy':o.data.energy,'type':o.data.type}for o in scene.objects if o.type=='LIGHT'}
 original=scene.world;original.use_fake_user=True;scene.world=original.copy();scene.world.name=original.name+' · 216 sun right';nt=scene.world.node_tree;dot=next(n for n in nt.nodes if n.label=='075 Sun angular distance');oldlink=dot.inputs[0].links[0];normal=oldlink.from_socket;source_node=oldlink.from_node.name;source_socket=normal.name
 def vec(op,label):
  n=nt.nodes.new('ShaderNodeVectorMath');n.operation=op;n.name='216 '+label;n.label=n.name;return n
 depth=vec('DOT_PRODUCT','Sun ray forward component');depth.inputs[1].default_value=before['camera_forward'];nt.links.new(normal,depth.inputs[0])
 offset=vec('SCALE','One apparent diameter camera-right');offset.inputs[0].default_value=Vector(before['camera_right'])*before['normalized_camera_plane_diameter'];nt.links.new(depth.outputs['Value'],offset.inputs['Scale'])
 shift=vec('SUBTRACT','Translate only visible sun ray');nt.links.new(normal,shift.inputs[0]);nt.links.new(offset.outputs['Vector'],shift.inputs[1]);unit=vec('NORMALIZE','Normalize translated sun ray');nt.links.new(shift.outputs['Vector'],unit.inputs[0]);nt.links.new(unit.outputs['Vector'],dot.inputs[0])
 # Exact plane-coordinate translation leaves the source angular test unchanged.
 delta=float(before['horizontal_diameter_px']);after=dict(before);after['center_full_resolution_px']=[before['center_full_resolution_px'][0]+delta,before['center_full_resolution_px'][1]];after['bounds_full_resolution_px']=[before['bounds_full_resolution_px'][0]+delta,before['bounds_full_resolution_px'][1],before['bounds_full_resolution_px'][2]+delta,before['bounds_full_resolution_px'][3]]
 # Independent boundary transport check through the native node formula.
 R=Vector(before['camera_right']);F=Vector(before['camera_forward']);d=-Vector(before['sun_direction_input']).normalized();axis=d.cross(R).normalized();other=d.cross(axis).normalized();theta=math.acos(before['effective_unit_direction_threshold']);origin=scene.camera.matrix_world.translation;shift_errors=[];angular_errors=[]
 for i in range(360):
  t=2*math.pi*i/360;ray=d*math.cos(theta)+(axis*math.cos(t)+other*math.sin(t))*math.sin(theta);moved=ray+R*(ray.dot(F)*before['normalized_camera_plane_diameter']);normal=-moved;remapped=(normal-R*(normal.dot(F)*before['normalized_camera_plane_diameter'])).normalized();angular_errors.append(abs(remapped.dot(Vector(before['sun_direction_input']))-before['angular_threshold']))
  p=world_to_camera_view(scene,scene.camera,origin+ray*1000);q=world_to_camera_view(scene,scene.camera,origin+moved*1000);shift_errors.append(max(abs((q.x-p.x)*scene.render.resolution_x-delta),abs((q.y-p.y)*scene.render.resolution_y)))
 assert max(shift_errors)<.01,max(shift_errors)
 audit['boundary_transport_max_error_full_resolution_px']=max(shift_errors);audit['boundary_angular_test_max_error']=max(angular_errors);audit['independent_boundary_samples']=360
 assert all([list(row)for row in bpy.data.objects[n].matrix_world]==m for n,m in matrices.items())
 assert all(list(bpy.data.objects[n].data.color)==v['color']and bpy.data.objects[n].data.energy==v['energy']and bpy.data.objects[n].data.type==v['type']for n,v in lights.items())
 assert list(dot.inputs[1].default_value)==before['sun_direction_input']
 audit.update({'after':after,'horizontal_shift_px':delta,'shift_in_original_horizontal_diameters':1.,'vertical_shift_px':0.,'apparent_dimensions_unchanged':True,'source_normal_socket':[source_node,source_socket],'private_world':scene.world.name,'all_object_transforms_unchanged':True,'all_scene_lights_unchanged':True,'source_world_graph_preserved':original.name,'changed_native_nodes':[n.name for n in nt.nodes if n.name.startswith('216 ')],'mapping':'Nprime=normalize(N - cameraRight * (N dot cameraForward) * projectedDiameter/focalPixels). Only the visible sun dot-product receives Nprime.'})
 return audit
