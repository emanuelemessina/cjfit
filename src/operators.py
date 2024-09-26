import bpy

from . import cylinder
from . import test

class CreateCylinderButton(bpy.types.Operator):
    bl_idname = "mesh.create_cylinder"
    bl_label = "Create Cylinder"
    
    def execute(self, context):        
        props = context.scene.props
        cylinder.update(props, context)
        return {'FINISHED'}

class TestButton(bpy.types.Operator):
    bl_idname = "object.test"
    bl_label = "Test"
    
    @classmethod
    def poll(cls, context):
        return any(obj.name == cylinder.name for obj in context.scene.objects)
    
    def execute(self, context):
        props = context.scene.props
        
        cylinder_obj = None
        for obj in context.scene.objects:
            if obj.name == cylinder.name:
                cylinder_obj = obj
                break

        if cylinder_obj:
            test.run(cylinder_obj)
        
        return {'FINISHED'}

classes = [CreateCylinderButton, TestButton]