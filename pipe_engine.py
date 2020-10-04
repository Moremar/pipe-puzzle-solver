import logging
from typing import Optional
from point import Point

LOGGING_LEVEL = logging.DEBUG

# Move types
GROW = "grow"          # Add a cell at the end of a pipe
SHRINK = "shrink"      # Remove the last cell of a pipe
ROLLBACK = "rollback"  # Remove the pipe (to fix the previous ones)


class Move:
    def __init__(self, move_type: str, pipe_id: int, point: Optional[Point], complete=False):
        self.move_type = move_type
        self.pipe_id = pipe_id
        self.point = point  # point added (GROW) or removed (SHRINK) to the pipe
        self.complete = complete

    def __repr__(self) -> str:
        return "Move({0}, {1}, {2}, {3})".format(self.move_type, self.pipe_id, self.point, self.complete)


class PipeEngine:
    def __init__(self, grid_size: int, pipe_ends: list):
        self.grid_size = grid_size
        self.pipe_ends = pipe_ends
        self.universe = dict()
        self.paths = []
        self.curr_pipe = -1
        self.solved = False
        self.init_universe()
        self.init_next_pipe()

    def init_universe(self):
        # create the grid surrounded by walls
        for i in range(-1, self.grid_size + 1):
            for j in range(-1, self.grid_size + 1):
                out_of_grid = (i == -1) or (i == self.grid_size) or (j == -1) or (j == self.grid_size)
                self.universe[i, j] = '#' if out_of_grid else '.'
        # put the pipe ends on the grid
        for (i, point) in enumerate(self.pipe_ends):
            self.universe[point[0].x, point[0].y] = str(i)
            self.universe[point[1].x, point[1].y] = str(i)

    def init_next_pipe(self):
        self.curr_pipe += 1
        start = self.pipe_ends[self.curr_pipe][0]
        self.paths.append([(start, self.possible_dirs(start, self.curr_pipe))])

    def possible_dirs(self, point: Point, pipe_id: int) -> list:
        return [adj for adj in point.adjacent_points()
                if self.universe[adj.x, adj.y] == '.' or adj == self.pipe_ends[pipe_id][1]]

    def next_move(self) -> Move:
        logging.debug(self.display())
        curr_point, moves = self.paths[self.curr_pipe][-1]
        if len(moves) == 0:
            # no possible move from here, revert the last move
            return self.shrink()
        else:
            # perform a move
            next_point = moves.pop(0)
            self.universe[next_point.x, next_point.y] = str(self.curr_pipe)
            if next_point != self.pipe_ends[self.curr_pipe][1]:
                self.paths[self.curr_pipe].append((next_point, self.possible_dirs(next_point, self.curr_pipe)))
                return Move(GROW, self.curr_pipe, next_point)
            else:
                # target reached
                logging.debug("Reached the goal for pipe " + str(self.curr_pipe))
                self.paths[self.curr_pipe].append((next_point, []))
                if self.curr_pipe < len(self.pipe_ends) - 1:
                    # move to next pipe
                    self.init_next_pipe()
                    return Move(GROW, self.curr_pipe - 1, next_point)
                else:
                    logging.info("Pipe puzzle solved")
                    # TODO it may use a path that does not cover all the universe
                    #      add a logic to check that later and consider as invalid
                    self.solved = True
                    self.display()
                    return Move(GROW, self.curr_pipe, next_point, True)

    def shrink(self) -> Move:
        point_to_shrink, _moves = self.paths[self.curr_pipe].pop()
        if len(self.paths[self.curr_pipe]) > 0:
            # remove the current point from the universe
            logging.debug("We are blocked, shrink the current pipe")
            self.universe[point_to_shrink.x, point_to_shrink.y] = '.'
            return Move(SHRINK, self.curr_pipe, point_to_shrink)
        else:
            # roll back the origin of the current pipe, so we remove this pipe from the state
            # and remove the last point of the path of the previous pipe
            logging.debug("We are blocked, rollback the current pipe to modify the previous pipe")
            self.paths.pop()
            self.curr_pipe -= 1
            self.paths[-1].pop()
            return Move(ROLLBACK, self.curr_pipe + 1, None)

    def display(self) -> str:
        res = 'Grid state:\n'
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                res += self.universe[i, j]
            res += '\n'
        return res


# Test in terminal with a simple example
#
#   0 0 0 2
#   1 1 0 2
#   1 0 0 2
#   1 0 2 2

if __name__ == "__main__":
    logging.basicConfig(
        format='[%(levelname)-7s] %(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p',
        level=LOGGING_LEVEL)
    size = 4
    pipes = [
       (Point(0, 0), Point(3, 1)),
       (Point(1, 1), Point(3, 0)),
       (Point(0, 3), Point(3, 2)),
    ]

    # size = 10
    # pipes = [
    #     (Point(0, 0), Point(2, 3)),
    #     (Point(0, 1), Point(4, 9)),
    #     (Point(1, 1), Point(6, 9)),
    #     (Point(2, 7), Point(4, 1)),
    #     (Point(3, 0), Point(5, 6)),
    #     (Point(3, 7), Point(4, 2)),
    #     (Point(4, 6), Point(5, 7)),
    #     (Point(6, 8), Point(9, 8)),
    #     (Point(7, 9), Point(8, 1)),
    #     (Point(8, 2), Point(9, 9)),
    # ]

    engine = PipeEngine(size, pipes)
    while not engine.solved:
        move = engine.next_move()
        logging.debug(move)
    logging.info(engine.display())