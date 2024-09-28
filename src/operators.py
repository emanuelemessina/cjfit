import bpy

from . import cylinder
from . import test
from . import commands

class TestButton(bpy.types.Operator):
    bl_idname = "object.test"
    bl_label = "Test"
    
    def execute(self, context):
        props = context.scene.props
        
        # get jig
        jig = commands.get_active_object()

        # visually show the cylinder
        cylinder.update(props, context)            

        # reselect jig
        commands.select_single(jig)
        
        # run test
        msg = test.run(jig, props.radius, props.depth)
        self.report({'INFO'}, msg)
        
        return {'FINISHED'}

classes = [TestButton]