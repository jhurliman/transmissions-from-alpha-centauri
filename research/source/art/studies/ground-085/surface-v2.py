"""Camera-readable compacted dirt: retained pigment plus clustered native mineral relief."""
import bpy,bmesh,math,random,json,sys
from mathutils import Vector,noise
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/ground-085';O.mkdir(exist_ok=True,parents=True)
def lin(v):
 v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def rgb(c):return tuple(lin(x) for x in c)+(1,)
def mineral(name,base):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();d=n.new('ShaderNodeBsdfDiffuse');d.inputs[0].default_value=(1,1,1,1);d.inputs['Roughness'].default_value=.7;sr=n.new('ShaderNodeShaderToRGB');l.new(d.outputs[0],sr.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(sr.outputs[0],bw.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.interpolation='LINEAR';cols=[(.18,[v*.46 for v in base]),(.34,[v*.68 for v in base]),(.62,base),(.88,[min(255,v*1.32) for v in base])]
 for i,(p,c) in enumerate(cols):
  e=r.color_ramp.elements[i] if i<2 else r.color_ramp.elements.new(p);e.position=p;e.color=rgb(c)
 scale=n.new('ShaderNodeMapRange');scale.clamp=True;scale.inputs['From Min'].default_value=.2;scale.inputs['From Max'].default_value=2.0;l.new(bw.outputs[0],scale.inputs[0]);l.new(scale.outputs[0],r.inputs[0]);gl=n.new('ShaderNodeBsdfGlossy');gl.inputs['Roughness'].default_value=.36;gr=n.new('ShaderNodeShaderToRGB');l.new(gl.outputs[0],gr.inputs[0]);gb=n.new('ShaderNodeRGBToBW');l.new(gr.outputs[0],gb.inputs[0]);g=n.new('ShaderNodeMapRange');g.clamp=True;g.inputs['From Min'].default_value=.22;g.inputs['From Max'].default_value=1.8;g.inputs['To Max'].default_value=.2;l.new(gb.outputs[0],g.inputs[0]);mix=n.new('ShaderNodeMixRGB');l.new(g.outputs[0],mix.inputs[0]);l.new(r.outputs[0],mix.inputs[1]);mix.inputs[2].default_value=rgb((142,113,81));e=n.new('ShaderNodeEmission');l.new(mix.outputs[0],e.inputs[0]);out=n.new('ShaderNodeOutputMaterial');l.new(e.outputs[0],out.inputs[0]);return m

def apply(s):
 rng=random.Random(85012);g=bpy.data.objects['Street foundation'];base=g.data.materials[0];m=base.copy();m.name='085 soil pigment with shallow granular relief';g.data.materials[0]=m
 n=m.node_tree.nodes;l=m.node_tree.links;em=next(q for q in n if q.type=='EMISSION');pigment=em.inputs[0].links[0].from_socket
 co=n.new('ShaderNodeNewGeometry');ns=n.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=5.7;ns.inputs['Detail'].default_value=2.2;ns.inputs['Roughness'].default_value=.7;l.new(co.outputs['Position'],ns.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=.029;b.inputs['Strength'].default_value=.65;l.new(ns.outputs['Fac'],b.inputs['Height']);dp=n.new('ShaderNodeVectorMath');dp.operation='DOT_PRODUCT';dp.inputs[1].default_value=(.47,-.55,.69);l.new(b.outputs['Normal'],dp.inputs[0]);mp=n.new('ShaderNodeMapRange');mp.clamp=True;mp.inputs['From Min'].default_value=.2;mp.inputs['From Max'].default_value=.95;mp.inputs['To Min'].default_value=.64;mp.inputs['To Max'].default_value=1.31;l.new(dp.outputs['Value'],mp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.6;l.new(pigment,mix.inputs[1]);l.new(mp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],em.inputs[0])
 C=bpy.data.collections.new('085 Compacted soil granular relief');s.collection.children.link(C)
 materials=[mineral('085 earth mineral '+str(i),c) for i,c in enumerate([(74,54,41),(86,63,46),(58,43,34),(104,80,57),(68,52,43)])]
 verts=[];faces=[];mi=[];count=0;centers=[(rng.uniform(-7.6,7.6),rng.uniform(-9,33),rng.uniform(.25,1.7),rng.uniform(.2,.9)) for _ in range(105)]
 for i in range(26500):
  if rng.random()<.7:
   cx,cy,rx,ry=rng.choice(centers);x=rng.gauss(cx,rx);y=rng.gauss(cy,ry)
  else:x=rng.uniform(-7.8,7.8);y=rng.uniform(-9.5,34)
  if abs(x)>7.8 or y<-9.8 or y>34 or abs(x)<.72 and -2.5<y<1:continue
  nval=noise.noise(Vector((x*.45,y*.45,3.2)));accept=max(.2,min(.93,.59+nval*.8))
  if rng.random()>accept:continue
  hit,loc,norm,idx=g.ray_cast(Vector((x,y,.4)),Vector((0,0,-1)))
  if not hit:continue
  z=loc.z
  u=rng.random();r=rng.uniform(.012,.032) if u<.76 else rng.uniform(.032,.065) if u<.985 else rng.uniform(.065,.10)
  h=r*rng.uniform(.32,.75);N=rng.choice([4,5,6]);angle=rng.random()*math.tau;elong=rng.uniform(.65,1.6);cidx=rng.choices(range(5),[3,2,5,1,3])[0];start=len(verts)
  for j in range(N):
   a=j*math.tau/N+rng.uniform(-.16,.16);rr=r*rng.uniform(.68,1.15);xx=math.cos(a)*rr;yy=math.sin(a)*rr*elong;verts.append((x+xx*math.cos(angle)-yy*math.sin(angle),y+xx*math.sin(angle)+yy*math.cos(angle),z-.004+rng.uniform(0,.003)))
  verts.append((x+r*.1,y-r*.2,z+h));peak=start+N
  for j in range(N):faces.append((start+j,start+(j+1)%N,peak));mi.append(cidx)
  count+=1
 me=bpy.data.meshes.new('085 clustered low angular grains');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);C.objects.link(ob)
 for ma in materials:me.materials.append(ma)
 for p,i in zip(me.polygons,mi):p.material_index=i
 for ls in s.view_layers[0].freestyle_settings.linesets:
  if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
   if C.name not in ls.collection.children:ls.collection.children.link(C)
 return {'native_grains':count,'faces':len(faces),'grain_radius_m':[.013,.13],'retained_base_pigment':base.name,'priority':'open ground surface; cracks currently baseline for isolation'}
if __name__=='__main__':
 bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/cloud-084/scene.blend'));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=4;stats=apply(s);(O/'surface-audit.json').write_text(json.dumps(stats,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'surface-scene.blend'));s.render.filepath=str(O/'surface-main.png');bpy.ops.render.render(write_still=True)
