import bpy

from . import operators
from . import ui
from . import props

classes = operators.classes + ui.classes + props.classes

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.props = bpy.props.PointerProperty(type=props.Properties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.props

if __name__ == "__main__":
    register()