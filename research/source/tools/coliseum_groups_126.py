"""Three-arch groups with dedicated tower envelopes; shared native angular deformation."""
import bpy,math,json,re,sys,time
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from coliseum_arch_ratio_125 import mapping
L=75*math.tau/12;T0=75*(-math.pi+math.tau/36+math.pi/2)
def group(F,period,clearance):
 g=bpy.data.node_groups.new('126 Shared three-arch grouping','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 for prefix in ['World','Local']:
  for suf in ['0','1','2','T']:g.interface.new_socket(name=prefix+suf,in_out='INPUT',socket_type='NodeSocketVector')
 for name in ['Rigid','Center']:g.interface.new_socket(name=name,in_out='INPUT',socket_type='NodeSocketFloat')
 n=g.nodes;l=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');pos=n.new('GeometryNodeInputPosition')
 def put(v,s):
  if isinstance(v,(float,int,tuple,Vector)):s.default_value=v
  else:l.new(v,s)
 def mathn(op,*args):
  x=n.new('ShaderNodeMath');x.operation=op
  for i,a in enumerate(args):put(a,x.inputs[i])
  return x.outputs[0]
 def vec(op,*args):
  x=n.new('ShaderNodeVectorMath');x.operation=op
  for i,a in enumerate(args):put(a,x.inputs[i])
  return x.outputs['Value']if op=='DOT_PRODUCT'else x.outputs[0]
 def combine(x,y,z):
  v=n.new('ShaderNodeCombineXYZ')
  for i,a in enumerate([x,y,z]):put(a,v.inputs[i])
  return v.outputs[0]
 def mat(p,M=None,prefix=None):
  rows=[tuple(M[i][k]for k in range(3))for i in range(3)]if M is not None else[inp.outputs[prefix+str(i)]for i in range(3)];t=tuple(M.translation)if M is not None else inp.outputs[prefix+'T'];return vec('ADD',combine(*[vec('DOT_PRODUCT',p,r)for r in rows]),t)
 w=mat(pos.outputs[0],prefix='World');q=mat(w,F.inverted());sep=n.new('ShaderNodeSeparateXYZ');l.new(q,sep.inputs[0]);x,y,z=[sep.outputs[k]for k in ['X','Y','Z']];rho=mathn('SQRT',mathn('ADD',mathn('MULTIPLY',x,x),mathn('MULTIPLY',y,y)));angle=mathn('ARCTAN2',y,x);angle=mathn('SUBTRACT',angle,mathn('MULTIPLY',mathn('GREATER_THAN',angle,math.pi/2),math.tau));xx=mathn('MULTIPLY',mathn('DIVIDE',mathn('ADD',angle,math.pi/2),.68),75)
 # x measured from front-center, with tower boundaries every three source bays.
 ix=mathn('FLOOR',mathn('DIVIDE',mathn('SUBTRACT',xx,T0),L));boundary=mathn('ADD',T0,mathn('MULTIPLY',ix,L));u=mathn('SUBTRACT',xx,boundary)
 h=75*math.tau/36*.34*.8+.83;c=L/6;edge=3.657+clearance;centers=[edge+h,period/2,period-edge-h];ks=[0,c-h,c+h,L/2-h,L/2+h,5*L/6-h,5*L/6+h,L];vs=[0,centers[0]-h,centers[0]+h,centers[1]-h,centers[1]+h,centers[2]-h,centers[2]+h,period]
 def interpolate(knots,values):
  value=0
  for i in range(len(knots)-1):
   clipped=mathn('MINIMUM',mathn('MAXIMUM',mathn('SUBTRACT',u,knots[i]),0),knots[i+1]-knots[i]);value=mathn('ADD',value,mathn('MULTIPLY',clipped,(values[i+1]-values[i])/(knots[i+1]-knots[i])))
  return value
 wideperiod=50.5;wh=75*math.tau/36*.34+.83;wc=[edge+wh,wideperiod/2,wideperiod-edge-wh];wks=[0,c-wh,c+wh,L/2-wh,L/2+wh,5*L/6-wh,5*L/6+wh,L];wvs=[0,wc[0]-wh,wc[0]+wh,wc[1]-wh,wc[1]+wh,wc[2]-wh,wc[2]+wh,wideperiod]
 flag=mathn('LESS_THAN',mathn('ABSOLUTE',mathn('SUBTRACT',ix,3)),.1);value=mathn('ADD',mathn('MULTIPLY',flag,interpolate(wks,wvs)),mathn('MULTIPLY',mathn('SUBTRACT',1,flag),interpolate(ks,vs)));extra=mathn('MULTIPLY',mathn('GREATER_THAN',ix,3.5),wideperiod-period);general=mathn('ADD',mathn('ADD',mathn('MULTIPLY',boundary,period/L),extra),value)
 rigid=mathn('ADD',mathn('SUBTRACT',xx,inp.outputs['Center']),inp.outputs['Rigid'])
 use=mathn('GREATER_THAN',inp.outputs['Rigid'],-10000);newx=mathn('ADD',mathn('MULTIPLY',use,rigid),mathn('MULTIPLY',mathn('SUBTRACT',1,use),general));a=mathn('SUBTRACT',mathn('MULTIPLY',mathn('DIVIDE',newx,75),.68),math.pi/2);qq=combine(mathn('MULTIPLY',rho,mathn('COSINE',a)),mathn('MULTIPLY',rho,mathn('SINE',a)),z);nw=mat(qq,F);local=mat(nw,prefix='Local');setp=n.new('GeometryNodeSetPosition');l.new(inp.outputs['Geometry'],setp.inputs['Geometry']);l.new(local,setp.inputs['Position']);l.new(setp.outputs[0],out.inputs['Geometry']);return g,ks,vs

def apply(C,period=45.8,clearance=2.9):
 started=time.time();_,world,unpack=mapping();p0=world(75,-math.pi/2,0)
 # Reconstruct existing F from native world helper, preserving the complete approved affine pose.
 origin=world(0,-math.pi/2,0) # inner-radius compression makes this unsuitable for F translation; obtain explicit mapping metadata.
 from coliseum_columns_124 import R as root
 with bpy.data.libraries.load(str(R/'art/studies/coliseum-114/scene.blend'),link=False)as(src,dst):dst.objects=['COL110 U4 fractured upper wall L']
 a=dst.objects[0];lean=Matrix.Rotation(math.radians(2),4,'X');auth=Matrix.Translation(Vector((0,347,0)))@lean@Matrix.Rotation(-math.pi+4.5*math.tau/36,4,'Z');P=a.matrix_basis@auth.inverted()@Matrix.Translation(Vector((0,347,0)))@lean;bpy.data.objects.remove(a);A=Matrix(json.loads((R/'art/studies/coliseum-perspective-115/E/audit.json').read_text())['exact_affine']['world_transform']);Y=Matrix(json.loads((R/'art/studies/coliseum-116/generation-settings.json').read_text())['rotation']['delta_matrix']);F=Y@A@P;g,ks,vs=group(F,period,clearance)
 def f(x):
  ix=math.floor((x-T0)/L+1e-8);b=T0+ix*L;u=x-b;k,v=ks,vs
  if ix==3:
   wh=75*math.tau/36*.34+.83;c=L/6;edge=3.657+clearance;cs=[edge+wh,50.5/2,50.5-edge-wh];k=[0,c-wh,c+wh,L/2-wh,L/2+wh,5*L/6-wh,5*L/6+wh,L];v=[0,cs[0]-wh,cs[0]+wh,cs[1]-wh,cs[1]+wh,cs[2]-wh,cs[2]+wh,50.5]
  value=sum(max(0,min(u-k[i],k[i+1]-k[i]))*(v[i+1]-v[i])/(k[i+1]-k[i])for i in range(len(k)-1));return b*period/L+(50.5-period if ix>=4 else 0)+value
 bpy.context.view_layer.update();records=[]
 for ob in list(C.objects):
  if ob.type not in ['MESH','CURVE']or ob.get('126 grouped'):continue
  rigid=-10001.;center=0.;m=re.search(r'Tower\s*(\d+)',ob.name,re.I)
  if m:
   center=75*(-math.pi+int(m.group(1))*math.tau/36+math.pi/2);rigid=f(center)
  elif 'engaged round column'in ob.name:
   center=75*(-math.pi+(int(ob['bay'])+1)*math.tau/36+math.pi/2);rigid=f(center)
  mod=ob.modifiers.new('126 Three-arch group clearance','NODES');mod.node_group=g
  for prefix,M in [('World',ob.matrix_world),('Local',ob.matrix_world.inverted())]:
   for suf,value in [(str(i),tuple(M[i][k]for k in range(3)))for i in range(3)]+[('T',tuple(M.translation))]:
    socket=next(s for s in g.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'and s.name==prefix+suf);getattr(mod.properties.inputs,socket.identifier).value=value
  for name,value in [('Rigid',rigid),('Center',center)]:
   socket=next(s for s in g.interface.items_tree if s.item_type=='SOCKET'and s.in_out=='INPUT'and s.name==name);getattr(mod.properties.inputs,socket.identifier).value=value
  ob['126 grouped']=True;records.append({'object':ob.name,'rigid_tower_or_column':rigid>-10000})
 return {'source_period_m':L,'group_period_m':period,'circumference_change_percent':100*(period/L-1),'height_change':0,'wide_damaged_group':{'tower_boundaries':[10,13],'period_m':50.5,'outer_arch_half_width_m':75*math.tau/36*.34+.83,'reason':'Tier2 bay10 retained its larger damaged opening when125 ratio skipped its topology; dedicated actual-envelope allowance preserves it.'},'tower_half_envelope_authored_m':3.657,'reserved_side_gap_authored_m':clearance,'knots':list(zip(ks,vs)),'objects':records,'shared_deformation_group':g.name,'storage':'Existing mesh masters, prior modifiers, original-world paint attributes retained; one shared new position modifier, no remeshing.','seconds':time.time()-started}
if __name__=='__main__':
 O=R/'art/studies/coliseum-126/grouping';O.mkdir(parents=True,exist_ok=True);bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-125/scene.blend'));C=bpy.data.collections['110 Coliseum detailed front ruin'];a=apply(C);(O/'audit.json').write_text(json.dumps(a,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'));s=bpy.context.scene;s.render.use_freestyle=False
 for ob in bpy.data.objects:
  if 'Landmark contact ink'in ob.name:ob.hide_render=True
 s.render.resolution_x=1920;s.render.resolution_y=1443;s.render.resolution_percentage=100;s.render.use_border=False;s.render.filepath=str(O/'main.png');bpy.ops.render.render(write_still=True)
