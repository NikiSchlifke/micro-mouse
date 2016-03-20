import copy
import numpy as np
from enum import Enum

Delta = [[-1,  0], # go north
         [ 0,  1], # go east
         [ 1,  0], # go south
         [ 0, -1]] # go west

"""
The robot steering (Delta index moves)
"""
class Steering(Enum):    
    L, F, R = (-1,0,1) # Left, Forward, Right

    def __str__(self):
        return self.name

"""
The robot direction
"""
class Direction(Enum):
    N, E, S, W = range(4) # North, East, South, West

    def reverse(self):
        return Direction((self.value+2)%4)

    # adjust the direction by steering value
    def adjust(self, steering):
        return Direction((self.value+steering.value)%4)

    def delta(self):
        return Delta[self.value]

    # returns a steering value based on the difference between two directions
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

    # adjust the location and direction by the steering and movement
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

    # return the distance from the robot to the walls given a steering value
    def distance(self, steering):
        steering_sensor_index_map = {
            Steering.L : 0,
            Steering.F : 1,
            Steering.R : 2
        }
        return self.sensors[steering_sensor_index_map[steering]]

    # True if the all sensors returns 0
    def isDeadEnd(self):
        return max(self.sensors)==0

    # forward path only (left and right are walls)
    def isForwardOnly(self):
        return self.forward()>0 and self.left()==0 and self.right()==0

    # left path only (forward and right are walls)
    def isLeftOnly(self):
        return self.forward()==0 and self.left()>0 and self.right()==0

    # right path only (left and forward are walls)
    def isRightOnly(self):
        return self.forward()==0 and self.left()==0 and self.right()>0

    # distance to the left wall
    def left(self):
        return self.sensors[0]

    # distance to the forward wall
    def forward(self):
        return self.sensors[1]

    # distance to the right wall
    def right(self):
        return self.sensors[2]

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
        self.data_type = type(init_val)

    def __getitem__(self, row):
        return self.grid[row]

    def getValue(self, location):
        return self.grid[location[0]][location[1]]

    def setValue(self, location, value):
        self.grid[location[0]][location[1]] = value

    def isValid(self, location):
        row, col = location
        return 0 <= row and row < self.rows and 0 <= col and col < self.cols

    def area(self):
        return self.rows * self.cols

    # print the whole grid values (differnt format is used based on the initial value data type)
    def __str__(self):
        if self.data_type == int or self.data_type == float:
            return '\n'.join(','.join('{:2d}'.format(val) for val in row) for row in self.grid)
        return '\n'.join(','.join('{}'.format(val) for val in row) for row in self.grid)

"""
Maps the maze
"""
class Mapper(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, -1) 

    # this method is used by the A* search test program to read the test maze file
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

    # Expand the maze mapping as the robot explores
    #
    # It uses the same maze encoding as the test maze file format:
    #
    # - North = 1 = 2^0 = 2^Direction.N.value 
    # - East  = 2 = 2^1 = 2^Direction.E.value
    # - South = 3 = 2^2 = 2^Direction.S.value
    # - West  = 4 = 2^3 = 2^Direction.W.value
    #
    def expand(self, heading, sensor):
        value = 0
        # Use the sensor values to map the left, forward, right walls/paths
        for s in Steering:
            if sensor.distance(s)>0:
                i = heading.direction.adjust(s).value
                value += 2**i
        # We don't have a back sensor.  Use the value already mapped for the back.
        backward = heading.backward()
        if self.canMove(backward.reverse()):
            value += 2**backward.direction.value
        self.setValue(heading.location, value)

    # return True if we can move to a direction at a location specified in a Heading value
    def canMove(self, heading):
        location = heading.location
        direction = heading.direction
        if not self.isValid(location) or self.isUnknown(location):
            return False
        value = self.getValue(location)
        i = direction.value
        return (value & 2**i) > 0

    # return True if there are only two ways to move indicating the location is part of one way path
    def isOneWay(self, location):
        directions = sum(1 for d in Direction if self.canMove(Heading(d, location)))
        return directions <= 2

    def isUnknown(self, location):
        return self.getValue(location)==-1

"""
Keeps track of dead ends using one Grid object per direction
"""
class DeadEnds(object):
    def __init__(self, rows, cols):
        # keep track of dead ends for each direction
        self.deadEndsMap = { d:Grid(rows, cols, '_') for d in Direction }
        self.rows = rows
        self.cols = cols

    # update dead end paths as the robot explores using the sensor values
    # and the mapper values to see where the dead end paths are
    def update(self, heading, sensor, maze):
        if sensor.isDeadEnd():
	    self.setDeadEnd(heading)
        if self.isDeadEnd(heading.forward()):
	    if sensor.isForwardOnly():
	        self.setDeadEnd(heading)
            elif maze.isOneWay(heading.location):
		if sensor.left()>0 and sensor.right()==0:
		    self.setDeadEnd(heading.right(0))
		elif sensor.left()==0 and sensor.right()>0:
		    self.setDeadEnd(heading.left(0))
        if self.isDeadEnd(heading.backward()):
	    if sensor.isForwardOnly():
		self.setDeadEnd(heading.reverse())
	    elif sensor.isLeftOnly():
		self.setDeadEnd(heading.right(0))
	    elif sensor.isRightOnly():
		self.setDeadEnd(heading.left(0))

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
        grid = Grid(self.rows, self.cols, '_')
        for d in Direction:
            deadEnd = self.deadEndsMap[d]
            for row in range(self.rows):
                for col in range(self.cols):
                    location = (row, col)
                    if deadEnd.getValue(location) != '_':
                        grid.setValue(location, d.name)
        return '{}'.format(grid)

"""
Keep track of how often each cell is visited
"""
class Counter(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, 0)

    def increment(self, location):
        row, col = location
        self.grid[row][col] += 1

    # This return a tuple with three values
    # - coverage = (the number of cells visited)/(the total number of cells)
    # - average = average count value (excluding zero values)
    # - standard deviation of count values (excluding zero values)
    def coverage(self):
        rows, cols = self.shape
        values = np.array([self.grid[r][c] for r in range(rows) for c in range(cols) if self.grid[r][c]>0])
        return 100.0*len(values)/self.area(), np.average(values), np.std(values)

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
        while len(open)>0:
            h,l = open.pop(0)
            self.setValue(l, h)

            isUnknown = maze.isUnknown(l)
            for d2 in Direction:
                delta = d2.delta() 
                l2 = (l[0]+delta[0], l[1]+delta[1])
                # we can move or unknown teritory
                if maze.canMove(Heading(d2, l)) or (isUnknown and self.isValid(l2)):
                    v2 = self.getValue(l2)
                    if v2==-1:
                        open.append((h+1,l2))
