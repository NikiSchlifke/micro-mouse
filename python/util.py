import copy
from enum import Enum

Delta = [[-1,  0], # go north
         [ 0,  1], # go east
         [ 1,  0], # go south
         [ 0, -1]] # go west

class Steering(Enum):    
    L, F, R = (-1,0,1) # Left, Forward, Right

class Direction(Enum):
    N, E, S, W = range(4) # North, East, South, West

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
    def __init__(self, rows, cols):
        self.goal_row_max = rows/2
        self.goal_row_min = rows/2-1
        self.goal_col_max = cols/2
        self.goal_col_min = cols/2-1

    def isGoal(self, location):
        row, col = location
        return self.goal_row_min <= row and row <= self.goal_row_max and \
               self.goal_col_min <= col and col <= self.goal_col_max

"""
Grid for keep track of values
"""
class Grid(object):
    def __init__(self, rows, cols ,init_val):
        self.rows = rows
        self.cols = cols
        self.grid = [ [ copy.deepcopy(init_val) for c in range(cols) ] for r in range(rows) ]

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
Maps the maze
"""
class Mapper(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, (-1)) 

    def expand(self, heading, sensor):
        if self.getValue(heading.location) >= 0:
            return
        value = 0
        for s in Steering:
            i = heading.direction.adjust(s).value
            if sensor.distance(s)>0:
                value += 2**i
        back = heading.backward().location
        if self.isValid(back):
            i = heading.direction.value
            if i & self.getValue(back)>0:
                value += 2**heading.direction.reverse().value
        print value, heading.location
        self.setValue(heading.location, value)

"""
Keep track of how often each cell is visited
"""
class Counter(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, 0)

    def increment(self, location):
        row, col = location
        self.grid[row][col] += 1

"""
Keeps track of dead ends
"""
class DeadEnds(object):
    def __init__(self, rows, cols):
        # keep track of dead ends for each direction
        self.deadEndsMap = { d:Grid(rows, cols, '_') for d in Direction }

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
Heuristic
"""
class Heuristic(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, -1)

        # set center values to zero
        open = [ (0, rows/2+r-1, cols/2+c-1) for r in range(2) for c in range(2) ]

        # expand from the center
        while len(open)>0:
            for h,r,c in open:
                self.grid[r][c] = h

            next_open = []
            for h,r,c in open:
                for d in Delta:
                    r2 = r + d[0]
                    c2 = c + d[1]
                    if r2>=0 and r2<rows and c2>=0 and c2<cols:
                        v2 = self.grid[r2][c2]
                        if v2==-1:
                            next_open.append((h+1,r2,c2))
            open = next_open

