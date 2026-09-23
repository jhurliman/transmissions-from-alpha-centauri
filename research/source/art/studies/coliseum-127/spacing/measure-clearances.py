import bpy,math,json,sys,re,collections
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'tools'));from coliseum_arch_ratio_125 import mapping
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-127/spacing/scene.blend'));_,world,unpack=mapping();C=bpy.data.collections['110 Coliseum detailed front ruin'];bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();cache=[]
for ob in C.objects:
 if ob.type!='MESH':continue
 tower=re.search(r'Tower\s*(\d+)',ob.name,re.I);col='engaged round column'in ob.name;arch='archivolt1 stone'in ob.name
 if not(tower or col or arch):continue
 ev=ob.evaluated_get(dg);me=ev.to_mesh();pts=[unpack(ev.matrix_world@v.co)for v in me.vertices];ed=[tuple(e.vertices)for e in me.edges];ev.to_mesh_clear();cache.append((ob,tower,col,arch,pts,ed))
rows=[]
for tier in range(3):
 base=2.73+tier*18.33+.35;spring=base+.95*(2.73+(tier+1)*18.33-2.184-75*math.tau/36*.34-base)
 for off in [.5,.8,1.2]:
  z=spring+off;profile=collections.defaultdict(list)
  for ob,tower,col,arch,pts,edges in cache:
   if not tower and ob.get('tier')!=tier:continue
   key=('tower',int(tower.group(1)))if tower else('column'if col else'arch',int(ob['bay']))
   for i,j in edges:
    p,q=pts[i],pts[j]
    if (p[2]-z)*(q[2]-z)<=0 and abs(q[2]-p[2])>1e-6:
     t=(z-p[2])/(q[2]-p[2]);r=p[0]+t*(q[0]-p[0]);a=p[1]+t*(q[1]-p[1]);profile[key].append((75*(a+math.pi/2),r))
  bounds={k:(min(x for x,r in v),max(x for x,r in v))for k,v in profile.items()}
  for bay in range(4,13):
   if ('arch',bay)not in bounds:continue
   lo,hi=bounds['arch',bay]
   # Towers stand at boundary j; round columns boundary j+1.
   left=('tower',bay)if bay in [1,4,7,10,13,16]else('column',bay-1)
   right=('tower',bay+1)if bay+1 in [1,4,7,10,13,16]else('column',bay)
   if left in bounds and right in bounds:rows.append({'tier':tier,'bay':bay,'height_above_spring':off,'left_support':str(left),'right_support':str(right),'left_gap':lo-bounds[left][1],'right_gap':bounds[right][0]-hi,'arch_width':hi-lo})
O=R/'art/studies/coliseum-127/spacing';(O/'measured-clearance.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
