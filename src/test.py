import math
from . import commands
from . import modifiers
from enum import Enum
from .pca import pca_rotate, fix_pca_xy
from . import transform
from .transform import Axis, Direction, RotationAxis
from . import intersections

def run(operator, jig, r, h):

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

    # fix pca x-y assignment, since it's not consistent
    fix_pca_xy(corners,bb)
    
    # save initial transform
    initial_location = bb.location.copy()
    initial_rotation = bb.rotation_euler.copy()

    # try remove vertical intersection (rotate along second shortest component)
    if intersections.try_rotate_adjust(bb, ch, RotationAxis.x, Axis.z, -h/2, h/2):
        # check for horizontal intersections
        crosses_left, crosses_right = intersections.get_boundaries_crosses(ch, Axis.y, -r, r)
        if crosses_left or crosses_right:
            # horizontal intersections (present or created after removing vertical ones)
            # roll back and try with the shortest component
            bb.location = initial_location
            bb.rotation_euler = initial_rotation
            
            operator.report({'INFO'}, "Doesn't fit")
        else:    
            # removed, now check top view
            operator.report({'INFO'}, "Fits!")
    else:
        # still vertical intersections
        operator.report({'INFO'}, "Doesn't fit")
    


