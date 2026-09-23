"""099: linked editable skyline infill; preserves existing towers and camera."""
import random
from collections import defaultdict
import bpy
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

def apply(scene=None):
    scene = scene or bpy.context.scene
    rng = random.Random(9907519)
    groups = defaultdict(list)
    for ob in scene.objects:
        if ob.name.startswith('FAR075 ') and ob.get('far_layer') is not None and not ob.hide_render:
            key = tuple(round(v, 5) for row in ob.matrix_world for v in row)
            groups[key].append(ob)
    records = []
    for obs in groups.values():
        points = [ob.matrix_world @ Vector(p) for ob in obs for p in ob.bound_box]
        lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
        hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
        records.append(dict(obs=obs, lo=lo, hi=hi, center=(lo+hi)/2, layer=int(obs[0]['far_layer'])))
    records.sort(key=lambda r:(r['layer'], r['center'].x))
    coll = bpy.data.collections.new('099 Distant city infill')
    scene.collection.children.link(coll)
    additions=[]
    gap_reports=[]
    for layer in sorted({r['layer'] for r in records}):
        row=[r for r in records if r['layer']==layer]
        row_new=[]
        for sign in [-1, 1]:
            side=sorted([r for r in row if r['center'].x*sign>0],key=lambda r:abs(r['center'].x))
            for i, src in enumerate(side):
                c=src['center']; width=src['hi'].x-src['lo'].x
                scale=Vector((rng.uniform(.82,1.02),rng.uniform(.90,1.06),rng.uniform(1.04,1.31)))
                new_y=c.y+rng.uniform(9.0,14.0)
                if i==0:
                    edge=src['lo'].x if sign>0 else -src['hi'].x
                    # Retain a narrow lane, with each successive infill layer continuing the perspective.
                    inner=max(.85,edge/3)
                    new_x=sign*(inner+width*scale.x/2)
                else:
                    new_x=(side[i-1]['center'].x+c.x)/2+rng.uniform(-.28,.28)
                target=Vector((new_x,new_y,0))
                anchor=Vector((c.x,c.y,0))
                xf=Matrix.Translation(target) @ Matrix.Diagonal((*scale,1)) @ Matrix.Translation(-anchor)
                for ob in src['obs']:
                    cp=ob.copy(); cp.name='CITY099 '+ob.name
                    coll.objects.link(cp); cp.matrix_world=xf @ ob.matrix_world
                    cp['city099_source']=ob.name; cp['city099_layer']=layer
                lo=xf @ src['lo']; hi=xf @ src['hi']
                rec=dict(layer=layer,position=list(target),bounds_min=list(lo),bounds_max=list(hi),source=src['obs'][0].name,parts=len(src['obs']))
                additions.append(rec); row_new.append(rec)
        def gap_bounds(rs, new=False):
            left=[r for r in rs if (r['bounds_max'][0] if new else r['hi'].x)<0]
            right=[r for r in rs if (r['bounds_min'][0] if new else r['lo'].x)>0]
            if not left or not right:return None
            def inn(r,side):
                if new:return Vector((r['bounds_max'][0] if side<0 else r['bounds_min'][0],r['bounds_min'][1],0))
                return Vector((r['hi'].x if side<0 else r['lo'].x,r['lo'].y,0))
            l=max((inn(r,-1) for r in left),key=lambda p:p.x)
            rr=min((inn(r,1) for r in right),key=lambda p:p.x)
            ql=world_to_camera_view(scene,scene.camera,l); qr=world_to_camera_view(scene,scene.camera,rr)
            return {'world_m':rr.x-l.x,'projected_pixels':(qr.x-ql.x)*scene.render.resolution_x*scene.render.resolution_percentage/100,'left':list(l),'right':list(rr)}
        baseline=gap_bounds(row); after=gap_bounds(row_new,True)
        gap_reports.append({'layer':layer,'baseline':baseline,'infill':after,'screen_ratio':after['projected_pixels']/baseline['projected_pixels']})
    return {'original_buildings':len(records),'additional_buildings':len(additions),'total_buildings':len(records)+len(additions),'parts_added':sum(r['parts'] for r in additions),'collection':coll.name,'gap_by_layer':gap_reports,'buildings':additions,'notes':'Existing towers unchanged. New linked native tower parts in staggered depth rows; gap is projected bounds measurement, not an occlusion-count claim.'}
