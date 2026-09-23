"""Sparse painted distant facades on the user-selected 101A native massing."""
import bpy, json, math, random, hashlib, os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'art/studies/city-102';O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/city-101/A/scene.blend'));s=bpy.context.scene
C=bpy.data.collections['101 Original city layout study']
records=json.loads((R/'art/studies/city-101/A/reconstruction.json').read_text())['masses']

def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def rgb(h):return [int(h.lstrip('#')[i:i+2],16)/255 for i in (0,2,4)]
def rgba(c):return tuple(lin(max(0,min(1,v))) for v in c)+(1,)
def scale(c,k):return [v*k for v in c]
def blend(a,b,f):return [x*(1-f)+y*f for x,y in zip(a,b)]
def material(mid,kind,col,seed,marks=0,spec=False,spec_strength=.58,spec_span=None):
 rng=random.Random(seed);m=bpy.data.materials.new('CITY102 '+mid+' '+kind);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
 def node(t,label=None):
  q=n.new(t)
  if label:q.label=label
  return q
 def mathnode(op,a,b=0):
  q=node('ShaderNodeMath');q.operation=op
  for i,v in enumerate((a,b)):
   if isinstance(v,(int,float)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 def mix(f,a,b):
  q=node('ShaderNodeMixRGB')
  for i,v in enumerate((f,a,b)):
   if isinstance(v,(float,int,tuple,list)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 out=node('ShaderNodeOutputMaterial');em=node('ShaderNodeEmission');l.new(em.outputs[0],out.inputs[0]);g=node('ShaderNodeNewGeometry');dot=node('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=(.38,-.67,.64);l.new(g.outputs['Normal'],dot.inputs[0]);r=node('ShaderNodeValToRGB','Two broad painted light families');r.color_ramp.interpolation='CONSTANT';r.color_ramp.elements[0].position=0;r.color_ramp.elements[0].color=rgba(scale(col,.81));r.color_ramp.elements[1].position=.5;r.color_ramp.elements[1].color=rgba(col);l.new(dot.outputs['Value'],r.inputs[0]);color=r.outputs[0]
 if marks:
  tex=node('ShaderNodeTexCoord');sep=node('ShaderNodeSeparateXYZ');l.new(tex.outputs['Generated'],sep.inputs[0]);noise=node('ShaderNodeTexNoise','Quiet underpainting and worn stamp edges');noise.inputs['Scale'].default_value=26;noise.inputs['Detail'].default_value=1.1;noise.inputs['Roughness'].default_value=.6;l.new(tex.outputs['Generated'],noise.inputs['Vector']);warp=mathnode('MULTIPLY',mathnode('SUBTRACT',noise.outputs['Fac'],.5),.24)
  # Explicit irregular stamps avoid any floor/window lattice. Generated coordinates
  # attach the paint to native solids and work from every camera direction.
  centers=[]
  for k in range(marks):
   for attempt in range(40):
    cx=rng.uniform(.15,.84);cz=rng.uniform(.13,.89)
    if all(abs(cx-x)>.14 or abs(cz-z)>.10 for x,z in centers):break
   centers.append((cx,cz));wx=rng.uniform(.035,.075);wz=rng.uniform(.012,.028)
   dx=mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['X'],cx),wx);dz=mathnode('DIVIDE',mathnode('SUBTRACT',sep.outputs['Z'],cz),wz)
   skew=mathnode('MULTIPLY',dz,rng.uniform(-.22,.22));dx=mathnode('ABSOLUTE',mathnode('ADD',dx,skew));dz=mathnode('ABSOLUTE',dz)
   shape=mathnode('MAXIMUM',dx,dz)
   if k%3==0:
    shape=mathnode('MAXIMUM',shape,mathnode('MULTIPLY',mathnode('ADD',dx,dz),.68))
   shape=mathnode('ADD',shape,warp);mask=mathnode('LESS_THAN',shape,1)
   if k%3==0:
    dry=node('ShaderNodeTexNoise','Fragmented warm dry-brush pigment');dry.inputs['Scale'].default_value=95;dry.inputs['Detail'].default_value=1;l.new(tex.outputs['Generated'],dry.inputs[0]);holes=mathnode('GREATER_THAN',dry.outputs['Fac'],.55);mask=mathnode('MULTIPLY',mask,mathnode('SUBTRACT',1,mathnode('MULTIPLY',holes,.78)))
   # Keep marks off the roof: this pigment is on vertical wall faces only.
   ng=node('ShaderNodeSeparateXYZ');l.new(g.outputs['Normal'],ng.inputs[0]);vertical=mathnode('LESS_THAN',mathnode('ABSOLUTE',ng.outputs['Z']),.4);mask=mathnode('MULTIPLY',mask,vertical)
   if k%3==0:c=blend(col,rgb('aa8680'),.36)
   elif k%3==1:c=scale(col,.86)
   else:c=blend(col,rgb('888395'),.17)
   color=mix(mask,color,rgba(c))
  # Very low contrast surface pigment; no embossed noise or pinprick speckles.
  wash=node('ShaderNodeTexNoise','Broad quiet violet pigment');wash.inputs['Scale'].default_value=8;wash.inputs['Detail'].default_value=0;l.new(tex.outputs['Generated'],wash.inputs[0]);fac=mathnode('MULTIPLY',mathnode('LESS_THAN',wash.outputs['Fac'],.41),.035);color=mix(fac,color,rgba(scale(col,.8)))
 if spec:
  glossy=node('ShaderNodeBsdfGlossy','Actual scene-light and view dependent highlight');glossy.inputs['Color'].default_value=(.65,.65,.65,1);glossy.inputs['Roughness'].default_value=.34
  st=node('ShaderNodeShaderToRGB');l.new(glossy.outputs[0],st.inputs[0]);bw=node('ShaderNodeRGBToBW');l.new(st.outputs[0],bw.inputs[0]);ramp=node('ShaderNodeValToRGB','Restrained grouped specular catch');ramp.color_ramp.interpolation='EASE';ramp.color_ramp.elements[0].position=.018;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.20;ramp.color_ramp.elements[1].color=(spec_strength,spec_strength,spec_strength,1);l.new(bw.outputs[0],ramp.inputs[0]);sf=ramp.outputs[0]
  if spec_span:
   coord=node('ShaderNodeTexCoord');sp=node('ShaderNodeSeparateXYZ');l.new(coord.outputs['Generated'],sp.inputs[0]);inside=mathnode('MULTIPLY',mathnode('GREATER_THAN',sp.outputs['X'],spec_span[0]),mathnode('LESS_THAN',sp.outputs['X'],spec_span[1]));sf=mathnode('MULTIPLY',sf,inside)
  color=mix(sf,color,rgba(blend(col,rgb('c2a39c'),.69)))
 l.new(color,em.inputs[0]);m['reference']='UX-03';m['paint_stamps']=marks;m['actual_specular']=spec;return m

def mesh(name,vs,fs,m,mid):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(m);me.update();ob=bpy.data.objects.new('CITY102 '+mid+' '+name,me);C.objects.link(ob);ob['reference_mass']=mid;return ob

def box(name,loc,dims,m,mid):
 x,y,z=loc;a,b,c=[v/2 for v in dims];vs=[(x+i*a,y+j*b,z+k*c) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];return mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],m,mid)

