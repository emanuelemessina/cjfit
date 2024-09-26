import bpy

name = "CJFIT_Cylinder"

def update(self, context):
    remove_existing(context)
    
    bpy.ops.mesh.primitive_cylinder_add(
        radius=self.radius,
        depth=self.depth,
        vertices=self.vertices,
        location=(0, 0, 0)
    )

    obj = context.active_object
    obj.name = name

def remove_existing(context):
    for obj in context.scene.objects:
        if obj.name == name:
            bpy.data.objects.remove(obj, do_unlink=True)
