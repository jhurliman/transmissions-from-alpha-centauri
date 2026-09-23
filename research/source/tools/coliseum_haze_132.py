"""Editable world-depth low dust study; preserve115 vertical gradient."""
import bpy,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
O=R/'art/studies/coliseum-132';O.mkdir(parents=True,exist_ok=True)
def apply(scene,multiplier,near_start=80.,far_end=210.):
    ob=scene.objects['Distant dust volume - real lighting'];m=ob.active_material.copy();m.name=f'132 Depth graded street dust {multiplier}x';ob.active_material=m
    n=m.node_tree.nodes;l=m.node_tree.links;volume=n.get('Volume Scatter');old=volume.inputs['Density'].links[0].from_socket
    xyz=n.get('Separate XYZ');ramp=n.new('ShaderNodeMapRange');ramp.name='132 Near-clear to far-dense';ramp.interpolation_type='SMOOTHERSTEP';ramp.clamp=True
    for k,v in [('From Min',near_start),('From Max',far_end),('To Min',.25),('To Max',float(multiplier))]:ramp.inputs[k].default_value=v
    l.new(xyz.outputs['Y'],ramp.inputs['Value']);mul=n.new('ShaderNodeMath');mul.name='132 Height times distance';mul.operation='MULTIPLY';l.new(old,mul.inputs[0]);l.new(ramp.outputs[0],mul.inputs[1]);l.new(mul.outputs[0],volume.inputs['Density'])
    return {'far_multiplier':multiplier,'near_multiplier':.25,'depth_y':[near_start,far_end],'height_z':[3,19],'base_density':.0017,'color':list(volume.inputs['Color'].default_value),'volume_bounds_unchanged':True}
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];kind=args[0]
    if kind=='build':
        from coliseum_crown_joints_131 import apply as joints
        from coliseum_frame_extension_131 import apply as frame
        bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-130/scene.blend'));s=bpy.context.scene;C=next(c for c in s.collection.children_recursive if c.name=='110 Coliseum detailed front ruin' and c.library is None)
        t=time.time();audit={'joints':joints(C),'frame':frame(C)};audit['seconds']=time.time()-t
        p=R/'art/studies/coliseum-131';bpy.ops.wm.save_as_mainfile(filepath=str(p/'scene.blend'));(p/'generation.json').write_text(json.dumps(audit,indent=2,default=str))
    else:
        multiplier=5 if kind=='selected' else int(kind);d=O/('selected' if kind=='selected' else f'{multiplier}x');d.mkdir(exist_ok=True)
        bpy.ops.wm.open_mainfile(filepath=str(R/'art/studies/coliseum-131/scene.blend'));s=bpy.context.scene;audit=apply(s,multiplier,48.,205.) if kind=='selected' else (apply(s,multiplier) if multiplier else {'baseline_haze':True})
        bpy.ops.wm.save_as_mainfile(filepath=str(d/'scene.blend'))
        s.render.resolution_x=3840;s.render.resolution_y=2885;s.render.resolution_percentage=100;s.render.line_thickness=3840/1440;s.render.use_border=False;s.render.use_crop_to_border=False;s.render.filepath=str(d/'main-4k.png')
        from coliseum_ink_reference_scene_130 import sync
        sync(s);t=time.time();bpy.ops.render.render(write_still=True);audit['render_seconds']=time.time()-t;(d/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
