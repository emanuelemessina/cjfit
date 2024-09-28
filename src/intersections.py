import math
from . import transform
from .transform import Direction, Axis
from . import commands
from collections import deque
from mathutils import Euler

def get_world_vertices(object):
    return [object.matrix_world @ v.co for v in object.data.vertices]

def get_boundaries_crosses(object, axis, bounds):

    world_vertices = get_world_vertices(object)
    
    axis_values = [getattr(v,axis.value) for v in world_vertices]

    if isinstance(bounds, (int, float)):
        lower_bound = -bounds/2
        upper_bound = bounds/2
    else:
        lower_bound = bounds[0]
        upper_bound = bounds[1]

    crosses_lower = any(a < lower_bound for a in axis_values)
    crosses_upper = any(a > upper_bound for a in axis_values)
    
    return crosses_lower, crosses_upper


def center_adjust_axial(bounding_box, convex_hull, axis, bounds):
        crosses_lower, crosses_upper = get_boundaries_crosses(convex_hull, axis, bounds)

        # choose a direction anyway, if not intersecting the loop will exit            
        if crosses_lower:
            direction = Direction.positive
        else:
            direction = Direction.negative
        
        while True:
            if (crosses_lower and not crosses_upper and direction == Direction.positive) or (crosses_upper and not crosses_lower and direction == Direction.negative):
                # continue to nudge until the single boundary stop intersecting
                transform.nudge(bounding_box, axis, direction)
                crosses_lower, crosses_upper = get_boundaries_crosses(convex_hull, axis, bounds)
                continue
            else:
                # solved or both boundaries intersecting
                return not (crosses_lower and crosses_upper) # returns solved

def try_remove_axis_aligned(bounding_box, convex_hull, rotation_axis, radius, height):
    if try_rotate_adjust(bounding_box, convex_hull, rotation_axis=rotation_axis, adjust_axis=Axis.z, bounds=height):
        # vertical intersections removed
        # try to remove horizontal intersections by another rotate adjust
        if try_rotate_adjust(bounding_box, convex_hull, rotation_axis=rotation_axis, adjust_axis=(Axis.y if rotation_axis == Axis.x else Axis.x), bounds=radius*2):
            # check vertical intersections again
            return center_adjust_axial(bounding_box, convex_hull, Axis.z, bounds=height)
        else:
            return False
    else:
        # cannot remove vertical intersections
        return False
    
def get_vertex_quadrant(vertex):
    x, y = vertex.x, vertex.y
    if x > 0 and y > 0:
        return 1   # Quadrant I
    elif x < 0 and y > 0:
        return 2  # Quadrant II
    elif x < 0 and y < 0:
        return 3 # Quadrant III
    elif x > 0 and y < 0:
        return 4  # Quadrant IV

def are_adjacent_quadrants(quadrants):    
    n = len(quadrants)
    if n == 1:
        # If there's only 1 quadrant, return True (it's technically adjacent to itself)
        return True
    elif n == 2:
        # If there are exactly 2 quadrants, check if they are adjacent
        return abs(quadrants[0]-quadrants[1]) != 2
    else:
        # More than 2 quadrants -> not adjacent
        return False

def get_distal_outlier_vertex(convex_hull, radius):

    outliers = []
    quadrants = set()

    for v in get_world_vertices(convex_hull):
        norm = math.sqrt(v.x**2 + v.y**2) # square norm is too penalizing
        if norm > radius:
            outliers.append((v, norm))
            quadrants.add(get_vertex_quadrant(v))
    
    quadrants = list(quadrants)

    if len(outliers) == 0:
        return None, None
    
    if are_adjacent_quadrants(quadrants):
        return max(outliers, key=lambda item: item[1])[0], quadrants
    else:
        return -1, quadrants

def center_adjust_radial(bounding_box, convex_hull, radius):
    quadrants_history = deque(maxlen=4)  # to store last few quadrant states
        
    while True:
        distal_v, quadrants = get_distal_outlier_vertex(convex_hull, radius)
        
        if distal_v == -1:
            return False # cannot remove intersections (non adjacent quadrants)
        if distal_v is not None:
            quadrants_history.append(quadrants) # register current quadrants occupied

            if len(quadrants_history) == 4:
                if quadrants_history[0] == quadrants_history[2] and quadrants_history[1] == quadrants_history[3]:
                    # deadlock
                    return False
                
            transform.attract(bounding_box, distal_v)

            continue
        else:
            return True  # removed intersections

def center_adjust(bounding_box, convex_hull, mode='axial', adjust_axis=None, radius=None, bounds=None):
    if mode == 'axial':
        if center_adjust_axial(bounding_box, convex_hull, adjust_axis, bounds):
            return True
    else:
        if center_adjust_radial(bounding_box, convex_hull, radius):
            return True
    
    return False

def try_rotate_adjust(bounding_box, convex_hull, rotation_axis, rotation_mode='global', adjust_mode='axial', adjust_axis=None, radius=None, bounds=None, max_rotation=transform.max_rotation):

    total_rotation = 0.0

    while total_rotation < max_rotation:
        
        if center_adjust(bounding_box, convex_hull, adjust_mode, adjust_axis, radius, bounds):
            return True
        
        # still radial intersections, continue rotating
        
        if rotation_mode == 'local':
            bounding_box.rotation_euler.rotate_axis(rotation_axis.to_euler(), transform.rotation_step) # local rotation
        else:
            bounding_box.rotation_euler[rotation_axis.to_index()] += transform.rotation_step # global rotation

        total_rotation += transform.rotation_step
        commands.update_scene() # recalc local matrices

    # check if last rotation resolved
    return center_adjust(bounding_box, convex_hull, adjust_mode, adjust_axis, radius, bounds)

def try_remove_radial(bounding_box, convex_hull, radius, height):
        
    initial_transform = transform.save(bounding_box)

    if bounding_box.rotation_euler != Euler((0,0,0)):
        # z tilted, try to rotate adjust circular around local z axis
        if try_rotate_adjust(bounding_box,convex_hull, rotation_mode='local', rotation_axis=Axis.z, adjust_mode='radial', radius=radius, max_rotation=math.radians(180)):
            # removed, check for vertical intersections
            if center_adjust_axial(bounding_box, convex_hull, Axis.z, bounds=height):
                return True
    
    # cannot remove with local z rotation, try horizontal component rotation
    transform.store(bounding_box, initial_transform)
    
    if try_rotate_adjust(bounding_box, convex_hull, rotation_axis=Axis.x, adjust_mode='radial', radius=radius):
        # removed radial intersections
        # check for formed vertical intersections
        if center_adjust_axial(bounding_box, convex_hull, Axis.z, bounds=height):
            return True
    
    # roll back and try on y
    transform.store(bounding_box, initial_transform)
    
    if try_rotate_adjust(bounding_box, convex_hull, rotation_axis=Axis.y, adjust_mode='radial', radius=radius):
        # removed radial intersecions
        # check for formed vertical intersections
        if center_adjust_axial(bounding_box, convex_hull, Axis.z, bounds=height):
            return True
        else:
            # cannot remove radial intersections, failed
            return False
    else:
        return False