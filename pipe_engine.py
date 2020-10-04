from abc import abstractmethod
from typing import Optional

from point import Point


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
        self.solved = False
        self.init_universe()

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
                res += self.universe[i, j]
            res += '\n'
        return res

    @abstractmethod
    def next_move(self) -> Move:
        pass
