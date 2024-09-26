import bpy

class Properties(bpy.types.PropertyGroup):
    radius: bpy.props.FloatProperty(name="Radius", default=1.0, min=0.01, update=lambda self, context: update_cylinder(self, context))
    depth: bpy.props.FloatProperty(name="Depth", default=2.0, min=0.01, update=lambda self, context: update_cylinder(self, context))
    vertices: bpy.props.IntProperty(name="Vertices", default=32, min=3, max=256, update=lambda self, context: update_cylinder(self, context))

classes = [Properties]