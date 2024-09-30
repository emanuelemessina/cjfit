import bpy
from . import cylinder

class Properties(bpy.types.PropertyGroup):
    radius: bpy.props.FloatProperty(name="Radius", default=1.0, min=0.01, unit='LENGTH', subtype='DISTANCE', update=lambda self, context: cylinder.update(self, context)) # type: ignore
    depth: bpy.props.FloatProperty(name="Height", default=2.0, min=0.01, unit='LENGTH', subtype='DISTANCE', update=lambda self, context: cylinder.update(self, context)) # type: ignore

classes = [Properties]