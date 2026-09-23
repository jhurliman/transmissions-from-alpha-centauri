"""Native fracture-plane rock masters. Coordinates XY centered; contact Z=0.
create_rock(name,family,seed,dimensions) -> bpy Object (unassigned material).
Broad unequal fracture faces, sparse clipped corners, no triangulated cube noise.
"""
import bpy, bmesh, random, math
from mathutils import Vector
FAMILIES=('wedge','slab','shard','chunk','splinter')

def clip(faces,n,d):
    n=Vector(n).normalized(); out=[]; crossings=[]
    for poly in faces:
        q=[]
        for a,b in zip(poly,poly[1:]+poly[:1]):
            da=n.dot(a)-d; db=n.dot(b)-d
            if da<=1e-7:q.append(a)
            if (da<0)!=(db<0):
                p=a+(b-a)*(da/(da-db));q.append(p);crossings.append(p)
        if len(q)>=3:out.append(q)
    points=[]
    for p in crossings:
        if not any((p-v).length<1e-6 for v in points):points.append(p)
    if len(points)>2:
        c=sum(points,Vector())/len(points);u=(points[0]-c).normalized();v=n.cross(u)
        points.sort(key=lambda p:math.atan2((p-c).dot(v),(p-c).dot(u)))
        out.append(points)
    return out

def create_rock(name,family='wedge',seed=0,dimensions=(.4,.3,.16)):
    if family not in FAMILIES:raise ValueError(family)
    r=random.Random(seed);s=3
    v=[Vector((x,y,z)) for x,y,z in [(-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s),(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)]]
    faces=[[v[i] for i in ids] for ids in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]]
    count=r.choice([5,6,7]); phase=r.uniform(-.3,.3)
    planes=[]
    for j in range(count):
        a=phase+2*math.pi*j/count+r.uniform(-.12,.12)
        # Slightly inclined fracture walls; irregular perimeter rather than a prism.
        planes.append(((math.cos(a),math.sin(a),r.uniform(-.12,.27)),r.uniform(.73,1.06)))
    planes.append(((0,0,-1),0))
    if family=='wedge':
        planes += [((.57+r.uniform(-.12,.12),.13,1),.69),((-.85,.12,1),.72),((.1,-.72,1),.91)]
    elif family=='slab':
        planes += [((.10,.19,1),.43),((-.30,-.48,1),.64),((.7,.36,1),.80)]
    elif family=='shard':
        planes += [((.37,.22,1),.55),((-.61,-.18,1),.66),((.23,-.83,1),.88)]
    elif family=='chunk':
        planes += [((.27,.20,1),.96),((-.69,.37,1),1.0),((.3,-.64,1),.95)]
    else:
        planes += [((.18,.36,1),.54),((-.57,-.22,1),.54),((.19,-.82,1),.71)]
    for n,d in planes:faces=clip(faces,n,d)
    # Local secondary fractures remove only 2–3 selected corners, not every edge.
    for j in range(r.choice([2,3])):
        candidates=[p for f in faces for p in f if p.z>.13]
        if not candidates:break
        p=r.choice(candidates);n=Vector((p.x*.65,p.y*.65,.6+r.random()*.5)).normalized()
        support=max(n.dot(v) for f in faces for v in f)
        faces=clip(faces,n,support-r.uniform(.025,.07))
    verts=[];lookup={};polys=[]
    for f in faces:
        ids=[]
        for p in f:
            key=tuple(round(t,7) for t in p)
            if key not in lookup:lookup[key]=len(verts);verts.append(list(p))
            ids.append(lookup[key])
        if len(set(ids))>=3:polys.append(ids)
    mn=[min(p[i] for p in verts) for i in range(3)];mx=[max(p[i] for p in verts) for i in range(3)]
    for p in verts:
        for i in range(3):p[i]=(p[i]-mn[i])/(mx[i]-mn[i])*dimensions[i]-(dimensions[i]/2 if i<2 else 0)
    mesh=bpy.data.meshes.new(name+' fracture mesh');mesh.from_pydata(verts,[],polys);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-5);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
    ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    ob['rock_family']=family;ob['rock_seed']=seed;ob['construction']='Unequal planar fracture volumes with selective corner losses';ob['contact_base_z']=0.
    return ob

def catalogue():
    from pathlib import Path
    out=Path(__file__).resolve().parents[1]/'art/studies/rocks-090';out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    mat=bpy.data.materials.new('Neutral matte rock clay');mat.diffuse_color=(.32,.32,.32,1);mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.83
    dims={'wedge':(.9,.66,.35),'slab':(1.0,.58,.24),'shard':(1.1,.40,.29),'chunk':(.75,.65,.52),'splinter':(1.0,.31,.22)}
    for row,fam in enumerate(FAMILIES):
        for col in range(3):
            ob=create_rock(f'090 {fam} {col+1}',fam,90100+row*61+col*13,dims[fam]);ob.location=((col-1)*1.65,(2-row)*1.2,0);ob.rotation_euler.z=.15*(col-1);ob.data.materials.append(mat)
    bpy.ops.mesh.primitive_plane_add(size=200);ground=bpy.context.object;ground.name='Catalogue neutral ground';ground.location.z=-.015
    gm=mat.copy();gm.name='Neutral background';gm.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.19,.19,.19,1);ground.data.materials.append(gm)
    world=bpy.data.worlds.new('Neutral world');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes.get('Background').inputs[0].default_value=(.15,.15,.15,1);world.node_tree.nodes.get('Background').inputs[1].default_value=.5
    bpy.ops.object.light_add(type='AREA',location=(-3,-1,7));bpy.context.object.data.energy=1000;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=4
    bpy.ops.object.camera_add(location=(5,-8,10));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=8.0
    sc=bpy.context.scene;sc.camera=cam;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.resolution_x=1400;sc.render.resolution_y=1400;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX';sc.render.filepath=str(out/'catalog.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'catalog.blend'));bpy.ops.render.render(write_still=True)
if __name__=='__main__':catalogue()
