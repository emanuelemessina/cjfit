import numpy as np
from mathutils import Vector, Matrix
from sklearn.decomposition import PCA
from . import commands

def pca_rotate(object, alignment):
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
    
    # align the principal axes to the global axes in a specific order
    rotation_matrix = principal_axes[alignment] # permutation

    blender_rotation_matrix = Matrix(rotation_matrix) # convert to blender
    object.rotation_euler = blender_rotation_matrix.to_euler() # rotate
    commands.apply_rotation()
    
def fix_pca_xy(bounding_box, corners, alignment):
    edge_vectors = [
        corners[1] - corners[0],  # Edge along the x-axis
        corners[3] - corners[0],  # Edge along the y-axis
        corners[4] - corners[0],  # Edge along the z-axis
    ]

    lengths = [vec.length for vec in edge_vectors]
    sorted_indices = sorted(range(len(lengths)), key=lambda i: lengths[i])
    sorted_vectors = [edge_vectors[i] for i in sorted_indices]
    sorted_vectors.reverse() # decreasing order like the pca components

    basis = Matrix.Identity(3)
    basis[0][:] = sorted_vectors[alignment[0]].normalized()
    basis[1][:] = sorted_vectors[alignment[1]].normalized()
    basis[2][:] = sorted_vectors[alignment[2]].normalized()

    bounding_box.rotation_euler = basis.to_euler()
    commands.apply_rotation()
