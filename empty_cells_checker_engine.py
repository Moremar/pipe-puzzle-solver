from wall_follower_engine import WallFollowerEngine
from point import Point

# Strategy bringing few improvements to the wall follower strategy :
#  - among the possible directions, pick first the closest one to the goal
#  - discard the moves causing a loop (not optimal path)
#  - if the target is reachable discard other moves
#  - after a move, give up early if some empty cells are surrounded by 3 walls
#    or if a group of empty cells is surrounded with walls


class EmptyCellsCheckerEngine(WallFollowerEngine):
    def __init__(self, grid_size: int, pipe_ends: list):
        super().__init__(grid_size, pipe_ends)

    def choose_next_point(self, points: [Point]) -> Point:
        # pick first the next direction that is closest from the target
        target = self.pipe_ends[self.pipes_mapping[self.curr_pipe]][1]
        distances = [self.shortest_path(p, target, self.pipes_mapping[self.curr_pipe]) for p in points]
        return points.pop(distances.index(min(distances)))

    def filter_next_cells(self, points: [Point]):
        original_pipe_id = self.original_id(self.curr_pipe)
        target = self.pipe_ends[original_pipe_id][1]
        # if the target is reachable, discard the other choices
        for p in points:
            if p == target:
                return [p]

        # if a pipe creates a loop, it is not optimal
        # so only accept points that have a single adjacent with the current pipe (the point they come from)
        # or two if we are adjacent to the target
        res = []
        for p in points:
            pipes_adj = [p_adj for p_adj in p.adjacent_points()
                         if self.universe[p_adj.x, p_adj.y] == str(original_pipe_id)]
            if len(pipes_adj) == 1 or (len(pipes_adj) == 2 and target in pipes_adj):
                res.append(p)
        return res

    def is_doomed(self):
        if super().is_doomed():
            return True

        # if an empty cell is surrounded by 3 walls, it becomes unreachable so give up
        also_walls = [(p.x, p.y) for (p, _dirs) in self.paths[self.curr_pipe][:-1]]
        for (i, j) in self.universe.keys():
            if self.universe[(i, j)] == '.':
                if len([p for p in Point(i, j).adjacent_points() if self.is_wall(p) or (p.x, p.y) in also_walls]) == 3:
                    return True

        # if some empty cells are circled by walls, give up
        valid = []
        for (i, j) in self.universe.keys():
            if self.universe[(i, j)] == '.' and (i, j) not in valid:
                blanks, dots = self.scan_zone(i, j)
                if len(dots) < 2:
                    return True
                valid += blanks
        return False

    def scan_zone(self, i, j):
        blanks = []
        dots = []
        checked = []
        to_check = [(i, j)]
        also_walls = [(p.x, p.y) for (p, _dirs) in self.paths[self.curr_pipe][:-1]]
        while len(to_check) > 0:
            (i, j) = to_check.pop(0)
            p = Point(i, j)
            checked.append((i, j))
            symbol = self.universe[(i, j)]
            if symbol == '.':
                blanks.append((i, j))
                for p2 in p.adjacent_points():
                    not_checked = (p2.x, p2.y) not in checked
                    not_to_check = (p2.x, p2.y) not in to_check
                    if not_checked and not_to_check and not self.is_wall(p2) and not (p2.x, p2.y) in also_walls:
                        to_check.append((p2.x, p2.y))
            else:
                dots.append((i, j))
                continue
        return blanks, dots
