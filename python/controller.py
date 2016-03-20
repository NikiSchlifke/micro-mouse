import random
from util import *
from planner import *

"""
Controller (base)
"""
class Controller(object):
    # return true if it wants to end the 1st run
    def canReset(self, robot):
        return robot.goal.isGoal(robot.heading.location)

    # this is called every step
    def search(self, robot):
        return (Steering.F, 1) # override this

    # for priting the class name
    def __str__(self):
        tokens = self.__class__.__name__.split('_')
        return tokens[1] if len(tokens)>1 else 'Base'

"""
Controller Exploration
"""
class Controller_Exploration(Controller):
    # react to deadend or make a choice
    def search(self, robot):
        steerings = self.steerings(robot)
        if len(steerings)==0:
            return self.deadEnd(robot)
        return self.choose(robot, steerings)

    # returns available ways to move
    def steerings(self, robot):
        sensor = robot.sensor
        return [s for s in Steering if sensor.distance(s)>0]

    # action at dead end path
    def deadEnd(self, robot):
        return (Steering.F, 0) # override this

    # action at normal path
    def choose(self, robot, steerings):
        return (Steering.F, 0) # override this

"""
Controller Random
- randomly move to where it has no wall
- at dead-end, it turns left or right 
"""
class Controller_Random(Controller_Exploration):
    def deadEnd(self, robot):
        # randomly turn at dead end
        return (random.choice([Steering.L, Steering.R]), 0)

    def choose(self, robot, steerings):
        # randomly choose available steering direction
        return (random.choice(steerings), 1)

"""
Controller that detects dead ends
"""
class Controller_DeadEnd(Controller_Random):
    def steerings(self, robot):
        heading = robot.heading
        sensor = robot.sensor
        deadEnds = robot.deadEnds
        # avoid dead ends and any path to it
        return [s for s in Steering if sensor.distance(s)>0 and not deadEnds.isDeadEnd(heading.adjust(s, 1))]

"""
Back off from deadend - a bad idea
"""
class Controller_DeadEnd2(Controller_DeadEnd):
    def deadEnd(self, robot):
        # back off at dead end
        return (Steering.F, -1)

"""
Controller that keep tracks how often each cell is visited
"""
class Controller_Counter(Controller_DeadEnd):
    def choose(self, robot, steerings):
        heading = robot.heading
        counter = robot.counter
        options = []
        for s in steerings:
            location = heading.adjust(s,1).location
            c = counter.getValue(location)
            options.append((c, s.value))
        options.sort()
        return (Steering(options[0][1]), 1)

"""
Controller that uses Heuristic value to choose a path
"""
class Controller_Heuristic(Controller_Counter):
    def choose(self, robot, steerings):
        heading = robot.heading
        counter = robot.counter
        heuristic = robot.heuristic
        options = []
        for s in steerings:
            location = heading.adjust(s,1).location
            c = counter.getValue(location)
            h = heuristic.getValue(location)
            options.append((c, h, s.value))
        options.sort()
        return (Steering(options[0][2]), 1)

"""
Follow the optimal moves given mapped area
"""
class Controller_Exploitation(Controller):
    def __init__(self, robot):
        self.moves = findOptimalMoves(robot.maze, robot.goal, robot.heuristic)

    # this controller is used in 2nd run - can not reset
    def canReset(self, robot):
        return False

    # just follow the moves
    def search(self, robot):
        return self.moves.pop(0)

