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

    # R1
    # eigenvecs: z>x>y                   x>y>z
    alignment = [1,2,0] if h > 2*r else [0,1,2]
    [pca_rotate(ch, alignment) for i in range(3)] # make it converge

    bb = commands.duplicate(ch)
    commands.rename(bb, f"{ch.name} BB")
    commands.parent_keep_transform(ch, bb)
    corners = modifiers.bounding_box(bb)
    
    # T1
    commands.to_world_origin(bb)

    # fix pca x-y assignment, since it's not consistent
    fix_pca_xy(bb, corners, alignment)
    
    # save initial transform
    initial_transform = transform.save(bb)

    # try remove aa intersections (rotate along biggest horizontal component)

    if intersections.try_remove_axis_aligned(bb, ch, Axis.x, r, h):
        # removed, now check top view
        if intersections.try_remove_radial(bb, ch, r, h):
            return "Fits!"
    
    # retry with other axis aligned removal

    transform.store(bb, initial_transform)

    # try rotating along shortest horizontal component
    if intersections.try_remove_axis_aligned(bb, ch, Axis.y, r, h):
        if intersections.try_remove_radial(bb, ch, r, h):
            return "Fits!"
        else:
            return "Doesn't fit: cannot remove radial intersections"
    else:
        # cannot remove vertical intersections, failed
        return "Doesn't fit: cannot remove axis-aligned intersections"


