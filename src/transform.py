from enum import Enum
from . import commands
import math

class Axis(Enum):
    x = 'x'
    y = 'y'
    z = 'z'

class RotationAxis(Enum):
    x = 0
    y = 1
    z = 2

class Direction(Enum):
    positive = 1
    negative = -1

adjustment_step = 0.01
rotation_step = math.radians(1)

def nudge(object, axis, direction, step=adjustment_step):
    axis = axis.value
    direction = direction.value
    coord = getattr(object.location, axis)
    coord += direction*step
    setattr(object.location, axis, coord)
    commands.update_scene()