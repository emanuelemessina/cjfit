import math
from . import transform
from .transform import Direction
from . import commands
import bpy

def get_boundaries_crosses(object, axis, lower_bound, upper_bound):

    world_vertices = [object.matrix_world @ v.co for v in object.data.vertices]
    
    axis_values = [getattr(v,axis.value) for v in world_vertices]
    
    crosses_lower = any(a < lower_bound for a in axis_values)
    crosses_upper = any(a > upper_bound for a in axis_values)
    
    return crosses_lower, crosses_upper


def center_adjust(bounding_box, object, axis, lower_bound, upper_bound, step=transform.adjustment_step):
        crosses_lower, crosses_upper = get_boundaries_crosses(object, axis, lower_bound, upper_bound)

        # choose a direction anyway, if not intersecting the loop will exit            
        if crosses_lower:
            direction = Direction.positive
        else:
            direction = Direction.negative
        
        while True:
            if (crosses_lower and not crosses_upper and direction == Direction.positive) or (crosses_upper and not crosses_lower and direction == Direction.negative):
                # continue to nudge until the single boundary stop intersecting
                transform.nudge(bounding_box, axis, direction, step)
                crosses_lower, crosses_upper = get_boundaries_crosses(object, axis, lower_bound, upper_bound)
                continue
            else:
                # solved or both boundaries intersecting
                return (crosses_lower or crosses_upper) # returns intersecting

def try_rotate_adjust(bounding_box, convex_hull, rotation_axis, adjust_axis, lower_bound, upper_bound, rotation_step=transform.rotation_step):

    max_rotation = math.radians(90)
    
    total_rotation = 0.0

    solved = False

    while total_rotation < max_rotation:
        
        intersecting = center_adjust(bounding_box, convex_hull, adjust_axis, lower_bound, upper_bound)

        if not intersecting:
            # solved
            solved = True
            break

        # both boundaries are crossed, continue rotating
        
        # Rotate the object by a small step along the X-axis
        
        bounding_box.rotation_euler[rotation_axis.value] += rotation_step
        total_rotation += rotation_step
        commands.update_scene() # recalc local matrices
    
    return solved