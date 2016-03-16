from util import *
import sys



if __name__ == '__main__':

    filename = sys.argv[1]
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

    print maze

    closed = Grid(rows, cols, 0)
    action = Grid(rows, cols, -1)
    expand = Grid(rows, cols, -1)
    path = Grid(rows, cols, ' ')
    heuristic = Heuristic(rows, cols)
    goal = Goal(rows, cols)

    start = (rows-1, 0) 
    closed.setValue(start, 1)

    g = 0
    h = heuristic.getValue(start)
    f = g+h
    count = 0

    open = [(f,g,h,start)]
    while len(open)>0:
        item = open.pop(0)

        f = item[0]
        g = item[1]
        h = item[2]
        l = item[3]

        expand.setValue(l, count)
        count += 1

        if goal.isGoal(l):
	    path.setValue(l, '*')
            while l != start:
                d = action.getValue(l)
                if d == -1:
                    break
		delta = d.delta()
                l2 = (l[0] - delta[0], l[1] - delta[1])                 
		path.setValue(l2, d)
		l = l2
            break

        for d in Direction:
            if maze.canMove(l, d): 
                delta = d.delta()
                l2 = ( l[0] + delta[0], l[1] + delta[1])
                if maze.getValue(l2)>=0 and closed.getValue(l2)==0: 
                    g2 = g+1
                    h2 = heuristic.getValue(l2)
                    f2 = g2+h2
                    closed.setValue(l2, 1)
                    action.setValue(l2, d)
                    open.append((f2,g2,h2,l2))
        open.sort()

    print 'closed'
    print closed
    print 'expand'
    print expand
    print 'action'
    print action
    print 'path'
    print path

    steering = Grid(rows, cols, ' ')
    l = start
    d = Direction.N
    while not goal.isGoal(l):
        diff = path.getValue(l).value - d.value
	if diff ==3:
	   diff = -1
        if diff ==-3:
	   diff = 1
	s = Steering(diff)
	steering.setValue(l, s)
	d = d.adjust(s)
	delta = d.delta()
	l2 = (l[0] + delta[0], l[1] + delta[1])
        print l, path.getValue(l), d, s, l2
	l = l2

    print steering


