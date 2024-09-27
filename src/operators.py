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
        test.run(jig, props.radius * 2, props.depth)
        
        return {'FINISHED'}

classes = [TestButton]