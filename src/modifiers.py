import bpy
import bmesh
from mathutils import Vector
from . import commands

def convex_hull(object):
    commands.select_single(object)
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
    commands.origin_to_geometry()

def remesh():
    bpy.ops.object.modifier_add(type='REMESH')
    bpy.context.object.modifiers["Remesh"].mode = 'SHARP'
    bpy.context.object.modifiers["Remesh"].octree_depth = 6
    bpy.ops.object.modifier_apply(modifier="Remesh")
    commands.origin_to_geometry()

def bounding_box(object):
    corners = [Vector(corner) for corner in object.bound_box]
    mesh = object.data
    mesh.clear_geometry()
    mesh.from_pydata(corners, [], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (0, 3, 7, 4), (1, 2, 6, 5)])
    mesh.update()
    commands.select_single(object)
    commands.origin_to_geometry()
    return corners