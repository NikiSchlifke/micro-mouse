from util import *
import sys

"""
A* search
"""
def findOptimalPath(maze):
    rows, cols = maze.shape
    closed = Grid(rows, cols, 0)
    action = Grid(rows, cols, -1)
    path = Grid(rows, cols, ' ')
    heuristic = Heuristic(rows, cols)
    goal = Goal(rows, cols)

    start = (rows-1, 0) 
    closed.setValue(start, 1)

    g = 0
    h = heuristic.getValue(start)
    f = g+h

    cost = {
        Steering.L : 2,
        Steering.F : 1,
        Steering.R : 2
    }

    goal_reached = False
    open = [(f,h,g,start,Direction.N)]
    while len(open)>0:
        item = open.pop(0)

        f = item[0]
        h = item[1]
        g = item[2]
        l = item[3]
        d = item[4]

        if goal.isGoal(l):
            goal_reached = True
            break

        for d2 in Direction:
            if maze.canMove(l, d2): 
                delta = d2.delta()
                l2 = ( l[0] + delta[0], l[1] + delta[1])
                if maze.getValue(l2)>=0 and closed.getValue(l2)==0: 
                    g2 = g + (1 if d==d2 else 2)
                    h2 = heuristic.getValue(l2)
                    f2 = g2+h2
                    closed.setValue(l2, 1)
                    action.setValue(l2, d2)
                    open.append((f2,h2,g2,l2,d2))
        open.sort()

    if goal_reached:
        path.setValue(l, '*')
        while l != start:
            d = action.getValue(l)
            if d == -1:
                break
            delta = d.delta()
            l = (l[0] - delta[0], l[1] - delta[1])                 
            path.setValue(l, d)
        # convert direction to steering
        count = 0
        steering = Grid(rows, cols, ' ')
        l = start
        d = Direction.N
        while not goal.isGoal(l):
            s = d.steer(path.getValue(l))
            steering.setValue(l, s)
            d = d.adjust(s)
            delta = d.delta()
            l = (l[0] + delta[0], l[1] + delta[1])
            count += 1

    print 'maze'
    print maze
    print 'closed'
    print closed
    print 'action'
    print action
    print 'path'
    print path
    print 'steering'
    print steering
    print 'path length={}'.format(count)

    return steering

if __name__ == '__main__':
    filename = sys.argv[1]
    maze = Mapper.openMazeFile(filename)
    findOptimalPath(maze)