removed=[];audits=[]
for index,rec in enumerate(records):
 mid=rec['id'];obs=sorted([o for o in C.objects if o.get('reference_mass')==mid],key=lambda o:o.name);seed=int(hashlib.sha256(mid.encode()).hexdigest()[:8],16);rng=random.Random(seed);col=rgb(rec['color_hex']);w,d,h=rec['dimensions'];x,y=rec['position'];low=rec['low'] or h<4.1
 body=next(o for o in obs if 'measured crown mass' in o.name or 'low single-story block' in o.name)
 # Preserve body vertices and transforms. Chamfer is an editable edge treatment.
 bodymat=material(mid,'quiet wall',col,seed,marks=(1 if low else rng.randint(5,8)))
 service=material(mid,'subtle raised details',scale(col,.92),seed+1)
 edge=material(mid,'exposed edge',blend(col,rgb('9a838d'),.22),seed+2,spec=True)
 shade=material(mid,'few recesses',scale(col,.78),seed+3)
 bevelmat=material(mid,'quiet masonry chamfer',col,seed+4,spec=True,spec_strength=.20)
 roofmat=material(mid,'selected roof catch',col,seed+5,spec=index%4==0,spec_strength=.32,spec_span=(.12,.56))
 body.data=body.data.copy();body.data.materials.clear();body.data.materials.append(bodymat)
 if not low:
  bevel=body.modifiers.new('102 restrained 45 degree masonry chamfer','BEVEL');bevel.width=min(.09,w*.034);bevel.segments=1;bevel.limit_method='ANGLE';bevel.angle_limit=.52;bevel.use_clamp_overlap=True;body.data.materials.append(bevelmat);bevel.material=1
 # The hundreds of grid parts and repeated story stripes are the regression.
 remove_tokens=['window recessed field','slider divider','sloping window kick','side window group','story trim','service strap','primary service loop','projecting receiver','tonal service strip']
 for ob in obs:
  if ob==body:continue
  kill=any(t in ob.name for t in remove_tokens)
  if 'closed service riser' in ob.name:kill=index%3!=0
  if 'chamfered corner pier' in ob.name:kill=True
  if kill:
   removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True);continue
  ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(shade if 'opening' in ob.name else service)
  if 'low roof rim' in ob.name:ob.data.materials[0]=roofmat
 if not low:
  vs=[body.matrix_world@v.co for v in body.data.vertices];front=min(v.y for v in vs)
  # Broken long chamfered corner rails, deliberately on one edge only. Each is
  # actual raised masonry with one broad face and a 45-degree inward return.
  side=-1 if index%4!=1 else 1
  spans=[(.16,.44),(.49,.80)] if index%3 else [(.22,.78)]
  q=min(w*.065,.20)
  for j,(lo,hi) in enumerate(spans):
   cx=x+side*(w*.5-q*.8);xa=cx-q*.5;xb=cx+q*.5;fy=front-.055;back=front+.025
   poly=[(xa,back),(xb,back),(xb,fy+q*.34),(xb-q*.34,fy),(xa,fy)]
   verts=[(xx,yy,z) for z in (h*lo,h*hi) for xx,yy in poly];N=len(poly);fs=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
   rail=mesh('broken corner return '+str(j),verts,fs,edge,mid)
  # One broad ledge/receiver, only on selected larger buildings, never a stack.
  if index%3==0:
   ledge=box('single weathered ledge',(x-w*.16,front-.08,h*.43),(w*.43,.17,min(.12,h*.025)),edge,mid)
   bevel=ledge.modifiers.new('45 degree ledge corner','BEVEL');bevel.width=.025;bevel.segments=1
 audits.append({'id':mid,'body':body.name,'paint_stamps':bodymat['paint_stamps'],'base_color':rec['color_hex'],'body_vertices_unchanged':True,'low':low,'specular':'Glossy BSDF -> scene-light response -> restrained paint color, limited to bevels/edge pieces'})
(O/'changes.json').write_text(json.dumps({'selected_layout':'101A','removed_grid_and_repeated_parts':len(removed),'removed':removed,'masses':audits,'preserved':['camera','body base mesh and transform','nearby scene','soil','rocks','sky','landmark'],'notes':'No projected artwork or new intersection-ink bake. Native attached material stamps and editable edge geometry.'},indent=2))
s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_freestyle=True;s.render.resolution_percentage=100;s.render.filepath=str(O/'main.png');bpy.ops.wm.save_as_mainfile(filepath=str(O/'scene.blend'))
if os.environ.get('CITY_PREVIEW')=='1':
 s.render.use_freestyle=False;s.render.resolution_percentage=100;s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=540/1440;s.render.border_max_x=960/1440;s.render.border_min_y=1-490/1082;s.render.border_max_y=1-260/1082;s.render.filepath=str(O/'preview-city.png')
bpy.ops.render.render(write_still=True)
