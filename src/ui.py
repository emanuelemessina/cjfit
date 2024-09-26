import bpy
from . import cylinder

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
        layout.prop(props, "vertices")
        
        cylinder_exists = any(obj.name == cylinder.name for obj in context.scene.objects)
        
        row = layout.row()
        row.operator("mesh.create_cylinder", text="Create Cylinder")
        row.enabled = not cylinder_exists
            
        layout.separator()

        row = layout.row()
        row.operator("object.test", text="Test")

classes = [Panel]