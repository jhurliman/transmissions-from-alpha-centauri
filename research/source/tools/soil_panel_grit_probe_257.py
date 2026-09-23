import bpy
s=bpy.context.scene
m=s.objects['Street foundation'].material_slots[0].material;m.node_tree.nodes['257 Grit strength'].outputs[0].default_value=1.5
s.render.border_min_x=2700/3840;s.render.border_max_x=3500/3840;s.render.border_min_y=1-1910/2885;s.render.border_max_y=1-1500/2885
