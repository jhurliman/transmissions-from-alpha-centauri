import bpy,math
from mathutils import Matrix,Vector

def apply(s):
 root=s.objects['right_vertical_galleries'];original=root.instance_collection
 private=bpy.data.collections.new('253 Private gallery with solid duct entry');private.instance_offset=original.instance_offset;private.use_fake_user=True
 target=next(o for o in original.objects if o.instance_collection and abs(o.location.x+4.2)<.01 and abs(o.location.z-12.36)<.01)
 bay=bpy.data.collections.new('253 Upper duct entry infill bay');bay.use_fake_user=True
 removed=[]
 for o in target.instance_collection.objects:
  if o.instance_collection and str(o.instance_collection.get('part_id','')).startswith('window_slider'):
   removed.append(o.name)
  else:bay.objects.link(o)
 assert len(removed)==1,removed
 material=next(o for o in original.objects if o.name.startswith('Gallery upper quiet panel')).material_slots[0].material
 F=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
 def box(name,center,size,mat,col):
  vs=[(center[0]+i*size[0]/2,center[1]+j*size[1]/2,center[2]+k*size[2]/2)for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  me=bpy.data.meshes.new(name);me.from_pydata(vs,[],F);me.materials.append(mat);o=bpy.data.objects.new(name,me);col.objects.link(o);b=o.modifiers.new('Small manufactured arris','BEVEL');b.width=.008;b.segments=1;return o
 panel=box('253 Flat weathered masonry duct entry',(0,.09,1.56),(1.95,.18,2.04),material,bay)
 q=target.copy();q.instance_collection=bay
 for o in original.objects:private.objects.link(q if o==target else o)
 for c in original.children:private.children.link(c)
 root.instance_collection=private
 C=bpy.data.collections.new('253 Side-wall return brackets');s.collection.children.link(C)
 moves=[];hidden=[]
 for index,z in enumerate([4.4,6.8,9.2,11.6]):
  saddle=s.objects[f'Duct wall saddle.{11+index:03d}'];mat=saddle.material_slots[0].material;saddle.hide_render=True;saddle.hide_viewport=True;hidden.append(saddle.name)
  for o in list(s.objects):
   if o.type=='MESH' and o.name.startswith('073 standoff wall extension'):
    pts=[o.matrix_world@Vector(v)for v in o.bound_box];center=sum(pts,Vector())/8
    if abs(center.y-15.8)<.01 and abs(center.z-z)<.01:o.hide_render=True;o.hide_viewport=True;hidden.append(o.name)
  # One continuous L-shaped rectangular support, with a 90-degree plan return.
  x0=9.12;xe=9.82;y0=15.8;wall=14.52;w=.18
  poly=[(x0,y0-w/2),(xe-w/2,y0-w/2),(xe-w/2,wall+.065),(xe+w/2,wall+.065),(xe+w/2,y0+w/2),(x0,y0+w/2)]
  n=len(poly);vs=[(x,y,zz)for zz in [z-.06,z+.06]for x,y in poly];fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n)for j in range(n)]
  me=bpy.data.meshes.new('253 L bracket');me.from_pydata(vs,[],fs);me.materials.append(mat);o=bpy.data.objects.new(f'253 Duct support side return {index+1}',me);C.objects.link(o);b=o.modifiers.new('Steel arris','BEVEL');b.width=.009;b.segments=1
  shoe=s.objects[f'073 bolted wall shoe.{33+index:03d}'];shoe.matrix_world=Matrix.Translation((xe,wall,z))@Matrix.Rotation(math.pi,4,'Z')
  moves.append({'height':z,'duct_contact':[x0,y0,z],'turn':[xe,y0,z],'wall_face':[xe,wall,z],'shoe':shoe.name})
 assert len(hidden)==8,hidden
 return {'window_bay':target.name,'removed_slider':removed,'flat_panel':panel.name,'four_returns':moves,'hidden_old_arms':hidden,'bottom_mount_unchanged':True,'side_wall':'Gallery pier at y14.4, side face y14.52, x9.5–10.15','top_entry':'Existing duct receiver now passes into solid replacement panel','other_gallery_instances_unchanged':True}
