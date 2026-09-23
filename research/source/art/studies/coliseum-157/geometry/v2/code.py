"""157 connected upper-right cornice course failure; native subtraction only.
Apply to the local156 landmark collection; no arches/columns or other objects.
"""
import bpy,bmesh
from types import SimpleNamespace
from mathutils import Vector,geometry
from mathutils.bvhtree import BVHTree
from coliseum_crown_repair_123 import topology,strict_crossings
TARGETS=['COL110 T2 band10 profile'+str(i)for i in range(5)]+['COL110 T2 band11 profile'+str(i)for i in range(4)]+['COL110 U10 sill wall','COL110 U11 sill wall']

def robust_crossings(ob,details=False):
    """Float64 geometric predicate; invariant to winding/cyclic corner order."""
    import numpy as np
    me=ob.data;me.calc_loop_triangles();M=np.array(ob.matrix_world,dtype=np.float64)
    vv=np.array([list(v.co)+[1.]for v in me.vertices],dtype=np.float64)@M.T;vv=vv[:,:3]
    fs=[tuple(t.vertices)for t in me.loop_triangles]
    tree=BVHTree.FromPolygons([Vector(v)for v in vv],fs,all_triangles=True);result=[]
    for i,j in tree.overlap(tree):
        if i>=j or set(fs[i])&set(fs[j]):continue
        A=vv[list(fs[i])];B=vv[list(fs[j])]
        na=np.cross(A[1]-A[0],A[2]-A[0]);nb=np.cross(B[1]-B[0],B[2]-B[0]);la=np.linalg.norm(na);lb=np.linalg.norm(nb)
        if la<1e-10 or lb<1e-10 or abs(np.dot(na/ la,nb/lb))>.99999:continue
        found=False
        for V,W in [(A,B),(B,A)]:
            e0=W[1]-W[0];e1=W[2]-W[0];n=np.cross(e0,e1);n/=np.linalg.norm(n)
            for k in range(3):
                a=V[k];b=V[(k+1)%3];d=b-a;length=np.linalg.norm(d);d0=np.dot(a-W[0],n);d1=np.dot(b-W[0],n)
                if not min(d0,d1)<-1e-5 or not max(d0,d1)>1e-5 or length<1e-8:continue
                t=d0/(d0-d1)
                if not 1e-5<t*length<length-1e-5:continue
                q=a+t*d-W[0];aa=np.dot(e0,e0);bb=np.dot(e0,e1);cc=np.dot(e1,e1);dd=np.dot(q,e0);ee=np.dot(q,e1);den=aa*cc-bb*bb
                if abs(den)<1e-20:continue
                u=(cc*dd-bb*ee)/den;v=(aa*ee-bb*dd)/den
                if min(u,v,1-u-v)>1e-5:found=True;break
            if found:break
        if found:result.append({'pair':[i,j],'plane_endpoint_signed_distances_world':[float(d0),float(d1)],'triangles_world':[A.tolist(),B.tolist()]}if details else[i,j])
    return result

def checked_topology(ob):
    d=topology(ob);d['legacy_float32_crossings']=d['strict_crossings'];d['strict_crossings']=len(robust_crossings(ob));d['crossing_predicate']='float64 segment/triangle, original tolerances';return d

def freeze_render_triangles(old):
    old.calc_loop_triangles();expected={tuple(sorted(t.vertices))for t in old.loop_triangles};coords=[tuple(v.co)for v in old.vertices]
    normals={(p.index,old.loops[k].vertex_index):tuple(old.corner_normals[k].vector)for p in old.polygons for k in p.loop_indices}
    new=old.copy();tag=new.attributes.new('157 temporary parent face','INT','FACE')
    for i,d in enumerate(tag.data):d.value=i
    bm=bmesh.new();bm.from_mesh(new);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    for face in list(bm.faces):
        ids=[v.index for v in face.verts]
        quad='ALTERNATE' if len(ids)==4 and tuple(sorted(ids[:3]))not in expected else 'FIXED'
        bmesh.ops.triangulate(bm,faces=[face],quad_method=quad,ngon_method='EAR_CLIP')
    bm.to_mesh(new);bm.free();new.update()
    if {tuple(sorted(p.vertices))for p in new.polygons}!=expected or [tuple(v.co)for v in new.vertices]!=coords:raise RuntimeError('Source render triangulation mismatch')
    parents=[d.value for d in new.attributes['157 temporary parent face'].data];ns=[normals[(parents[p.index],new.loops[k].vertex_index)]for p in new.polygons for k in p.loop_indices];new.normals_split_custom_set(ns);new.attributes.remove(new.attributes['157 temporary parent face'])
    return new

