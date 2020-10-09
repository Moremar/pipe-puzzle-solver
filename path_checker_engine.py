import logging

from utils import setup_logging
from brute_force_engine import BruteForceEngine
from point import Point

# Engine that checks after each move if there is still a way for each pipe
# to reach its goal using the cells not used yet.
# This allows to give up early when the goal of one of the next pipes is already no longer reachable


class PathCheckerEngine(BruteForceEngine):
    def __init__(self, grid_size: int, pipe_ends: list):
        super().__init__(grid_size, pipe_ends)

    def is_doomed(self):
        # For each remaining pipe to process, check if there exist at least one path to
        # connect the start to the end (even if several pipes use some common cells)
        for pipe_id in range(self.curr_pipe, len(self.pipe_ends)):
            start_point = self.paths[self.curr_pipe][-1][0] if (pipe_id == self.curr_pipe) \
                        else self.pipe_ends[self.original_id(pipe_id)][0]
            end_point = self.pipe_ends[self.original_id(pipe_id)][1]
            logging.debug("Check if there is a way for pipe {0} from {1} to {2}".format(
                pipe_id, start_point, end_point))
            if not self.exist_path(start_point, end_point, self.original_id(pipe_id)):
                # There is no existing path for this pipe so we already can give up this path
                return True
        return False

    def exist_path(self, p1: Point, p2: Point, pipe_id: int) -> bool:
        return self.shortest_path(p1, p2, pipe_id) > -1

    def shortest_path(self, p1: Point, p2: Point, pipe_id: int) -> int:
        """Breadth first search (BFS) to find if p2 is still reachable from p1"""
        to_process = [(p1, 0)]
        seen = set()
        while len(to_process) > 0:
            (p, depth) = to_process.pop(0)
            if p == p2:
                return depth
            seen.add(p)
            for adj in self.possible_dirs(p, pipe_id):
                if adj not in seen:
                    to_process.append((adj, depth + 1))
        return -1

    # override to re-order the paths
    def final_paths(self):
        return [self.paths[self.pipes_mapping.index(i)] for i in range(len(self.paths))]


if __name__ == "__main__":
    setup_logging()
    size = 10
    pipes = [
        (Point(0, 0), Point(2, 3)),
        (Point(0, 1), Point(4, 9)),
        (Point(1, 1), Point(6, 9)),
        (Point(2, 7), Point(4, 1)),
        (Point(3, 0), Point(5, 6)),
        (Point(3, 7), Point(4, 2)),
        (Point(4, 6), Point(5, 7)),
        (Point(6, 8), Point(9, 8)),
        (Point(7, 9), Point(8, 1)),
        (Point(8, 2), Point(9, 9)),
    ]

    engine = PathCheckerEngine(size, pipes)
    while not engine.solved:
        for next_move in engine.next_moves():
            logging.debug(next_move)
    logging.info(engine.display())
