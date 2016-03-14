import random
import util

"""
Raise this exception when exploration is over
"""
class ResetException(Exception):
    pass

"""
Controller (base)
"""
class Controller(object):
    def __init__(self, rows, cols):
        self.goal = Goal(rows, cols)
        self.raiseIfGoal = True
        self.mapper = Mapper(rows, cols)

    # this is called just before a run begins
    def reset(self, heading):
        pass

    # this is called every step in the first run
    def explore(self, heading, sensor):
        self.mapper.expand(heading, sensor)
        print '--'
        print self.mapper
        self.checkGoal(heading.location)
        return self.onExplore(heading, sensor)

    # dummy
    def onExplore(self, heading, sensor):
        return (Steering.F, 1)

    # this is called every step in the second run
    def exploit(self, heading, sensor):
        return self.onExploit(heading, sensor)

    # dummy
    def onExploit(self, heading, sensor):
        return (Steering.F, 1)

    # check if we are at the goal
    def isGoal(self, location):
        return self.goal.isGoal(location)

    def checkGoal(self, location):
        if self.isGoal(location):
            if self.raiseIfGoal:
                raise ResetException
            else:
                return True
        return False

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
    def __init__(self, rows, cols):
        Controller.__init__(self, rows, cols)

    def onExplore(self, heading, sensor):
        return self.handle(heading, sensor, 1)

    def onExploit(self, heading, sensor):
        return self.handle(heading, sensor, 1)

    def handle(self, heading, sensor, movement):
        if sensor.isDeadEnd():
            # randomly turn at dead end
            steering = random.choice([Steering.L, Steering.R])
            movement = 0
        else:
            # randomly choose available steering direction
            steering = random.choice([s for s in Steering if sensor.distance(s)>0])
        return (steering, movement)

"""
Controller that detects dead ends
"""
class Controller_DeadEnd(Controller):
    def __init__(self, rows, cols):
        Controller.__init__(self, rows, cols)
        self.deadEnds = DeadEnds(rows, cols)

    def reset(self, heading):
        self.deadEnds.reset(heading)

    def onExplore(self, heading, sensor):
        return self.handle(heading, sensor, 1)

    def onExploit(self, heading, sensor):
        return self.handle(heading, sensor, 1)

    def handle(self, heading, sensor, movement):
        self.deadEnds.update(heading, sensor)
        print self.deadEnds
        if self.deadEnds.isDeadEnd(heading):
            # back off at dead end
            steering = Steering.F
            movement = -1
        else:
            # randomly choose available steering direction
            steering = random.choice([s for s in Steering if sensor.distance(s)>0])
        return (steering, movement)

"""
Controller that keep tracks how often each cell is visited
"""
class Controller_Counter(Controller_DeadEnd):
    def __init__(self, rows, cols):
        Controller_DeadEnd.__init__(self, rows, cols)
        self.counter = Counter(rows, cols)

    def handle(self, heading, sensor, movement):
        self.counter.increment(heading.location)
        self.deadEnds.update(heading, sensor)
        if self.deadEnds.isDeadEnd(heading):
            # back off at dead end
            steering = Steering.F
            movement = -1
        else:
            counts = []
            for s in Steering:
                if sensor.distance(s)>0:
                    location = heading.adjust(s,1).location
                    c = self.counter.getValue(location)
                    counts.append((c, s.value))
            counts.sort()
            steering = Steering(counts[0][1])
        return (steering, movement)

class Controller_Heuristic(Controller_Counter):
    def __init__(self, rows, cols):
        Controller_Counter.__init__(self, rows, cols)
        self.heuristic = Heuristic(rows, cols)

    def handle(self, heading, sensor, movement):
        self.counter.increment(heading.location)
        self.deadEnds.update(heading, sensor)
        if self.deadEnds.isDeadEnd(heading):
            # back off at dead end
            steering = Steering.F
            movement = -1
        else:
            counts = []
            for s in Steering:
                if sensor.distance(s)>0:
                    location = heading.adjust(s,1).location
                    c = self.counter.getValue(location)
                    h = self.heuristic.getValue(location)
                    counts.append((c, h, s.value))
            counts.sort()
            steering = Steering(counts[0][2])
        return (steering, movement)

