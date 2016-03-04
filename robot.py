import numpy as np
import random
import time

class Grid(object):
    def __init__(self, rows, cols ,init_val):
        self.rows = rows
        self.cols = cols
        self.grid = [ [ init_val for c in range(rows) ] for r in range(cols) ]

    def __getitem__(self, row):
        return self.grid[row]

    def log(self):
        for row in self.grid:
            print row 

class Heuristic(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, -1)

        # set center values to zero
        open = [ (0, rows/2+r-1, cols/2+c-1) for r in range(2) for c in range(2) ]

        delta = [[-1,  0], # go north
                 [ 0, -1], # go west
                 [ 1,  0], # go south
                 [ 0,  1]] # go east

        # expand from the center
        while len(open)>0:
            for h,r,c in open:
                self.grid[r][c] = h

            next_open = []
            for h,r,c in open:
                for d in delta:
                    r2 = r + d[0]
                    c2 = c + d[1]
                    if r2>=0 and r2<self.rows and c2>=0 and c2<self.cols:
                        v2 = self.grid[r2][c2]
                        if v2==-1:
                            next_open.append((h+1,r2,c2))
            open = next_open

class Counter(Grid):
    def __init__(self, rows, cols):
        Grid.__init__(self, rows, cols, 0)

    def increment(self, row, col):
        self.grid[row][col] += 1

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim

        # initial location
        self.row = maze_dim-1
        self.col = 0
        self.direction = 0 # up

        # hueristic
        self.heuristic = Heuristic(maze_dim, maze_dim)
        self.heuristic.log()

        # count visits at each location
        self.counter = Counter(maze_dim, maze_dim)
        self.counter.log()

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''

        print '(r,c)=',(self.row, self.col), 'direction', self.direction, 'sensors',sensors

        delta = [[-1,  0], # go north
                 [ 0, -1], # go west
                 [ 1,  0], # go south
                 [ 0,  1]] # go east

        turn_map   = { 'left':1,   'straight':0, 'right':-1 }
        sensor_map = { 'left':0,   'straight':1, 'right':2  }
        angle_map  = { 'left':-90, 'straight':0, 'right':90 }

        rotation = 0
        movement = 0

        # count the number of visits to the current location
        self.counter.increment(self.row, self.col)

        min_count = self.counter[self.row][self.col]
        moves = []
        for turn in ['left', 'right', 'straight']:
            d = (self.direction + turn_map[turn])%len(delta)
            r = self.row + delta[d][0]
            c = self.col + delta[d][1]
            if r>=0 and r<self.maze_dim and c>=0 and c<self.maze_dim:
                depth = sensors[sensor_map[turn]]
                print turn,delta[d],r,c, 'depth', depth
                if depth==0:
                    continue # hit wall
                count = self.counter[r][c]
                if count <= min_count:
                    min_count = count
                    h = self.heuristic[r][c]
                    moves.append((count, h, depth, d, r, c, turn))
        moves.sort()
        if len(moves)>0:
            moves.sort()
            count, h, depth, self.direction, self.row, self.col, turn = moves[0]
            movement = 1
            rotation = angle_map[turn]
        else:
            rotation = angle_map['left']
            self.direction = (self.direction + turn_map['left'])%len(delta)

        print 'rotation', rotation, 'movement', movement
        self.counter.log()        

        time.sleep(1)

        return rotation, movement
