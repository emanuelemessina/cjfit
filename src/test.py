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
    initial_transform = transform.save(bb)

    # try remove vertical intersection (rotate along second shortest component)
    if intersections.try_remove_vertical(bb, ch, RotationAxis.x, Axis.y, r, h):
        # removed, now check top view
        operator.report({'INFO'}, "Fits!")
    else:
        # roll back and try rotating along shortest component
        operator.report({'INFO'}, "Cannot remove intersections w/ 1st hor component, trying 2nd...")
        transform.store(bb, initial_transform)
        if intersections.try_remove_vertical(bb, ch, RotationAxis.y, Axis.x, r, h):
            # removed, now check top view
            operator.report({'INFO'}, "Fits!")
        else:
            # cannot remove vertical intersections, failed
            operator.report({'INFO'}, "Doesn't fit: cannot remove axis-aligned intersections")
    


