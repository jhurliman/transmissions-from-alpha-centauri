"""Camera-only clear sky, user125 exact output sRGB endpoints; preserves illumination/clouds/sun."""
import bpy,math
from mathutils import Vector
TARGET_TOP=(231,90,56)
TARGET_BOTTOM=(236,95,55)
def linear(v):
 v=v/255
 return v/12.92 if v<=.04045 else((v+.055)/1.055)**2.4

def apply():
 s=bpy.context.scene
 if s.world.get('125 calibrated clear sky'):return {'already_applied':True}
 if (s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma)!=('Standard','None',0.,1.):raise RuntimeError('Sky125 calibration expects preserved Standard/None exposure0 gamma1')
 oldworld=s.world;s.world=oldworld.copy();w=s.world;nt=w.node_tree;n=nt.nodes;l=nt.links;base=next(q for q in n if q.label=='075 Amber horizon to vermilion zenith');tc=next(q for q in n if q.label=='075 World directions');bg=next(q for q in n if q.label=='075 Camera sky only');strength=bg.inputs['Strength'].default_value
 old={'world':oldworld.name,'ramp':[{'position':e.position,'scene_linear':list(e.color)}for e in base.color_ramp.elements],'factor_sources':[x.from_node.name for x in base.inputs[0].links],'camera_strength':strength}
 cam=s.camera;frame=cam.data.view_frame(scene=s);ymin=min(v.y/-v.z for v in frame);ymax=max(v.y/-v.z for v in frame);Q=cam.matrix_world.to_quaternion();up=Q@Vector((0,1,0));forward=Q@Vector((0,0,-1))
 def dot(label,axis):
  q=n.new('ShaderNodeVectorMath');q.operation='DOT_PRODUCT';q.label='125 '+label;l.new(tc.outputs['Normal'],q.inputs[0]);q.inputs[1].default_value=axis;return q.outputs['Value']
 def mathn(op,label,a,b):
  q=n.new('ShaderNodeMath');q.operation=op;q.label='125 '+label
  for i,v in enumerate([a,b]):
   if isinstance(v,(float,int)):q.inputs[i].default_value=v
   else:l.new(v,q.inputs[i])
  return q.outputs[0]
 slope=mathn('DIVIDE','Camera vertical ray slope',dot('Camera up projection',up),dot('Camera forward projection',forward));factor=mathn('DIVIDE','Full-frame bottom0 top1',mathn('SUBTRACT','Frame bottom offset',slope,ymin),ymax-ymin)
 for link in list(base.inputs[0].links):l.remove(link)
 l.new(factor,base.inputs[0]);r=base.color_ramp
 while len(r.elements)>2:r.elements.remove(r.elements[-1])
 r.interpolation='LINEAR';r.elements[0].position=0.;r.elements[1].position=1.;r.elements[0].color=tuple(linear(v)/strength for v in TARGET_BOTTOM)+(1,);r.elements[1].color=tuple(linear(v)/strength for v in TARGET_TOP)+(1,)
 w['125 calibrated clear sky']=True;w['125 top output hex']='#e75a38';w['125 bottom output hex']='#ec5f37'
 return {'old':old,'new':{'world':w.name,'ramp':[{'position':e.position,'scene_linear':list(e.color)}for e in r.elements],'target_top_srgb':list(TARGET_TOP),'target_bottom_srgb':list(TARGET_BOTTOM)},'mapping':'Vertical full camera frame, including current lens shift and aspect; y0 bottom/y1 top. Not world elevation ABS.','camera_frame_slope_bounds':[ymin,ymax],'color_management_unchanged':True,'compensation':'Exact inverse Standard sRGB transfer, divided by existing0.9 camera-background strength','preserved':'Existing non-camera world illumination, sun branch, cloud objects/materials/layout and all scene geometry'}
