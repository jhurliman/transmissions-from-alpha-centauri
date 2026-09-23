"""Lighter service-cavity backing and half-strength right Y corrosion, native materials."""
import bpy

def apply(scene):
    rows=[]
    host=scene.objects['Architecture | gangway_single_Y_8m.001']
    assert host.matrix_world.translation.x > 0, 'Expected right Y support'
    for ob in host.instance_collection.all_objects:
        if not ob.name.startswith(('Y arm','Y stem')): continue
        for slot in ob.material_slots:
            old=slot.material
            m=old.copy();m.name='193 Right support half rust | '+ob.name
            n=m.node_tree.nodes;l=m.node_tree.links
            mix=next(q for q in n if q.label=='189 Edge-fed oxide over accepted steel')
            old_factor=mix.inputs[0].links[0].from_socket
            scale=n.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.label='193 Right rust strength 50 percent';scale.inputs[1].default_value=.5
            l.new(old_factor,scale.inputs[0]);l.new(scale.outputs[0],mix.inputs[0]);slot.link='OBJECT';slot.material=m
            rows.append({'object':ob.name,'old_material':old.name,'material':m.name,'rust_strength_multiplier':.5})
    ob=bpy.data.objects['133 Deep closed service backwall'];old=ob.material_slots[0].material
    m=old.copy();m.name='193 Lighter slate service backing';m.diffuse_color=(.13,.145,.17,1);n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
    df=n.new('ShaderNodeBsdfDiffuse');df.inputs[0].default_value=(.7,.7,.7,1)
    rgb=n.new('ShaderNodeShaderToRGB');l.new(df.outputs[0],rgb.inputs[0]);bw=n.new('ShaderNodeRGBToBW');l.new(rgb.outputs[0],bw.inputs[0])
    light=n.new('ShaderNodeMapRange');light.clamp=True;light.inputs['From Max'].default_value=.9;light.inputs['To Min'].default_value=.45;light.inputs['To Max'].default_value=1.05;l.new(bw.outputs[0],light.inputs[0]);light.label='193 Retained native light response with readable cavity floor'
    geo=n.new('ShaderNodeNewGeometry');grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=8;grain.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],grain.inputs['Vector'])
    pigment=n.new('ShaderNodeMixRGB');pigment.inputs[1].default_value=(.11,.125,.15,1);pigment.inputs[2].default_value=(.145,.16,.19,1);l.new(grain.outputs['Fac'],pigment.inputs[0])
    lit=n.new('ShaderNodeMixRGB');lit.blend_type='MULTIPLY';lit.inputs[0].default_value=1;l.new(pigment.outputs[0],lit.inputs[1]);l.new(light.outputs[0],lit.inputs[2])
    em=n.new('ShaderNodeEmission');l.new(lit.outputs[0],em.inputs['Color']);out=n.new('ShaderNodeOutputMaterial');l.new(em.outputs[0],out.inputs['Surface'])
    ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=m
    return {'right_y_materials':rows,'service_backing':{'object':ob.name,'old_material':old.name,'material':m.name},'left_y_unchanged':True,'geometry_unchanged':True,'original_material_graphs_unchanged':True,'references':['RS-01','UP-03','DP-08']}
