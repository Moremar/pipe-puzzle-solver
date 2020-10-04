import logging
from utils import setup_logging
from pipe_engine import PipeEngine, Move, GROW, SHRINK, ROLLBACK
from point import Point


class BruteForceEngine(PipeEngine):
    def __init__(self, grid_size: int, pipe_ends: list):
        super().__init__(grid_size, pipe_ends)
        self.curr_pipe = -1
        self.init_next_pipe()

    def init_next_pipe(self):
        self.curr_pipe += 1
        start = self.pipe_ends[self.curr_pipe][0]
        self.paths.append([(start, self.possible_dirs(start, self.curr_pipe))])

    def next_move(self) -> Move:
        logging.debug(self.display())
        curr_point, moves = self.paths[self.curr_pipe][-1]
        if len(moves) == 0 or self.is_doomed():
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
                    return Move(GROW, self.curr_pipe, next_point)

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

    def is_doomed(self) -> bool:
        """Hook for children classes to let the engine know early that a path is doomed to fail"""
        return False


if __name__ == "__main__":
    setup_logging()
    size = 4
    pipes = [
       (Point(0, 0), Point(3, 1)),
       (Point(1, 1), Point(3, 0)),
       (Point(0, 3), Point(3, 2)),
    ]

    engine = BruteForceEngine(size, pipes)
    while not engine.solved:
        move = engine.next_move()
        logging.debug(move)
    logging.info(engine.display())
