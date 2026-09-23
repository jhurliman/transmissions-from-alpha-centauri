"""Scoped, scene-scale mineral staining on the central ground arcade column."""
import bpy

TARGET='COL124 T0 B07 engaged round column'

def apply(scene):
    assert not scene.get('249 central column weathering')
    obj=bpy.data.objects[TARGET]
    before=[(o.name,[(s.link,s.material.name if s.material else None)for s in o.material_slots]) for o in scene.objects if o is not obj]
    old=obj.material_slots[0].material
    mat=old.copy();mat.name='249 Central arcade column | broken mineral stains'
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    def node(t,name):
        n=nodes.new(t);n.name='249 '+name;n.label=name;return n
    def noise(vec,scale,name):
        v=node('ShaderNodeVectorMath',name+' proportions');v.operation='MULTIPLY';v.inputs[1].default_value=scale;links.new(vec,v.inputs[0])
        n=node('ShaderNodeTexNoise',name);n.inputs['Scale'].default_value=1;n.inputs['Detail'].default_value=2.6;n.inputs['Roughness'].default_value=.72;links.new(v.outputs['Vector'],n.inputs['Vector']);return n.outputs['Fac']
    def ramp(src,lo,hi,name):
        n=node('ShaderNodeValToRGB',name);n.color_ramp.elements[0].position=lo;n.color_ramp.elements[0].color=(0,0,0,1);n.color_ramp.elements[1].position=hi;n.color_ramp.elements[1].color=(1,1,1,1);links.new(src,n.inputs[0]);return n.outputs[0]
    def math(op,a,b,name):
        n=node('ShaderNodeMath',name);n.operation=op
        for i,val in enumerate((a,b)):
            if isinstance(val,(float,int)):n.inputs[i].default_value=val
            else:links.new(val,n.inputs[i])
        return n.outputs[0]
    tex=node('ShaderNodeTexCoord','Column-local stable pigment coordinates')
    broad=ramp(noise(tex.outputs['Generated'],(4.7,3.1,9.4),'Unequal broad water stain islands'),.48,.66,'Irregular soft mineral stain margins')
    breakup=ramp(noise(tex.outputs['Generated'],(19,13,37),'Broken stain surface flecks'),.29,.61,'Coarse fleck gaps')
    patches=math('MULTIPLY',broad,breakup,'Granular stain coverage')
    runoff=ramp(noise(tex.outputs['Generated'],(18,12,3.9),'Interrupted narrow gravity runoff'),.60,.73,'Sparse runoff paths')
    fac=math('ADD',math('MULTIPLY',patches,.63,'Readable mineral patina strength'),math('MULTIPLY',runoff,.18,'Quiet runoff strength'),'Combined restrained staining')
    fac=math('MINIMUM',fac,.72,'Bound stain opacity')
    emission=next(n for n in nodes if n.type=='EMISSION')
    source=emission.inputs['Color'].links[0].from_socket
    mul=node('ShaderNodeMixRGB','Violet-brown mineral stains preserve painted light');mul.blend_type='MULTIPLY';mul.inputs[2].default_value=(.36,.36,.42,1)
    links.new(fac,mul.inputs[0]);links.new(source,mul.inputs[1]);links.new(mul.outputs[0],emission.inputs['Color'])
    obj.material_slots[0].link='OBJECT';obj.material_slots[0].material=mat
    assert obj.material_slots[0].material is mat
    assert before==[(o.name,[(s.link,s.material.name if s.material else None)for s in o.material_slots])for o in scene.objects if o is not obj]
    scene['249 central column weathering']=True
    return {'target':TARGET,'projected_bounds_4k':[1868,890,1906,1126],'previous_actual_material':old.name,'new_actual_material':mat.name,'treatment':'Broad irregular granular mineral staining with interrupted vertical runoff, no geometry change','references':['UCL-01','UP-03','DP-08'],'only_target_binding_changed':True,'fog_unchanged':True,'unrelated_columns_unchanged':True,'review_required':True}
