import logging

from utils import setup_logging
from pipe_engine import Move, GROW
from point import Point, LEFT, UP, RIGHT, DOWN
from path_checker_engine import PathCheckerEngine


class WallFollowerEngine(PathCheckerEngine):
    def __init__(self, grid_size: int, pipe_ends: list):
        super().__init__(grid_size, pipe_ends)

    def begin_next_moves_hook(self) -> [Move]:
        # when we start a new pipe, we first check if there is a pipe that can be connected
        # simply by following the walls
        if len(self.paths) == self.curr_pipe:
            (pipe_id, moves) = self.next_pipe_path_along_walls()
            if pipe_id != -1:
                # A pipe can be connected by following the wall, process it first
                current_index_of_pipe_id = self.pipes_mapping.index(pipe_id)
                self.pipes_mapping[current_index_of_pipe_id] = self.pipes_mapping[self.curr_pipe]
                self.pipes_mapping[self.curr_pipe] = pipe_id
                start = self.pipe_ends[pipe_id][0]

                self.paths.append([(start, [])])
                for move in moves:
                    self.universe[move.x, move.y] = str(pipe_id)
                    self.paths[self.curr_pipe].append((move, []))
                self.curr_pipe += 1
                return [Move(GROW, pipe_id, move) for move in moves]
        return []

    def is_wall(self, p: Point):
        symbol = self.universe[(p.x, p.y)]
        # pipes already completed count as walls
        return symbol == '#' or (symbol != '.' and self.pipes_mapping.index(int(symbol)) < self.curr_pipe)

    def get_wall_sequence(self, origin: Point):
        """Succession of points against the wall starting from a given point"""
        sequence = [origin]
        if all([self.is_wall(p) for p in origin.adjacent_points()]):
            # the origin point is surrounded by walls
            return sequence

        loop_done = False
        curr = origin

        # get the direction where the wall is
        wall_dir = LEFT if self.is_wall(curr.adj(LEFT)) \
            else UP if self.is_wall(curr.adj(UP)) \
            else RIGHT if self.is_wall(curr.adj(RIGHT)) \
            else DOWN if self.is_wall(curr.adj(DOWN)) \
            else LEFT if self.is_wall(curr.adj(UP).adj(LEFT)) \
            else UP if self.is_wall(curr.adj(UP).adj(RIGHT)) \
            else RIGHT if self.is_wall(curr.adj(DOWN).adj(RIGHT)) \
            else DOWN

        while not loop_done:
            # get the next point against the wall
            p = curr.adj(Point.next_dir(wall_dir))
            while self.is_wall(p):
                # changes the run direction if a wall is found
                wall_dir = Point.next_dir(wall_dir)
                p = curr.adj(Point.next_dir(wall_dir))

            sequence.append(p)
            loop_done = (p == sequence[0])
            curr = p
            if not self.is_wall(curr.adj(wall_dir)):
                wall_dir = Point.prev_dir(wall_dir)
        return sequence

    def next_pipe_path_along_walls(self):
        for pipe_id in range(self.curr_pipe, len(self.pipe_ends)):
            original_pipe_id = self.original_id(pipe_id)
            start: Point = self.pipe_ends[original_pipe_id][0]
            end: Point = self.pipe_ends[original_pipe_id][1]
            start_against_wall = any([self.is_wall(p) for p in start.adjacent_points() + start.diagonal_points()])
            end_against_wall = any([self.is_wall(p) for p in end.adjacent_points() + end.diagonal_points()])
            if not start_against_wall or not end_against_wall:
                # both ends are not against the wall, no need to check this pipe
                continue

            # get the sequence of points against the wall (first and last are the start point)
            wall_sequence = self.get_wall_sequence(start)
            pipes_on_walls = []
            for point in wall_sequence:
                symbol = self.universe[point.x, point.y]
                if symbol == '.':
                    continue
                else:
                    pipes_on_walls.append(int(symbol))

            if pipes_on_walls.count(original_pipe_id) != 3:
                # the start of the pipe is at the beginning and at the end, if we also have the end it makes 3
                continue

            if len(pipes_on_walls) == 3:
                # rare case when there are only the 2 ends of our pipe on the wall
                # we cannot know what direction to go around the wall so skip it
                continue

            if pipes_on_walls[1] != original_pipe_id and pipes_on_walls[-2] != original_pipe_id:
                # the 2 ends of the pipe are against the wall but not following each other
                continue

            moves = []
            if pipes_on_walls[1] == original_pipe_id:
                # the end is following the start along the wall
                for i in range(1, len(wall_sequence)):
                    point = wall_sequence[i]
                    moves.append(point)
                    if self.universe[point.x, point.y] == str(original_pipe_id):
                        break
            else:
                # the start is following the end along the wall
                for i in range(1, len(wall_sequence)):
                    point = wall_sequence[-i-1]
                    moves.append(point)
                    if self.universe[point.x, point.y] == str(original_pipe_id):
                        break

            return original_pipe_id, moves

        # No pipe to process following the walls
        return -1, []


if __name__ == "__main__":
    setup_logging()
    size = 4
    pipes = [
       (Point(0, 0), Point(3, 1)),
       (Point(1, 1), Point(3, 0)),
       (Point(0, 3), Point(3, 2)),
    ]

    engine = WallFollowerEngine(size, pipes)
    while not engine.solved:
        for next_move in engine.next_moves():
            logging.debug(next_move)
    logging.info(engine.display())
