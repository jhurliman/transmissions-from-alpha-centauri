"""Local broad-fill correction on real voussoir radial end faces; no geometry change."""
import bpy,math,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
from coliseum_arch_thickness_129 import params,closest
ATTR='129 Radial masonry joint end'
def apply(C,strength=1.,actual_diffuse=False,reduce_ao=False):
 _,_,unpack=mapping();cache={};count=0;objects=0;vertices_verified=0
 for ob in C.objects:
  if ob.type!='MESH'or'archivolt'not in ob.name or 'niche' in ob.name.lower():continue
  before_coords=[tuple(v.co)for v in ob.data.vertices];ob.data=ob.data.copy();me=ob.data;t,b=int(ob['tier']),int(ob['bay']);rx,rz,sp=params(t,b);ac=-math.pi+(b+.5)*math.tau/36;coords=[]
  for v in me.vertices:
   rr,a,z=unpack(ob.matrix_world@v.co);d,nx,ny=closest((a-ac)*75,z-sp,rx,rz);th=math.atan2(ny*rz,nx*rx);coords.append((rr,d,th))
  at=me.attributes.get(ATTR)or me.attributes.new(ATTR,'FLOAT','FACE')
  hits=0
  for p in me.polygons:
   co=[coords[i]for i in p.vertices];span=lambda k:max(x[k]for x in co)-min(x[k]for x in co);yes=span(0)>.1 and span(1)>.1 and span(2)<.005;at.data[p.index].value=float(yes);hits+=yes
  if not hits:continue
  count+=hits;objects+=1;assert before_coords==[tuple(v.co)for v in me.vertices];vertices_verified+=len(before_coords)
  for sl in ob.material_slots:
   old=sl.material
   if not old or not old.use_nodes:continue
   if old.get('129 radial joint treatment'):raise RuntimeError('Apply joint correction only once')
   if old not in cache:
    m=old.copy();m['129 radial joint treatment']=True;m.name='129 Joint end broad fill '+old.name;n,l=m.node_tree.nodes,m.node_tree.links;orient=next((q for q in n if q.label=='Broad form lighting'),None);gate=next((q for q in n if q.label=='128 Only outward-facing masonry receives broad fill'),None)
    if not orient or not gate:raise RuntimeError('Expected128 broad lighting graph')
    dot=gate.inputs['Value'].links[0].from_node;macro=dot.inputs[1].links[0].from_socket;native=orient.inputs[0].links[0].from_socket
    a=n.new('ShaderNodeAttribute');a.attribute_name=ATTR;a.label='Only physical radial joint end faces';f=n.new('ShaderNodeMath');f.operation='MULTIPLY';f.inputs[1].default_value=strength;l.new(a.outputs['Fac'],f.inputs[0]);inv=n.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;l.new(f.outputs[0],inv.inputs[1]);x=n.new('ShaderNodeVectorMath');x.operation='SCALE';l.new(native,x.inputs[0]);l.new(inv.outputs[0],x.inputs['Scale']);y=n.new('ShaderNodeVectorMath');y.operation='SCALE';l.new(macro,y.inputs[0]);l.new(f.outputs[0],y.inputs['Scale']);add=n.new('ShaderNodeVectorMath');add.operation='ADD';l.new(x.outputs[0],add.inputs[0]);l.new(y.outputs[0],add.inputs[1]);norm=n.new('ShaderNodeVectorMath');norm.operation='NORMALIZE';l.new(add.outputs[0],norm.inputs[0]);l.new(norm.outputs[0],orient.inputs[0]);l.new(norm.outputs[0],dot.inputs[0])
    if actual_diffuse:
     for q in n:
      if q.type=='BSDF_DIFFUSE':l.new(norm.outputs[0],q.inputs['Normal'])
    if reduce_ao:
     for q in list(n):
      if q.type=='AMBIENT_OCCLUSION':
       out=q.outputs['AO'];targets=[li.to_socket for li in list(out.links)];aa=n.new('ShaderNodeMath');aa.operation='MULTIPLY';l.new(out,aa.inputs[0]);l.new(inv.outputs[0],aa.inputs[1]);bb=n.new('ShaderNodeMath');bb.operation='ADD';l.new(aa.outputs[0],bb.inputs[0]);l.new(f.outputs[0],bb.inputs[1])
       for to in targets:l.new(bb.outputs[0],to)
    cache[old]=m
   sl.link='OBJECT';sl.material=cache[old]
 return {'vertices_verified_unchanged':vertices_verified,'vertex_displacement':0.,'objects':objects,'radial_end_faces':count,'strength':strength,'actual_diffuse_normal_adjusted':actual_diffuse,'local_end_face_ao_reduced':reduce_ao,'scope':'Only broad orientation and its macro compensation on tagged radial joint end faces. Diffuse/glossy untouched unless explicitly requested; optional AO reduction only on tagged ends. Physical normals, gaps, depth and all vertices unchanged.'}
if __name__=='__main__':
 O=R/'art/studies/coliseum-129/joints';bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-129/arches/geometry.blend'));a=apply(bpy.data.collections['110 Coliseum detailed front ruin'],reduce_ao=True);s=bpy.context.scene;s.render.use_freestyle=False;s.render.resolution_x=7680;s.render.resolution_y=5770;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=.43;s.render.border_max_x=.53;s.render.border_min_y=.69;s.render.border_max_y=.80;s.render.filepath=str(O/'end-face-ao.png');bpy.ops.render.render(write_still=True);(O/'end-face-ao.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'end-face-ao.blend'));print(a)
