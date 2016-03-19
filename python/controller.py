import random
from util import *
from planner import *

"""
Controller (base)
"""
class Controller(object):
    # returns True when it wants to finish the exploration
    def canReset(self, robot):
        return robot.goal.isGoal(robot.heading.location)

    # this is called every step
    def search(self, robot):
        return (Steering.F, 1)

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
    def search(self, robot):
        if self.isDeadEnd(robot):
            steering, movement = self.deadEnd(robot)
        else:
            steering, movement = self.choose(robot)
        return (steering, movement)

    def isDeadEnd(self, robot):
        sensor = robot.sensor
        return sensor.isDeadEnd()

    def deadEnd(self, robot):
        # randomly turn at dead end
        steering = random.choice([Steering.L, Steering.R])
        movement = 0
        return (steering, movement)

    def choose(self, robot):
        # randomly choose available steering direction
        steering = random.choice(self.steerings(robot))
        movement = 1
        return (steering, movement)

    def steerings(self, robot):
        sensor = robot.sensor
        return [s for s in Steering if sensor.distance(s)>0]

"""
Controller that detects dead ends
"""
class Controller_DeadEnd(Controller_Random):
    def isDeadEnd(self, robot):
        heading = robot.heading
        deadEnds = robot.deadEnds
        return deadEnds.isDeadEnd(heading)

    def deadEnd(self, robot):
        sensor = robot.sensor
        if sensor.isDeadEnd():
            # back off at dead end by sensor
            steering = Steering.F
            movement = -1
        else:
            steering, movement = Controller_Random.deadEnd(self, robot)
        return (steering, movement)

    def steerings(self, robot):
        heading = robot.heading
        sensor = robot.sensor
        deadEnds = robot.deadEnds
        # avoid dead ends
        return [s for s in Steering if sensor.distance(s)>0 and not deadEnds.isDeadEnd(heading.adjust(s, 1))]

"""
Controller that keep tracks how often each cell is visited
"""
class Controller_Counter(Controller_DeadEnd):
    def choose(self, robot):
        heading = robot.heading
        counter = robot.counter
        options = []
        for s in self.steerings(robot):
            location = heading.adjust(s,1).location
            c = counter.getValue(location)
            options.append((c, s.value))
        options.sort()
        steering = Steering(options[0][1])
        movement = 1
        return (steering, movement)

"""
Controller that uses Heuristic value to choose a path
"""
class Controller_Heuristic(Controller_Counter):
    def choose(self, robot):
        heading = robot.heading
        counter = robot.counter
        heuristic = robot.heuristic
        options = []
        for s in self.steerings(robot):
            location = heading.adjust(s,1).location
            c = counter.getValue(location)
            h = heuristic.getValue(location)
            options.append((c, h, s.value))
        options.sort()
        steering = Steering(options[0][2])
        movement = 1
        return (steering, movement)

"""
Follow the optimal moves
"""
class Controller_Optimal(Controller):
    def __init__(self):
        self.moves = []

    def canReset(self, robot):
        return False

    def search(self, robot):
        if len(self.moves)==0:
            self.moves = findOptimalMoves(robot.maze, robot.goal, robot.heuristic)
        return self.moves.pop(0)