def prepare_source(me,name):
    me=freeze_render_triangles(me)
    if name!='COL110 U10 sill wall':return me
    # Source render tessellation includes one opposite-winding duplicate pair.
    # Remove that zero-volume internal double cover, preserving all live coords.
    normals={tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices)):{tuple(me.vertices[me.loops[k].vertex_index].co):me.corner_normals[k].vector.copy()for k in p.loop_indices}for p in me.polygons}
    bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();groups={}
    for f in bm.faces:groups.setdefault(tuple(sorted(v.index for v in f.verts)),[]).append(f)
    pairs=[fs for fs in groups.values()if len(fs)==2 and fs[0].normal.dot(fs[1].normal)<-.99999]
    if len(pairs)!=1:raise RuntimeError('Unexpected U10 duplicate-pair normalization')
    bmesh.ops.delete(bm,geom=[f for fs in pairs for f in fs],context='FACES_ONLY');loose=[e for e in bm.edges if not e.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='EDGES')
    bm.to_mesh(me);bm.free();me.update();custom=[]
    for p in me.polygons:
        key=tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices))
        custom.extend(normals[key][tuple(me.vertices[me.loops[k].vertex_index].co)]for k in p.loop_indices)
    me.normals_split_custom_set(custom);return me

def apply(C):
    dg=bpy.context.evaluated_depsgraph_get();rows=[]
    core=next(m for m in bpy.data.materials if m.name.startswith('151 Warm violet exposed masonry core') and not m.library)
    for name in TARGETS:
        ob=C.objects[name];ev=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(ev,depsgraph=dg);me=prepare_source(me,name);M=ob.matrix_world.copy();iv=M.inverted();src=[v.co.copy()for v in me.vertices];me.calc_loop_triangles();tris=[tuple(t.vertices)for t in me.loop_triangles];attrs=[v.vector.copy()for v in me.attributes['115 Original world position'].data]
        normals={tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices)):{tuple(me.vertices[me.loops[k].vertex_index].co):me.corner_normals[k].vector.copy()for k in p.loop_indices}for p in me.polygons}
        tree=BVHTree.FromPolygons(src,tris,all_triangles=True);tmp=bpy.data.objects.new('157 temporary evaluated',me);C.objects.link(tmp);tmp.matrix_world=M;before=checked_topology(SimpleNamespace(data=tmp.data,matrix_world=M));baseline_pairs=robust_crossings(SimpleNamespace(data=tmp.data,matrix_world=M),True)
        if before['nonmanifold']:raise RuntimeError('Unsafe157source '+name+str(before))
        if before['strict_crossings']:
            import json
            from pathlib import Path
            (Path(__file__).resolve().parents[1]/'art/studies/coliseum-157/geometry/float64-source.json').write_text(json.dumps({'object':name,'topology':before,'crossings':baseline_pairs},indent=2))
        original_materials=list(me.materials);temporary_materials=[];material_restore={i:i for i in range(len(original_materials))}
        source_tri_normals=[[me.corner_normals[k].vector.copy()for k in t.loops]for t in me.loop_triangles];cut_trees=[];lower_part=None
        # Common camera-mapped world frame. Course projections step backward
        # independently; the central loss removes projection fully, shoulders
        # retain unequal connected course tails. No replacement rubble is added.
        if 'profile' in name:
            layer=int(name.rsplit('profile',1)[1]);spec={
                0:(18.3,19.0,21.0,24.7,2.20),
                1:(17.4,18.0,24.0,26.0,.00),
                2:(18.0,18.4,23.2,25.2,1.05),
                3:(17.1,17.9,25.4,27.3,-1.03),
                4:(17.9,18.4,23.3,25.0,2.20)}[layer]
            lo,left,right,hi=spec[:4];xs=[lo,lo+(left-lo)*.45,left,left+.22,right-.17,right,right+(hi-right)*.70,hi];offset=spec[4]
            heights=[((M@v.co).z)for v in me.vertices];lows=[min(heights)-.05]*len(xs);highs=[max(heights)+.05]*len(xs)
            depths=[.08,.45,.70,6.7,6.0,.85,.30,.06]if layer==3 else[.08,.45,.70,5.2,4.7,.85,.30,.06]
        else:
            xs=[18.65,19.02,20.15,21.25,22.05];offset=4.5
            lows=[41.20]*5;highs=[41.68,42.42,43.55,43.08,41.75];depths=[.08,.85,1.85,.85,.05]
        verts=[]
        for back in [False,True]:
            for high in [False,True]:
                for i,x in enumerate(xs):
                    z=highs[i]if high else lows[i];front=.03033*x*x-.10493*x+195.9346+offset
                    y=front+(depths[i]if back else-6.)
                    verts.append(iv@Vector((x,y,z)))
        n=len(xs);faces=[]
        # Four long surfaces are split only at authored changes of direction.
        for i in range(n-1):
            faces.extend([(i,i+1,n+i+1,n+i),(2*n+i,3*n+i,3*n+i+1,2*n+i+1),(i,2*n+i,2*n+i+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)])
        faces.extend([(0,n,3*n,2*n),(n-1,3*n-1,4*n-1,2*n-1)])
        cm=bpy.data.meshes.new('157 connected course loss cutter');cm.from_pydata(verts,[],faces);bm=bmesh.new();bm.from_mesh(cm);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cm);bm.free();cm.calc_loop_triangles()
        cut_trees.append(BVHTree.FromPolygons([v.co.copy()for v in cm.vertices],[tuple(t.vertices)for t in cm.loop_triangles],all_triangles=True));co=bpy.data.objects.new('157 temporary cutter',cm);C.objects.link(co);co.matrix_world=M
        mod=tmp.modifiers.new('157 remove interrupted course projection','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=co;bpy.context.view_layer.objects.active=tmp;tmp.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(co,do_unlink=True)
        print('157 cut',name,flush=True)
        me=tmp.data;me.update();restored_indices=[material_restore.get(p.material_index,0)for p in me.polygons];me.materials.clear()
        for material in original_materials:me.materials.append(material)
        for p,material_index in zip(me.polygons,restored_indices):p.material_index=material_index
        for material in temporary_materials:bpy.data.materials.remove(material)
        audit_ob=SimpleNamespace(data=tmp.data,matrix_world=M);after=checked_topology(audit_ob);candidate_pairs=robust_crossings(audit_ob,True)
        def pair_keys(rows):return {tuple(sorted(tuple(sorted(tuple(v)for v in t))for t in q['triangles_world']))for q in rows}
        new_pair_keys=pair_keys(candidate_pairs)-pair_keys(baseline_pairs);after['new_strict_crossings']=len(new_pair_keys)
        if after['strict_crossings']:
            import json
            from pathlib import Path
            (Path(__file__).resolve().parents[1]/'art/studies/coliseum-157/geometry/float64-candidate.json').write_text(json.dumps({'object':name,'topology':after,'crossings':candidate_pairs},indent=2))
        if after['nonmanifold']or new_pair_keys or not 0<after['volume']<before['volume']:
            import json
            from pathlib import Path
            me.calc_loop_triangles();pairs=strict_crossings(audit_ob,True);details=[{'pair':pair,'triangles':[{'polygon':me.loop_triangles[i].polygon_index,'world':[list(M@me.vertices[v].co)for v in me.loop_triangles[i].vertices],'exact_source_triangle':tuple(sorted(tuple(me.vertices[v].co)for v in me.loop_triangles[i].vertices))in {tuple(sorted(tuple(src[j])for j in tri))for tri in tris}}for i in pair]}for pair in pairs]
            (Path(__file__).resolve().parents[1]/'art/studies/coliseum-157/geometry/crossing-failure.json').write_text(json.dumps({'object':name,'before':before,'after':after,'details':details},indent=2))
            raise RuntimeError('Rejected157cut '+name+str(after))
        me.calc_loop_triangles();envelope=[v.co.copy()for v in me.vertices]+[sum((me.vertices[i].co for i in t.vertices),Vector())/3 for t in me.loop_triangles];outward=[];violations=[]
        for p in envelope:
            q,n,idx,dist=tree.find_nearest(p)
            if dist>1e-5 and (p-q).dot(n)>1e-5:
                outward.append((p-q).dot(n));violations.append({'sample':list(M@p),'nearest':list(M@q),'distance':dist,'outward':(p-q).dot(n),'source_triangle':[list(M@src[i])for i in tris[idx]],'retained_vertex':tuple(p)in {tuple(v)for v in src}})
        # Nearest-face normal is not a signed distance at concave corners.
        # Certify points off the original surface using ray parity; resolve
        # rare grazing disagreements with oriented solid-angle winding.
        import math
        retained_coords={tuple(p)for p in src};source_triangle_keys={tuple(sorted(tuple(src[i])for i in tri))for tri in tris}
        certificate_samples=[v.co.copy()for v in me.vertices if tuple(v.co)not in retained_coords]
        certificate_samples += [sum((me.vertices[i].co for i in t.vertices),Vector())/3 for t in me.loop_triangles if tuple(sorted(tuple(me.vertices[i].co)for i in t.vertices))not in source_triangle_keys]
        containment=[];outside=[];numeric_residuals=[]
        from bpy_extras.object_utils import world_to_camera_view
        scene=bpy.context.scene;camera=scene.camera
        for p in certificate_samples:
            if tree.find_nearest(p)[3]<=1e-4:continue
            counts=[]
            for direction in [(0.872,.319,.371),(-.423,.873,.239),(.197,-.527,.826)]:
                direction=Vector(direction).normalized();q=p.copy();count=0
                for guard in range(200):
                    hit=tree.ray_cast(q,direction,1000.)
                    if hit[0]is None:break
                    count+=1;q=hit[0]+direction*1e-5
                counts.append(count)
            parities=[k%2 for k in counts];winding=None
            if len(set(parities))==1:inside=bool(parities[0])
            else:
                angle=0.
                for triangle in tris:
                    a,b,c=[src[i]-p for i in triangle];la,lb,lc=a.length,b.length,c.length
                    angle+=2*math.atan2(a.dot(b.cross(c)),la*lb*lc+a.dot(b)*lc+b.dot(c)*la+c.dot(a)*lb)
                winding=angle/(4*math.pi);inside=abs(winding)>.5
            row={'world':list(M@p),'ray_counts':counts,'winding_on_disagreement':winding,'inside':inside};containment.append(row)
            if not inside:
                near=tree.find_nearest(p)[0];world_distance=(M@p-M@near).length;a=world_to_camera_view(scene,camera,M@p);b=world_to_camera_view(scene,camera,M@near);pixel_distance=((a.x-b.x)**2*3840**2+(a.y-b.y)**2*2885**2)**.5;row.update(world_distance=world_distance,native_pixel_distance=pixel_distance)
                if world_distance<=.0005 and pixel_distance<=.02:numeric_residuals.append(row)
                else:outside.append(row)
        if outside:
            import json
            from pathlib import Path
            (Path(__file__).resolve().parents[1]/'art/studies/coliseum-157/geometry/containment-failure.json').write_text(json.dumps({'object':name,'outside':outside},indent=2))
            raise RuntimeError('Outside157source by parity/winding '+name+str(len(outside)))
        result=BVHTree.FromPolygons([v.co.copy()for v in me.vertices],[tuple(t.vertices)for t in me.loop_triangles],all_triangles=True)
        lower=[result.find_nearest(p)[3]for p in src if (M@p).z<40.25]
        aa=me.attributes['115 Original world position'];retained={tuple(v)for v in src};newverts=[]
        for v in me.vertices:
            if tuple(v.co)in retained:continue
            p,n,idx,dist=tree.find_nearest(v.co);tri=tris[idx];aa.data[v.index].vector=geometry.barycentric_transform(p,*[src[i]for i in tri],*[attrs[i]for i in tri]);newverts.append(list(M@v.co))
        tag=me.attributes.get('157 Exposed course core')or me.attributes.new('157 Exposed course core','FLOAT','FACE');oldcore=me.attributes.get('117 Exposed core')or me.attributes.new('117 Exposed core','FLOAT','FACE');me.materials.append(core);slot=len(me.materials)-1;custom=[x.vector.copy()for x in me.corner_normals];newfaces=[]
        for p in me.polygons:
            key=tuple(sorted(tuple(me.vertices[i].co)for i in p.vertices));center=sum((me.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);near=tree.find_nearest(center)[0];source_offset_world=(M@center-M@near).length;on_cutter=min((M@center-M@ct.find_nearest(center)[0]).length for ct in cut_trees)<.0001;exposed=on_cutter and source_offset_world>.0005;tag.data[p.index].value=float(exposed)
            if exposed:p.material_index=slot;oldcore.data[p.index].value=1.;newfaces.append(p.index)
            for li in p.loop_indices:
                point=me.vertices[me.loops[li].vertex_index].co;q=tuple(point)
                if key in normals:custom[li]=normals[key][q]
                elif exposed:custom[li]=p.normal.copy()
                else:
                    nearest,normal,idx,dist=tree.find_nearest(point);tri=tris[idx];custom[li]=geometry.barycentric_transform(nearest,*[src[i]for i in tri],*source_tri_normals[idx]).normalized()
        me.normals_split_custom_set(custom);ob.data=me
        for mod in list(ob.modifiers):ob.modifiers.remove(mod)
        bpy.data.objects.remove(tmp,do_unlink=True);ob['157 connected cornice failure']='Unequal course terminations and attached upward sill loss; no added fragments'
        rows.append({'object':name,'before':before,'after':after,'removed_volume':before['volume']-after['volume'],'nearest_normal_proxy_max_positive_local':max(outward,default=0),'source_containment_outside_count':len(outside),'accepted_numeric_residuals':numeric_residuals,'numeric_budget_world_m':.0005,'numeric_budget_native_px':.02,'exact_inherited_surface_samples':len(envelope)-len(certificate_samples),'source_containment_surface_tolerance_local':1e-4,'off_surface_parity_winding_checks':containment,'protected_below_world_z40_25_surface_max_error':max(lower,default=0),'retained_old_vertices':sum(tuple(v.co)in retained for v in me.vertices),'original_vertex_count':len(src),'source_render_triangles_bit_exact_except_canceling_pair':True,'source_normalization':'Removed one opposite-winding duplicate triangle pair of zero net volume; all surviving positions unchanged'if name=='COL110 U10 sill wall'else'Exact render triangulation','source_vertices_bit_exact':True,'lower_part_isolated_during_boolean':lower_part is not None,'new_vertices_world':newverts,'new_exposed_face_ids':newfaces,'core_material':core.name,'new_core_attr':'157 Exposed course core'})
    return {'source':'156','targets':rows,'operation':'Native DIFFERENCE only; stepped projecting courses with retained attached returns','references':['UCL-01','UCL-02','DP-03'],'no_constructive_additions':True}
