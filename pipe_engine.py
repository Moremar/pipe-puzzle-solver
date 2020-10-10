from abc import abstractmethod
from typing import Optional

from point import Point


# Move types
GROW = "grow"          # Add a cell at the end of a pipe
SHRINK = "shrink"      # Remove the last cell of a pipe
ROLLBACK = "rollback"  # Remove the pipe (to fix the previous ones)


class Move:
    def __init__(self, move_type: str, pipe_id: int, point: Optional[Point], prev_pipe_id=None):
        self.move_type = move_type
        self.pipe_id = pipe_id
        self.point = point  # point added (GROW) or removed (SHRINK) to the pipe
        self.prev_pipe_id = prev_pipe_id  # only for ROLLBACK, previous pipe to disconnect

    def __repr__(self) -> str:
        return "Move({0}, {1}, {2})".format(self.move_type, self.pipe_id, self.point)


class PipeEngine:
    def __init__(self, grid_size: int, pipe_ends: list):
        self.grid_size = grid_size
        self.pipe_ends = pipe_ends
        self.universe = dict()
        self.paths = []
        self.solved = False
        self.init_universe()
        # some algos do not process the pipes in the order they were provided
        # so we use a mapping array :
        #  - the index is the pipe process order
        #  - the value at the index is the original pipe_id in pipe_ends for this pipe
        self.pipes_mapping = [i for i in range(len(self.pipe_ends))]

    def original_id(self, pipe_id: int) -> int:
        return self.pipes_mapping[pipe_id]

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

    def possible_dirs(self, point: Point, pipe_id: int) -> list:
        return [adj for adj in point.adjacent_points()
                if self.universe[adj.x, adj.y] == '.' or adj == self.pipe_ends[pipe_id][1]]

    def display(self) -> str:
        res = 'Grid state:\n'
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                res += '{0: <3}'.format(self.universe[i, j])  # left aligned 3-width string
            res += '\n'
        return res

    def final_paths(self):
        """must be overridden in children class if the pipes have a different order in paths and pipe_ends"""
        return self.paths

    @abstractmethod
    def next_moves(self) -> [Move]:
        pass
