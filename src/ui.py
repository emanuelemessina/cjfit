import bpy
from . import cylinder
from . import commands

def check_active_object():
    obj = bpy.context.active_object

    return obj is not None and obj.type == 'MESH' and obj.name != cylinder.name

class Panel(bpy.types.Panel):
    bl_label = "CJFIT"
    bl_idname = "CJFIT"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'IPCV'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.props
        
        layout.prop(props, "radius")
        layout.prop(props, "depth")
        
        layout.separator()

        row = layout.row()
        row.operator("object.test", text="Test")
        row.enabled = check_active_object()

classes = [Panel]