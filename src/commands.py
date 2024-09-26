import bpy

def duplicate(object):
        copy = object.copy()
        copy.data = object.data.copy()
        bpy.context.collection.objects.link(copy)
        return copy

def rename(object, new_name):
    object.name = new_name
    object.data.name = new_name

def get_active_object():
    obj = bpy.context.active_object

    if obj is None or obj.type != 'MESH':
        raise ValueError("Please select a mesh object.")
    if bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    if obj.users_collection:
        collection_name = obj.users_collection[0].name
        layer_collection = bpy.context.view_layer.layer_collection.children.get(collection_name)
        
        if layer_collection:
            bpy.context.view_layer.active_layer_collection = layer_collection
        else:
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection

    return obj

def select_single(object):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = object
    object.select_set(True)

def origin_to_geometry():
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

def apply_rotation():
    bpy.ops.object.transform_apply(location=False , rotation=True, scale=False)

def apply_scale():
    bpy.ops.object.transform_apply(location=False , rotation=False, scale=True)


def to_world_origin(object):
    object.location = (0,0,0)

def parent_keep_transform(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()

def hide(object):
    object.hide_set(True)
    object.hide_render = True