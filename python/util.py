import copy
from enum import Enum

Delta = [[-1,  0], # go north
         [ 0,  1], # go east
         [ 1,  0], # go south
         [ 0, -1]] # go west

class Steering(Enum):    
    L, F, R = (-1,0,1) # Left, Forward, Right

    def __str__(self):
        return self.name

class Direction(Enum):
    N, E, S, W = range(4) # North, East, South, West

    def reverse(self):
        return Direction((self.value+2)%4)

    def adjust(self, steering):
        return Direction((self.value+steering.value)%4)

    def delta(self):
        return Delta[self.value]

    def steer(self, direction):
        diff = direction.value - self.value
        if diff ==3:
            diff = -1
        if diff ==-3:
            diff = 1
        return Steering(diff)

    def __str__(self):
        return self.name

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

    # both sides are walls
    def isOneWay(self):
        return self.sensors[0]==0 and self.sensors[1]>0 and self.sensors[2]==0

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
        self.shape = (rows, cols)

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
        Grid.__init__(self, rows, cols, -1) 

    @staticmethod
    def openMazeFile(filename):
        with open(filename, 'rb') as f:
            # First line should be an integer with the maze dimensions
            maze_dim = int(f.next())
            rows, cols = maze_dim, maze_dim
            maze = Mapper(rows, cols)

            # Subsequent lines describe the permissability of walls
            for c in range(cols):
                cells = f.next().split(',')
                for i in range(len(cells)):
                    r = rows-(i+1)
                    maze.setValue((r,c), int(cells[i].strip()))
        return maze

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
            if self.canMove(back, heading.direction):
                value += 2**heading.direction.reverse().value
        self.setValue(heading.location, value)

    def canMove(self, location, direction):
        if not self.isValid(location) or self.isUnknown(location):
            return False
        value = self.getValue(location)
        i = direction.value
        return value & 2**i > 0

    def isUnknown(self, location):
        return self.getValue(location)==-1

    def __str__(self):
        return '\n'.join(','.join('{:2d}'.format(val) for val in row) for row in self.grid)
"""
Keep track of how often each cell is visited
"""
class Counter(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, 0)

    def increment(self, location):
        row, col = location
        self.grid[row][col] += 1

    def __str__(self):
        return '\n'.join(','.join('{:2d}'.format(val) for val in row) for row in self.grid)
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
    def __init__(self, maze):
        rows, cols = maze.shape
        Grid.__init__(self, rows, cols, -1)

        # set center values to zero
        open = []
        for r in range(2):
            for c in range(2):
                l = (rows/2+r-1, cols/2+c-1)
                open.append((0,l))
                self.setValue(l, 0)

        # expand from the center
        self.expand(maze, open)

    def expand(self, maze, open):
        while len(open)>0:
            h,l = open.pop(0)
            self.setValue(l, h)

            isUnknown = maze.isUnknown(l)
            for d2 in Direction:
                delta = d2.delta() 
                l2 = (l[0]+delta[0], l[1]+delta[1])
                # we can move or unknown teritory
                if maze.canMove(l, d2) or (isUnknown and self.isValid(l2)):
                    v2 = self.getValue(l2)
                    if v2==-1:
                        open.append((h+1,l2))

    def __str__(self):
        return '\n'.join(','.join('{:2d}'.format(val) for val in row) for row in self.grid)
