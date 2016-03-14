import os
import time
from controller import *

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        '''
        rows, cols = maze_dim, maze_dim
        try:
            controller_name = os.environ['CONTROL']
        except:
            controller_name = ''
        if controller_name=='random':
            self.controller = Controller_Random(rows, cols)
        elif controller_name=='deadend':
            self.controller = Controller_DeadEnd(rows, cols)
        elif controller_name=='counter':
            self.controller = Controller_Counter(rows, cols)
        elif controller_name=='heuristic':
            self.controller = Controller_Heuristic(rows, cols)
        else:
            self.controller = Controller(rows, cols) # this does nothing

        try:
            self.tick_delay = float(os.environ['DELAY'])
        except:
            self.tick_interval = 0

        self.init_heading = Heading(Direction.N, [rows-1, 0])
        self.is_training = True
        self.time = 0
        self.reset()

    def reset(self):
        self.heading = self.init_heading
        self.controller.reset(self.heading)

    def tick(self):
        self.time += 1
        if self.tick_delay>0:
            time.sleep(self.tick_delay)

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

        heading = self.heading
        sensor = Sensor(sensors)

        try:
            if self.is_training:
                steering, movement = self.controller.explore(heading, sensor)
            else:
                steering, movement = self.controller.exploit(heading, sensor)
        except ResetException:
            self.is_training = False
            self.reset()
            return ('Reset', 'Reset')

        # check the steering and movement against sensor values
        if sensor.distance(steering)>=movement:
            # update our direction and location
            self.heading = heading.adjust(steering, movement)
            # map steering to rotation
            steering_rotation_map = {
                Steering.R :  90,
                Steering.F :   0,
                Steering.L : -90
            }
            rotation = steering_rotation_map[steering]
        else:
            rotation = 0
            movement = 0

        print '{:03d} {} {} [{:>2d},{:>2d},{:>2d}] {:>3d},{:>2d} => {}'.format(
            self.time, 
            self.controller,
            heading,
            sensors[0], sensors[1], sensors[2],
            rotation,
            movement,
            self.heading)

        self.tick()

        return rotation, movement
