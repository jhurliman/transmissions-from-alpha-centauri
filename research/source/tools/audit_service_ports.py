import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]/'art/components/services/v002';bpy.ops.wm.open_mainfile(filepath=str(P/'service-kit.blend'))
result=[]
for c in bpy.data.collections:
 if 'ports_json' not in c:continue
 for port in json.loads(c['ports_json']):
  if port.get('profile')!='rect':continue
  p=Vector(port['position']);n=Vector(port['outward']);y=Vector(port.get('up',[0,1,0]));y=(y-n*y.dot(n)).normalized();x=y.cross(n).normalized();from mathutils import Matrix;frame=Matrix((x,y,n)).transposed();verts=[]
  for o in c.objects:
   if o.type!='MESH':continue
   for v in o.data.vertices:
    q=o.matrix_world@v.co-p
    if abs(q.dot(n))<1e-5:verts.append(frame.transposed()@q)
  width=max(v.x for v in verts)-min(v.x for v in verts);height=max(v.y for v in verts)-min(v.y for v in verts)
  ok=abs(width-port['width']-.048)<.002 and abs(height-port['height']-.048)<.002
  result.append({'part':c['part_id'],'position':port['position'],'outer_width':width,'outer_height':height,'profile_matches':ok})
(P/'profile-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('PORT PROFILES',len(result),'FAILURES',[r for r in result if not r['profile_matches']])

assert all(r["profile_matches"] for r in result), "Rectangular mesh does not match its declared port orientation"
