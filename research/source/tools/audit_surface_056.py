import bpy,json,hashlib
from pathlib import Path
R=Path('/PATH/TO/transmissions-from-alpha-centauri/art/reviews/surface-056')
checks={}
for stage in ['clean','mottled','weathered']:
 bpy.ops.wm.open_mainfile(filepath=str(R/(stage+'.blend')))
 obs=[]
 for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
  d={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world]}
  if o.type=='MESH':
   d['v']=[list(v.co) for v in o.data.vertices];d['p']=[list(p.vertices) for p in o.data.polygons]
   d['modifiers']=[(m.type,getattr(m,'width',None),getattr(m,'segments',None)) for m in o.modifiers]
  if o.type=='CURVE':d['curve']={'radius':o.data.bevel_depth,'resolution':o.data.resolution_u,'cap':o.data.use_fill_caps,'points':[[list(p.co),list(p.handle_left),list(p.handle_right)] for s in o.data.splines for p in s.bezier_points]}
  if o.type=='CAMERA':d['camera']=[o.data.type,o.data.ortho_scale,o.data.lens]
  obs.append(d)
 checks[stage]=hashlib.sha256(json.dumps(obs,sort_keys=True).encode()).hexdigest()
(R/'geometry-check.json').write_text(json.dumps({'signatures':checks,'identical':len(set(checks.values()))==1,'covers':'Transforms, mesh vertices/faces and bevels, curve control points/handles and sweep, camera'},indent=2))
