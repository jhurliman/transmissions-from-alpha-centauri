"""Persistent selected214double-detail sprites at exact output-pixel coordinates.

Generated2D artwork, expressly user-selected; never a3D geometry claim.
No scene mesh/light/material change except the scoped206proxy removal.
"""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'art/studies/pixel-characters-217'

def overlay(scene):
    assert not scene.get('217 selected pixel characters'),'217 already installed'
    assert (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage)==(3840,2885,100),'217 current approved screen layout requires3840x2885at100percent'
    tree=scene.compositing_node_group
    assert tree,'Expected existing native scene compositor'
    output=next(n for n in tree.nodes if n.type=='GROUP_OUTPUT' and n.is_active_output)
    socket=output.inputs.get('Image') or output.inputs[0]
    assert socket.is_linked
    original=socket.links[0].from_socket
    group=bpy.data.node_groups.new('217 Selected pixel characters | 5x6 exact grid','CompositorNodeTree')
    group.interface.new_socket(name='Background',in_out='INPUT',socket_type='NodeSocketColor')
    group.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    gin=group.nodes.new('NodeGroupInput');gout=group.nodes.new('NodeGroupOutput');last=gin.outputs['Background'];rows=json.loads((O/'assets.json').read_text())
    for index,row in enumerate(rows):
        source=R/row['source_sprite'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['source_sha256']
        original_image=bpy.data.images.load(str(source),check_existing=False);original_image.name='217 SOURCE '+source.name;original_image.use_fake_user=True;original_image.pack()
        path=R/row['placed_canvas'];assert hashlib.sha256(path.read_bytes()).hexdigest()==row['canvas_sha256']
        image=bpy.data.images.load(str(path),check_existing=False);image.name='217 '+row['name']+' selected214pixel art';image.pack()
        im=group.nodes.new('CompositorNodeImage');im.image=image;im.label=row['name'].title()+' | exact5x6pixels | '+str(row['body_bbox']);im.location=(-600,index*-220)
        move=group.nodes.new('CompositorNodeTranslate');move.label='Integer pixel offset only';move.location=(-350,index*-220)
        group.links.new(im.outputs['Image'],move.inputs['Image'])
        for axis in ['X','Y']:
            inp=group.interface.new_socket(name=row['name'].title()+' '+axis,in_out='INPUT',socket_type='NodeSocketInt');inp.default_value=0;inp.min_value=-3840;inp.max_value=3840
            group.links.new(gin.outputs[inp.name],move.inputs[axis])
        over=group.nodes.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;over.label=row['name'].title()+' selected sprite';over.location=(index*220,0)
        group.links.new(last,over.inputs['Background']);group.links.new(move.outputs['Image'],over.inputs['Foreground']);last=over.outputs[0]
    group.links.new(last,gout.inputs['Image']);gout.location=(500,0)
    node=tree.nodes.new('CompositorNodeGroup');node.node_tree=group;node.label='217 USER SELECTED: double-detail pixel Traveler-A + Traveler-B';node.location=(output.location.x-220,output.location.y-220)
    tree.links.new(original,node.inputs['Background']);tree.links.new(node.outputs['Image'],socket)
    prior_dither=scene.render.dither_intensity;scene.render.dither_intensity=0
    scene.render.use_compositing=True;scene['217 selected pixel characters']=True
    return {'rows':rows,'packed_images':True,'output_dither_before':prior_dither,'output_dither_after':0,'compositor_group':group.name,'render_resolution':[3840,2885,100],'scope':'Persistent editable2Dpixel overlays after current native scene/ink composite','filtering':'Already placed integer5x6nearest pixels; no image scaling nodes; zero integer translation by default','limitations':['Fixed approved camera/output framing; redo placement for different resolution/camera.','Foreground depth ordering is authored for the current clear-road placement, not automatic3Docclusion.','No contact shadow or3Dcharacter rig is claimed.'],'user_selected_treatment':'214double-detail pixels'}

def apply(scene):
    from anime_proxy_hide_206 import apply as hide_proxy
    audit=overlay(scene);audit['proxy_removal']=hide_proxy(scene)
    scene['217 character integration audit']=json.dumps(audit)
    (O/'integration-audit.json').write_text(json.dumps(audit,indent=2))
    return audit
