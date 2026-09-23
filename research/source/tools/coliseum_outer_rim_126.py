"""Explicit Freestyle outer-front archivolt edge marks; no vertex changes."""
import bpy,math,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_depth_120 import _authored
def apply(C):
 marked=[];skipped=[]
 rim=bpy.data.collections.get('126 Outer arch boundary targets')or bpy.data.collections.new('126 Outer arch boundary targets')
 if rim.name not in bpy.context.scene.collection.children:bpy.context.scene.collection.children.link(rim)
 for ob in C.objects:
  if ob.type!='MESH' or 'archivolt1 stone'not in ob.name:continue
  p=_authored(ob)
  if p is None:continue
  rr=[math.hypot(v.x,v.y)/(1-.055*v.z/78)for v in p];hi=max(rr);ids=[i for i,r in enumerate(rr)if r>hi-.03]
  # Each wedge has two front radii; the outer pair is farther from its own arch spring.
  j=ob.get('bay');tier=ob.get('tier');a=-math.pi+(j+.5)*math.tau/36
  family=[x for x in C.objects if x.type=='MESH'and x.get('bay')==j and x.get('tier')==tier and 'archivolt1 stone'in x.name]
  allp=[v for x in family for v in (_authored(x)or[])];spring=min(v.z for v in allp)
  def d(i):
   theta=math.atan2(p[i].y,p[i].x)
   if theta>math.pi/2:theta-=math.tau
   return ((theta-a)*75)**2+(p[i].z-spring)**2
  outer=set(sorted(ids,key=d,reverse=True)[:max(2,len(ids)//2)]);edges=[e for e in ob.data.edges if set(e.vertices)<=outer]
  if not edges:skipped.append(ob.name);continue
  attr=ob.data.attributes.get('freestyle_edge')or ob.data.attributes.new('freestyle_edge','BOOLEAN','EDGE')
  if ob.name not in rim.objects:rim.objects.link(ob)
  for edge in edges:
   attr.data[edge.index].value=True;marked.append({'object':ob.name,'edge':edge.index})
 settings=bpy.context.view_layer.freestyle_settings
 ls=settings.linesets.get('126 Outer arch molding boundary')or settings.linesets.new('126 Outer arch molding boundary')
 for k in ['select_silhouette','select_border','select_crease','select_ridge_valley','select_suggestive_contour','select_material_boundary','select_contour','select_external_contour']:
  if hasattr(ls,k):setattr(ls,k,False)
 ls.select_edge_mark=True;ls.select_by_collection=True;ls.collection=rim;ls.collection_negation='INCLUSIVE';ls.linestyle.thickness=.65;ls.linestyle.color=(.025,.019,.032)
 return {'marked_outer_edges':marked,'skipped':skipped,'vertices_changed':0,'scope':'Landmark outer-front archivolt edges only','line_thickness':.65}
if __name__=='__main__':
 O=R/'art/studies/coliseum-126/joints';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-124/B/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];a=apply(C);(O/'audit.json').write_text(json.dumps(a,indent=2));s=bpy.context.scene;s.render.use_freestyle=True
 for ob in s.objects:
  if ob.type=='GREASEPENCIL':ob.hide_render=True
 s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.425;s.render.border_max_x=.565;s.render.border_min_y=.69;s.render.border_max_y=.82;s.render.filepath=str(O/'outer-rim.png');bpy.ops.render.render(write_still=True)
