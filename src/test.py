import math
from . import commands
from . import modifiers
from enum import Enum
from .pca import pca_rotate, fix_pca_xy
from . import transform
from .transform import Axis, Direction
from . import intersections

def run(jig, r, h):

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

    # try remove aa intersections (rotate along second shortest component)

    if intersections.try_remove_axis_aligned(bb, ch, Axis.x, Axis.y, r, h):
        # removed, now check top view
        if intersections.try_remove_diagonal(bb, ch, r, h):
            return "Fits!"
    
    # retry with other axis aligned removal

    transform.store(bb, initial_transform)

    # try rotating along shortest component
    if intersections.try_remove_axis_aligned(bb, ch, Axis.y, Axis.x, r, h):
        if intersections.try_remove_diagonal(bb, ch, r, h):
            return "Fits!"
        else:
            return "Doesn't fit: cannot remove diagonal intersections"
    else:
        # cannot remove vertical intersections, failed
        return "Doesn't fit: cannot remove axis-aligned intersections"


