import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix
from sklearn.decomposition import PCA
import math
    
def run(cylinder):
        
    def duplicate(object):
        copy = object.copy()
        copy.data = object.data.copy()
        bpy.context.collection.objects.link(copy)
        return copy

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

    def apply_convex_hull(object):
        select_single(object)
        mesh = object.data
        
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        # reduce to verts only.
        bmesh.ops.delete(bm, geom=bm.edges, context='EDGES_FACES')

        ch = bmesh.ops.convex_hull(bm, input=bm.verts)

        # remove interior verts 
        bmesh.ops.delete(
            bm,
            geom=ch["geom_unused"],
            context='VERTS',
            )

        bm.to_mesh(mesh)
        bm.free()
        
        mesh.update()
        origin_to_geometry()

    def to_world_origin(object):
        object.location = (0,0,0)

    def parent_keep_transform(child, parent):
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()

    def remesh():
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
        bpy.context.object.modifiers["Remesh"].octree_depth = 6
        bpy.ops.object.modifier_apply(modifier="Remesh")
        origin_to_geometry()

    def pca_rotate(object):
        select_single(object)
        mesh = object.data
        vertices = [v.co for v in mesh.vertices]
        points = np.array([(v.x, v.y, v.z) for v in vertices]) # convert to numpy

        pca = PCA(n_components=3)
        pca.fit(points)
        principal_axes = pca.components_  # Shape (3, 3) , column-major

        # Create a rotation matrix from the principal axes to the global axes (identity)
        # The principal axes form the object's local coordinate system
        # We want to rotate the object so that the local axes match the global axes
        # the rotation matrix with respect to the identity is the basis itself
        # we want to rotate back to the identity so the inverse rotation matrix is the inverse of the basis
        # but the eigenvector basis is orthogonal so the inverse is the transpose
        # in this case it corresponds to the column major form of the eigenvector basis (principal_axes variable)
        # since we want the principal axes to be aligned with (z,x,y) instead of (x,y,z) we permute the principal_axes matrix
        rotation_matrix = principal_axes[[1,2,0]] # which pca axis to assign to (x,y,z)

        blender_rotation_matrix = Matrix(rotation_matrix) # convert to blender
        object.rotation_euler = blender_rotation_matrix.to_euler() # rotate
        apply_rotation()
        
    def create_bounding_box(object):
        corners = [object.matrix_world @ Vector(corner) for corner in object.bound_box]
        mesh = bpy.data.meshes.new(name=f"{object.name} BB")
        bounding_box = bpy.data.objects.new(f"{object.name} BB", mesh)
        bpy.context.collection.objects.link(bounding_box)
        mesh.from_pydata(corners, [], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)])
        mesh.update()
        select_single(bounding_box)
        origin_to_geometry()
        return bounding_box, corners

    def fix_pca_xy(corners, bounding_box):
        edge_vectors = [
            corners[1] - corners[0],  # Edge along the x-axis
            corners[3] - corners[0],  # Edge along the y-axis
            corners[4] - corners[0],  # Edge along the z-axis
        ]

        lengths = [vec.length for vec in edge_vectors]
        sorted_indices = sorted(range(len(lengths)), key=lambda i: lengths[i])
        sorted_vectors = [edge_vectors[i] for i in sorted_indices]

        basis = Matrix.Identity(3)
        basis[0][:] = sorted_vectors[1].normalized()  # Align second shortest with X
        basis[1][:] = sorted_vectors[0].normalized()  # Align shortest with Y
        basis[2][:] = sorted_vectors[2].normalized()  # Align longest with Z

        bounding_box.rotation_euler = basis.to_euler()
        apply_rotation()

    def hide(object):
        object.hide_set(True)
        object.hide_render = True
        
    jig = get_active_object()
    origin_to_geometry()
    apply_rotation()

    ch = duplicate(jig)
    ch.name = f"{jig.name} CH"
    apply_convex_hull(ch)
    remesh()

    parent_keep_transform(jig, ch)
    #hide(jig)

    # R1
    [pca_rotate(ch) for i in range(3)] # make it converge

    bb, corners = create_bounding_box(ch)
    parent_keep_transform(ch, bb)

    # T1
    to_world_origin(bb)

    # fix pca x-y assignment
    fix_pca_xy(corners,bb)
    
    rotation_step = math.radians(1)  # Small constant angle to rotate (1 degree in radians)
    max_rotation = math.radians(90)  # Maximum allowable rotation (90 degrees in radians)
    upper_z_bound = 1  # Define the upper z-boundary
    lower_z_bound = -1  # Define the lower z-boundary
    adjustment_step = 0.01 

    # Function to check if object is within the z-boundary
    def check_z_boundaries():
        apply_rotation()
        
        world_vertices = [ch.matrix_world @ v.co for v in ch.data.vertices]
        
        z_values = [v.z for v in world_vertices]
        
        crosses_lower = any(z < lower_z_bound for z in z_values)
        crosses_upper = any(z > upper_z_bound for z in z_values)
        
        return crosses_lower, crosses_upper

    def push_towards_origin(direction, adjustment_step):
        if direction == 'down':
            bb.location.z -= adjustment_step
        elif direction == 'up':
            bb.location.z += adjustment_step

    # Rotating the object iteratively
    total_rotation = 0.0
    
    select_single(ch)

    while total_rotation < max_rotation:
        
        crosses_lower, crosses_upper = check_z_boundaries()
        
        # If no boundaries are crossed, stop the rotation
        if not crosses_lower and not crosses_upper:
            print("Object is within z-boundaries. Stopping rotation.")
            break
        
        # If only one boundary is crossed, push the object towards the world origin
        if crosses_lower and not crosses_upper:
            push_towards_origin('up', adjustment_step)
            continue
        elif crosses_upper and not crosses_lower:
            push_towards_origin('down', adjustment_step)
            continue
        
        # If both boundaries are crossed, continue rotating
        
        # Rotate the object by a small step along the X-axis
        bb.rotation_euler[0] += rotation_step
        total_rotation += rotation_step
            
    bpy.context.view_layer.update()



