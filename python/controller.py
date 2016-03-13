import random
from enum import Enum

Delta = [[-1,  0], # go north
         [ 0, -1], # go west
         [ 1,  0], # go south
         [ 0,  1]] # go east

class Steering(Enum):    
    R, F, L = (-1,0,1) # Right, Forward, Left, Backward

class Direction(Enum):
    N, W, S, E = range(4) # North, West, South, East

    def reverse(self):
        return Direction((self.value+2)%4)

    def adjust(self, steering):
        return Direction((self.value+steering.value)%4)

    def delta(self):
        return Delta[self.value]

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
        direction = self.direction.adjust(steering)
        delta = direction.delta()
        location = [ self.location[i]+delta[i]*movement for i in range(2) ]
        return Heading(direction, location)

    # move forward
    def forward(self, movement=1):
        return self.adjust(Steering.F, movement)

    # move to left
    def left(self, movement=1):
        return self.adjust(Steering.L, movement)

    # move to right
    def right(self, movement=1):
        return self.adjust(Steering.R, movement)

    # move backward with turning
    def backward(self, movement=1):
        return self.reverse().forward(movement)

    # only reverse the direction 
    def reverse(self):
        return Heading(self.direction.reverse(), self.location)

"""
Utility for sensors
"""
class Sensor:
    def __init__(self, sensors):
        self.sensors = sensors

    def distance(self, steering):
        steering_sensor_index_map = {
            Steering.L : 0,
            Steering.F : 1,
            Steering.R : 2
        }
        return self.sensors[steering_sensor_index_map[steering]]

    def isDeadEnd(self):
        return max(self.sensors)==0

    def __str__(self):
        return str(self.sensors)

"""
Check goal location
"""
class Goal(object):
    def __init__(self, maze_dim):
        self.goal_max = maze_dim/2
        self.goal_min = self.goal_max - 1

    def isGoal(self, location):
        row, col = location
        return self.goal_min <= row and row <= self.goal_max and \
               self.goal_min <= col and col <= self.goal_max

"""
Raise this exception when exploration is over
"""
class ResetException(Exception):
    pass

"""
Controller (base)
"""
class Controller(object):
    def init(self, maze_dim):
        self.goal = Goal(maze_dim)

    def isGoal(self, location):
        return self.goal.isGoal(location)

    # this is called just before a run begins
    def reset(self, heading):
        pass

    # this is called every step in the first run
    def explore(self, heading, sensors):
        return (Steering.F, 0)

    # this is called every step in the second run
    def exploit(self, heading, sensors):
        return (Steering.F, 0)

    # for priting the class name
    def __str__(self):
        tokens = self.__class__.__name__.split('_')
        return tokens[1] if len(tokens)>1 else 'Base'

"""
Controller Random
- randomly move to where it has no wall
- at dead-end, it turns left or right 
"""
class Controller_Random(Controller):
    def explore(self, heading, sensor):
        if self.isGoal(heading.location):
            raise ResetException
        return self.random(heading, sensor, 1)

    def exploit(self, heading, sensor):
        return self.random(heading, sensor, 1)

    def random(self, heading, sensor, movement):
        if sensor.isDeadEnd():
            # randomly turn at dead end
            steering = random.choice([Steering.L, Steering.R])
            movement = 0
        else:
            # randomly choose available steering direction
            steering = random.choice([s for s in Steering if sensor.distance(s)>0])
        return (steering, movement)

"""
Grid for keep track of values
"""
class Grid(object):
    def __init__(self, rows, cols ,init_val):
        self.rows = rows
        self.cols = cols
        self.grid = [ [ init_val for c in range(rows) ] for r in range(cols) ]

    def __getitem__(self, row):
        return self.grid[row]

    def getValue(self, location):
        return self.grid[location[0]][location[1]]

    def setValue(self, location, value):
        self.grid[location[0]][location[1]] = value

    def isValid(self, location):
        row, col = location
        return 0 <= row and row < self.rows and 0 <= col and col < self.cols

    def __str__(self):
        return '\n'.join(','.join('{}'.format(val) for val in row) for row in self.grid)

"""
Keeps track of dead ends
"""
class DeadEnds(object):
    def __init__(self, maze_dim):
        # keep track of dead ends for each direction
        self.deadEndsMap = { d:Grid(maze_dim, maze_dim, '_') for d in Direction }

    def reset(self, heading):
        # initial location is dead end
        self.setDeadEnd(heading.reverse())

    def update(self, heading, sensor):
        if sensor.isDeadEnd():
            self.setDeadEnd(heading)
        elif sensor.distance(Steering.L)==0 and sensor.distance(Steering.R)==0:
            if self.isDeadEnd(heading.forward()):
                self.setDeadEnd(heading)
            if self.isDeadEnd(heading.backward()):
                self.setDeadEnd(heading.reverse())

    def setDeadEnd(self, heading):
        deadEnds = self.deadEndsMap[heading.direction]
        if deadEnds.isValid(heading.location):
            deadEnds.setValue(heading.location, 'X')

    def isDeadEnd(self, heading):
        deadEnds = self.deadEndsMap[heading.direction]
        if deadEnds.isValid(heading.location):
            return deadEnds.getValue(heading.location)=='X'
        return False

    def __str__(self):
        return '\n'.join('{}\n{}'.format(d, self.deadEndsMap[d]) for d in Direction)

"""
Controller that detects dead ends
"""
class Controller_DeadEnd(Controller_Random):
    def init(self, maze_dim):
        Controller_Random.init(self, maze_dim)
        self.deadEnds = DeadEnds(maze_dim)

    def reset(self, heading):
        self.deadEnds.reset(heading)

    def random(self, heading, sensor, movement):
        self.deadEnds.update(heading, sensor)
        print heading, self.deadEnds
        if self.deadEnds.isDeadEnd(heading):
            # back off at dead end
            steering = Steering.F
            movement = -1
        else:
            # randomly choose available steering direction
            steering = random.choice([s for s in Steering if sensor.distance(s)>0])
        return (steering, movement)
