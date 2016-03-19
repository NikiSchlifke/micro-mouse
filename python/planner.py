from util import *
import sys

"""
A* search
"""
def findOptimalMoves(maze, goal, heuristic):
    rows, cols = maze.shape
    closed = Grid(rows, cols, 0)
    action = Grid(rows, cols, '_')

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
            if maze.canMove(Heading(d2, l)): 
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

    path_count = 0
    path = Grid(rows, cols, ' ')

    move_count = 0
    moves = []

    if goal_reached:
        path.setValue(l, '*')
        while l != start:
            d = action.getValue(l)
            if d == '_':
                break
            delta = d.delta()
            l = (l[0] - delta[0], l[1] - delta[1])                 
            path.setValue(l, d)
            path_count += 1
        # convert direction to steering
        heading = Heading(Direction.N, start)
        while not goal.isGoal(heading.location):
            direction = path.getValue(heading.location)
            steering = heading.direction.steer(direction)
            movement = 1
            while movement < 3:
                next_heading = heading.adjust(steering, movement)
                next_direction = path.getValue(next_heading.location)
                if next_direction != direction:
                    break
                movement += 1
            moves.append((steering, movement))
            heading = heading.adjust(steering, movement)
            move_count += 1

    print '-- Maze --'
    print maze
    print '-- Heuristic --'
    print heuristic
    print '-- Closed --'
    print closed
    print '-- Action --'
    print action
    print '-- Path --'
    print path
    print 'Path Length! {}'.format(path_count)
    print '-- Moves --'
    for steering, movement in moves:
        print '({},{})'.format(steering, movement)
    print '# of Moves! {}'.format(move_count)

    return moves

if __name__ == '__main__':
    filename = sys.argv[1]
    maze = Mapper.openMazeFile(filename)
    rows, cols = maze.shape
    goal = Goal(rows, cols)
    heuristic = Heuristic(maze)
    findOptimalMoves(maze, goal, heuristic)
