from enum import Enum
from . import commands
import math
from mathutils import Vector

class Axis(Enum):
    x = 'x'
    y = 'y'
    z = 'z'

    def to_index(self):
        match self.value:
            case 'x':
                return 0
            case 'y':
                return 1
            case 'z':
                return 2
            
    def to_euler(self):
        return self.value.upper()

class Direction(Enum):
    positive = 1
    negative = -1

adjustment_step = 0.01
rotation_step = math.radians(1)
max_rotation = math.radians(90)

def nudge(object, axis, direction,):
    axis = axis.value
    direction = direction.value
    coord = getattr(object.location, axis)
    coord += direction*adjustment_step
    setattr(object.location, axis, coord)
    commands.update_scene()

def attract(object, vertex):
    nudge_vector = Vector((-vertex.co.x,-vertex.co.y,0)).normalized()*adjustment_step
    object.location += nudge_vector
    commands.update_scene()

def save(object):
    return (object.location.copy(), object.rotation_euler.copy())

def store(object, transform):
    object.location = transform[0]
    object.rotation_euler = transform[1]
    commands.update_scene()