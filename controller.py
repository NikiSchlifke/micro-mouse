import random
from enum import Enum

Delta = [[-1,  0], # go north
         [ 0, -1], # go west
         [ 1,  0], # go south
         [ 0,  1]] # go east

class Direction(Enum):
    N, W, S, E = range(4)

class Steering(Enum):    
    Right, Straight, Left = (-1,0,1)

"""
Utility for sensors
"""
class Sensor:
    SteeringMap = {
        Steering.Left     : 0,
        Steering.Straight : 1,
        Steering.Right    : 2
    }

    def __init__(self, sensors):
        self.sensors = sensors

    def distance(self, steering):
        return self.sensors[Sensor.SteeringMap[steering]]

    def isDeadEnd(self):
        return max(self.sensors)==0

    def random(self):
        if self.isDeadEnd():
            return random.choice([Steering.Left, Steering.Right])
        return random.choice([s for s in list(Steering) if self.distance(s) > 0])
"""
Encapsulate direction @ location
"""
class Heading(object):
    def __init__(self, direction, location):
        self.direction = direction
        self.location = location

    def __str__(self):
        return '{} @ ({:>2d},{:>2d})'.format(
            self.direction.name, self.location[0], self.location[1])

    def adjust(self, steering, movement):
        direction = Direction((self.direction.value+steering.value)%4)
        delta = Delta[direction.value]
        location = [ self.location[i]+delta[i]*movement for i in range(2) ]
        return Heading(direction, location)

"""
Raise this exception when exploration is over
"""
class ResetException(Exception):
    pass

"""
Base Controller
"""
class Controller(object):
    def explore(self, heading, sensors):
        return (Steering.Straight, 0)

    def exploit(self, heading, sensors):
        return (Steering.Straight, 0)

    def random(self, sensor, movement):
        steering = sensor.random()
        if sensor.isDeadEnd():
            movement = 0
        return (steering, movement)

class RandomController(Controller):
    def explore(self, heading, sensor):
        return self.random(sensor, 1)

    def exploit(self, heading, sensors):
        return self.explore(heading, sensors)
