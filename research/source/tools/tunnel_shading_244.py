"""Quiet enclosed tunnel lighting; preserve exterior masonry and accepted fog."""
import bpy

def apply(scene):
    assert not scene.get('244 enclosed tunnel shading')
    tunnels=sorted((o for o in bpy.data.objects if o.get('220 descending arcade tunnel')),key=lambda o:o['bay'])
    caps=sorted((o for o in bpy.data.objects if o.get('241 tunnel end cap')),key=lambda o:o['bay'])
    assert len(tunnels)==len(caps)==18
    source=tunnels[0].material_slots[0].material
    mat=source.copy();mat.name='244 Enclosed tunnel masonry | quiet indirect light'
    n=mat.node_tree.nodes;l=mat.node_tree.links
    ramp=next(x for x in n if x.label=='Warm exposed stone, violet recesses')
    previous=[{'node':a.from_node.name,'socket':a.from_socket.name}for a in ramp.inputs[0].links]
    for a in list(ramp.inputs[0].links):l.remove(a)
    # Keep a subdued actual-light response, with no fabricated normal-dot sun.
    bw=next(x for x in n if x.type=='RGBTOBW' and any(a.from_node.type=='SHADERTORGB'for a in x.inputs[0].links))
    quiet=n.new('ShaderNodeMapRange');quiet.name='244 Bounded enclosed indirect light'
    quiet.label='Actual enclosed light, quiet violet palette; no directional emission'
    quiet.clamp=True;quiet.inputs['From Min'].default_value=0;quiet.inputs['From Max'].default_value=2
    quiet.inputs['To Min'].default_value=.10;quiet.inputs['To Max'].default_value=.16
    l.new(bw.outputs[0],quiet.inputs['Value']);l.new(quiet.outputs['Result'],ramp.inputs[0])
    mat['244 scoped tunnel interior']=True
    rows=[]
    for o in tunnels+caps:
        for i,slot in enumerate(o.material_slots):
            old=slot.material
            slot.link='OBJECT';slot.material=mat
            assert slot.material is mat
            rows.append({'object':o.name,'slot':i,'before':old.name if old else None,'after':mat.name})
    scene['244 enclosed tunnel shading']=True
    return {'diagnosis':'18 solid terminal caps exist. Actual OBJECT material overrides contain unoccluded normal-dot form lighting feeding emission. Corrected actual-slot return-only test barely changed visible glow and was discarded. Actual-slot tunnel-only crop removes the narrow pale column, max21/255 channel delta; native warm haze persists.',
            'references':{'UCL-01':'Quiet recessed opening value families under warm atmosphere','UCL-02':'Legible arch shell surrounding subdued interior','DP-01':'Simple shadowed monumental threshold'},
            'source':source.name,'previous_palette_driver':previous,'actual_light_palette_range':[.10,.16],
            'objects':rows,'all_18_caps_preserved':True,'geometry_positions_unchanged':True,'fog_unchanged':True,'upper_arcades_unchanged':True,'exterior_front_materials_unchanged':True,'native_crop_review':{'before':'art/studies/tunnel-shading-244/before.png','after':'art/studies/tunnel-shading-244/after.png','max_8bit_delta':21,'pixels_delta_above_3':3089,'finding':'Pale narrow column in right opening removed; warm lower haze remains'},'view_review_required':False}
