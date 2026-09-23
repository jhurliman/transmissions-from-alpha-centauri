"""Re-art-direct native soil intersection contours into broken pigment fissures.
Uses rejected soil-only contours, never reference-image projection. Positions
and visibility remain those of the native 096 intersection calculation.
"""
import bpy,sys,random,math,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[1];O=R/'art/studies/soil-097';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/lines-096/scene.blend'));s=bpy.context.scene;rng=random.Random(97019)
cache=O/'source-contours.json';source=None
if not cache.exists():
 with bpy.data.libraries.load(str(R/'art/studies/lines-096/scene.blend1'),link=False) as (src,dst):dst.objects=['096 contacts ink']
 source=dst.objects[0];source.hide_render=True
W=s.render.resolution_x;H=s.render.resolution_y
def project(p):
 q=world_to_camera_view(s,s.camera,p);return Vector((q.x*W,q.y*H))
if cache.exists():
 raw=[[Vector(p) for p in run] for run in json.loads(cache.read_text())]
else:
 raw=[]
 for frame in source.data.layers[0].frames:
  for st in frame.drawing.strokes:
   run=[]
   for p in st.points:
    v=Vector(p.position)
    if p.opacity<.01 and -8.1<v.x<8.1 and -10.3<v.y<34 and -.35<v.z<.35:
     if not run or (project(v)-project(run[-1])).length>.06:run.append(v)
    else:
     if len(run)>1:raw.append(run)
     run=[]
   if len(run)>1:raw.append(run)
assert raw,'Need unpruned source drawing with rejected soil samples'
(O/'source-contours.json').write_text(json.dumps([[list(v) for v in run] for run in raw]))
# Subdivide actual contour segments to control cuts and taper in screen space.
fragments=[];corner_cuts=0
for run in raw:
 dense=[run[0]];remaining=.45;total=0
 for a,b in zip(run,run[1:]):
  length=(project(b)-project(a)).length;total+=length;offset=0
  while length-offset>=remaining:
   offset+=remaining;dense.append(a.lerp(b,offset/max(length,1e-8)));remaining=.45
  remaining-=length-offset
 if (project(dense[-1])-project(run[-1])).length>.04:dense.append(run[-1])
 # Separate independently generated native runs that meet at box corners.
 if total>5 and len(dense)>9:dense=dense[4:-4]
 # Mark right-angle helper corners for a small clean break, not a fading elbow.
 cuts=set()
 for i in range(1,len(dense)-1):
  a=project(dense[i])-project(dense[max(0,i-4)]);b=project(dense[min(len(dense)-1,i+4)])-project(dense[i])
  if a.length>.01 and b.length>.01 and a.normalized().dot(b.normalized())<.72:
   cuts.update(range(max(0,i-4),min(len(dense),i+5)));corner_cuts+=1
 i=0
 while i<len(dense)-1:
  maxlen=rng.uniform(3,16);pts=[];length=0
  while i<len(dense) and i not in cuts and length<maxlen:
   if pts:length+=(project(dense[i])-project(pts[-1])).length
   pts.append(dense[i]);i+=1
  if len(pts)>1 and length>.65:
   # Short fragments retain most original density; end taper and variable
   # width give chipped/gritty edges rather than constant-width boxes.
   fragments.append((pts,rng.uniform(.6,.85),rng.uniform(.96,1)))
  i+=rng.choice([1,1,2,3])
g=bpy.data.grease_pencils.new('097 Broken soil ink');ob=bpy.data.objects.new('097 Broken soil ink',g);s.collection.objects.link(ob);layer=g.layers.new('Soil contour fragments',set_active=True);layer.use_lights=False;g.materials.append(bpy.data.objects['096 contacts ink'].data.materials[0]);drawing=layer.frames.new(s.frame_current).drawing;drawing.add_strokes(sizes=[len(p) for p,_,_ in fragments]);right=s.camera.matrix_world.to_quaternion()@Vector((1,0,0))
for stroke,(pts,width,opacity) in zip(drawing.strokes,fragments):
 for i,(p,pos) in enumerate(zip(stroke.points,pts)):
  p.position=pos;ppm=(project(pos+right)-project(pos)).length;t=i/max(1,len(pts)-1);tip=min(1,.65+min(t,1-t)*3)
  p.radius=width*tip*rng.uniform(.76,1.2)/max(ppm,1);p.opacity=opacity
if source:bpy.data.objects.remove(source,do_unlink=True)
(O/'audit.json').write_text(json.dumps({'source':'native096 rejected soil contours','raw_runs':len(raw),'soil_fragments':len(fragments),'sharp_corner_breaks':corner_cuts,'pixel_radius_range':[.6,.85],'locked_scene':'096','geometry_and_materials_unchanged':True,'camera_specific':True},indent=2));print('SOIL_INK',len(raw),len(fragments),flush=True)
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.use_border=False;s.render.resolution_percentage=100;bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
