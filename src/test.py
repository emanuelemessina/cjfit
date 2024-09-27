import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix
from sklearn.decomposition import PCA
import math
from . import commands
from . import modifiers

def pca_rotate(object):
    commands.select_single(object)
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
    commands.apply_rotation()
    
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
    commands.apply_rotation()

def run(jig, d, h):

    commands.origin_to_geometry()
    commands.apply_rotation()
    commands.apply_scale()

    ch = commands.duplicate(jig)
    commands.rename(ch, f"{jig.name} CH")
    modifiers.convex_hull(ch)
    modifiers.remesh()

    commands.parent_keep_transform(jig, ch)
    #hide(jig)

    # R1
    [pca_rotate(ch) for i in range(3)] # make it converge

    bb = commands.duplicate(ch)
    commands.rename(bb, f"{ch.name} BB")
    commands.parent_keep_transform(ch, bb)
    corners = modifiers.bounding_box(bb)
    
    # T1
    commands.to_world_origin(bb)

    # fix pca x-y assignment
    fix_pca_xy(corners,bb)
    
    rotation_step = math.radians(1)
    max_rotation = math.radians(90)
    upper_z_bound = h/2  # Define the upper z-boundary
    lower_z_bound = -h/2  # Define the lower z-boundary
    adjustment_step = 0.01 

    def check_boundaries_intersections(axis, lower_bound, upper_bound):

        world_vertices = [ch.matrix_world @ v.co for v in ch.data.vertices]
        
        axis_values = [getattr(v,axis) for v in world_vertices]
        
        crosses_lower = any(a < lower_bound for a in axis_values)
        crosses_upper = any(a > upper_bound for a in axis_values)
        
        return crosses_lower, crosses_upper

    def push_towards_origin(direction, adjustment_step):
        if direction == 'down':
            bb.location.z -= adjustment_step
        elif direction == 'up':
            bb.location.z += adjustment_step

    total_rotation = 0.0

    while total_rotation < max_rotation:
        
        commands.update_scene() # recalc local matrices

        crosses_lower, crosses_upper = check_boundaries_intersections('z', lower_z_bound, upper_z_bound)
        
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
                
    commands.apply_rotation()
    


