"""Three sparse fracture families following native curved tread and riser faces."""
import bpy
from mathutils import Vector

def apply(scene):
    assert not scene.get('249 sparse step fracture ink')
    col=bpy.data.collections.new('249 Native step fracture geometry');scene.collection.children.link(col)
    ink=bpy.data.collections.new('249 Sparse step fracture ink targets');ink.use_fake_user=True
    mat=bpy.data.materials.new('249 Hairline weathered stone fracture');mat.diffuse_color=(.09,.06,.06,1);mat.use_nodes=True
    ns=mat.node_tree.nodes;ns.clear();e=ns.new('ShaderNodeEmission');e.inputs[0].default_value=(.09,.06,.06,1);out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(e.outputs[0],out.inputs['Surface'])
    rows=[];objects=[]
    families=[(-8.2,[2,3,4,5]),(3.7,[1,2,3]),(12.1,[3,4,5])]
    def sample(o,ring,x):
        n=len(o.data.vertices)//4;points=[o.matrix_world@v.co for v in o.data.vertices[ring*n:(ring+1)*n]]
        for a,b in zip(points,points[1:]):
            if min(a.x,b.x)<=x<=max(a.x,b.x):return a.lerp(b,(x-a.x)/(b.x-a.x))
        raise RuntimeError(('249 crack x out of range',o.name,x))
    for fi,(x,ks) in enumerate(families):
      for k in ks:
        o=bpy.data.objects[f'COL228 Ground curved step{k} of5'];center=x+(.11 if k%2 else -.08)*(fi+1)
        back=sample(o,2,center);front=sample(o,3,center)
        # Natural zigzags cross the top; matching riser path folds over the lip.
        ps=[]
        for t,dx in [(0,.03),(.28,-.055),(.59,.07),(.82,-.025),(1,0)]:
            a=sample(o,2,center+dx);b=sample(o,3,center+dx);p=a.lerp(b,t);p.z+=.009;ps.append(p)
        outward=front-back;outward.z=0;outward.normalize()
        # Lower visible riser ends at next lower tread; native visibility handles overlaps.
        low=sample(o,3,center).z
        if k>1:low=sample(bpy.data.objects[f'COL228 Ground curved step{k-1} of5'],2,center).z+.012
        else:low=sample(o,1,center).z+.055
        for t,dx in [(.35,.035),(.68,-.02),(1,.045)]:
            p=sample(o,3,center+dx)+outward*.012;p.z=front.z+(low-front.z)*t;ps.append(p)
        vs=[];fs=[]
        for a,b in zip(ps,ps[1:]):
            q=len(vs);side=Vector((.003,0,0));vs.extend([a,b,b+side,a+side]);fs.append((q,q+1,q+2,q+3))
        me=bpy.data.meshes.new(f'249 Step fracture F{fi} C{k}');me.from_pydata(vs,[],fs);me.update();me.materials.append(mat)
        marks=me.attributes.new('freestyle_edge','BOOLEAN','EDGE')
        for edge in me.edges:
            a,b=edge.vertices
            if a//4==b//4 and {a%4,b%4}=={0,1}:marks.data[edge.index].value=True
        ob=bpy.data.objects.new(me.name,me);col.objects.link(ob);ink.objects.link(ob);objects.append(ob)
        rows.append({'object':ob.name,'course':k,'family':fi,'world_x':center,'path_points':[list(p)for p in ps]})
    for layer in scene.view_layers:
      for ls in layer.freestyle_settings.linesets:
        if ls.select_by_collection and ls.collection and ls.collection_negation=='EXCLUSIVE':
          for ob in objects:
            if ob.name not in ls.collection.objects:ls.collection.objects.link(ob)
    layer=scene.view_layers['215 Distant ink without atmospheric boundary'];ls=layer.freestyle_settings.linesets.new('249 Sparse step fracture marks');ls.select_by_collection=True;ls.collection=ink;ls.collection_negation='INCLUSIVE';ls.select_by_visibility=True;ls.visibility='VISIBLE';ls.select_by_edge_types=True
    for kind in ['silhouette','border','crease','ridge_valley','suggestive_contour','material_boundary','contour','external_contour','edge_mark']:
      if hasattr(ls,'select_'+kind):setattr(ls,'select_'+kind,False)
    ls.select_edge_mark=True;ls.edge_type_combination='OR';ls.linestyle.thickness=.55;ls.linestyle.color=(.09,.06,.06);ls.linestyle.alpha=.5
    scene['249 sparse step fracture ink']=True
    return {'families':3,'objects':rows,'line_width':.55,'line_alpha':.5,'existing_geometry_materials_fog_unchanged':True,'native_visibility':True,'review_required':True}
