import logging
from utils import setup_logging
from pipe_engine import Move, GROW, ROLLBACK
from empty_cells_checker_engine import EmptyCellsCheckerEngine
from samples import Samples

# The biggest issue with the previous algorithms is that they always check new paths starting
# at the end of the currently explored path
# That means that if one of the first moves was incorrect in the path, it will try first all valid
# moves with those incorrect moves before actually changing it
# This new algorithms stores the paths differently so the paths explored follow a BFS algorithm :
# All possible moves found when exploring are stored and assigned a total distance (the distance so far
# + an estimation of the remaining distance)
# We process all paths by increasing order of this distance, making it quicker to test shorter paths


class Possibles:
    """A class to store all the possible moves not explored yet ordered by distance"""
    def __init__(self):
        self._possibles = dict()

    def exist(self, pipe_id: int) -> bool:
        return pipe_id in self._possibles

    def create(self, pipe_id: int):
        # estimation -> possible paths
        self._possibles[pipe_id] = dict()

    def delete(self, pipe_id: int):
        del self._possibles[pipe_id]

    def add(self, pipe_id, depth, estimation, path):
        distance = depth + estimation
        if distance not in self._possibles[pipe_id]:
            self._possibles[pipe_id][distance] = []
        self._possibles[pipe_id][distance].append((depth, path))

    def next(self, pipe_id):
        """Return the next unexplored path with the smallest distance for this pipe"""
        if pipe_id not in self._possibles:
            # only happens when there is no solution to the maze
            return -1, []
        if len(self._possibles[pipe_id].keys()) == 0:
            # no more possible move for this pipe, we will need to revert the previous one
            return -1, []
        distance = min(self._possibles[pipe_id].keys())
        res = self._possibles[pipe_id][distance].pop(0)
        if len(self._possibles[pipe_id][distance]) == 0:
            del self._possibles[pipe_id][distance]

        logging.debug("Next path (DEPTH {0}, DISTANCE {1}) : {2}".format(res[0], distance, res[1]))
        return res


class ShortestPathEngine(EmptyCellsCheckerEngine):
    def __init__(self, grid_size: int, pipe_ends: list):
        super().__init__(grid_size, pipe_ends)
        self.possibles = Possibles()

    def next_moves(self) -> [Move]:
        # if we can complete a pipe by following the wall, start with it
        moves = self.begin_next_moves_hook()
        if len(moves) > 0:
            return moves

        # when we start a new pipe, try to pick one smartly
        if len(self.paths) == self.curr_pipe:
            self.choose_next_pipe()

        original_pipe_id = self.original_id(self.curr_pipe)
        start = self.pipe_ends[original_pipe_id][0]
        target = self.pipe_ends[original_pipe_id][1]

        if len(self.paths) == self.curr_pipe:
            self.paths.append([(start, [])])
            self.possibles.create(self.curr_pipe)
            next_cells = self.possible_dirs(start, original_pipe_id)
            next_cells = self.filter_next_cells(next_cells)

            for next_cell in next_cells:
                estimation = self.shortest_path(next_cell, target, original_pipe_id)
                self.possibles.add(self.curr_pipe, 1, estimation, [start] + [next_cell])

            # The pipe following the walls may have revealed some invalid state, if so roll them back
            if self.is_doomed():
                return self.rollback()

        # If we have no possible path left for this pipe, it means there was an issue earlier, rollback
        depth, path_to_try = self.possibles.next(self.curr_pipe)
        if depth == -1:
            return self.rollback()

        # need to shrink them grow to reach the path to explore
        set_of_moves = []
        keep = 0
        while len(path_to_try) > keep \
                and len(self.paths[self.curr_pipe]) > keep \
                and path_to_try[keep] == self.paths[self.curr_pipe][keep][0]:
            keep += 1
        # the moves to keep are already as expected in self.paths, remove the next ones
        for i in range(0, len(self.paths[self.curr_pipe]) - keep):
            set_of_moves += self.shrink()
        # add the next points to reach the path to explore
        for i in range(keep, len(path_to_try)):
            self.universe[path_to_try[i].x, path_to_try[i].y] = str(original_pipe_id)
            self.paths[self.curr_pipe].append((path_to_try[i], []))
            set_of_moves.append(Move(GROW, original_pipe_id, path_to_try[i]))

        # now the universe is in the expected config
        # if it is already doomed, we do not add any further possibles
        if self.is_doomed():
            return set_of_moves

        # add the next possibles
        if path_to_try[-1] != target:
            next_cells = self.possible_dirs(path_to_try[-1], original_pipe_id)
            next_cells = self.filter_next_cells(next_cells)
            for next_cell in next_cells:
                estimation = self.shortest_path(next_cell, target, original_pipe_id)
                self.possibles.add(self.curr_pipe, depth + 1, estimation, list(path_to_try) + [next_cell])
            return set_of_moves
        else:
            logging.debug("Reached the goal for pipe " + str(original_pipe_id))
            if self.curr_pipe < len(self.pipe_ends) - 1:
                # move to next pipe
                self.curr_pipe += 1
                return set_of_moves
            else:
                logging.info("Pipe puzzle solved")
                self.solved = True
                self.display()
                return set_of_moves

    def rollback(self):
        # On rollback of a pipe explored with this engine, we need to revert this path and all the previous
        # pipes that were generated automatically because they follow a wall
        logging.debug("We are blocked, rollback the last pipe and the previous ones following walls")
        logging.debug(self.display())
        if self.curr_pipe < 0:
            # No solution
            return []
        self.possibles.delete(self.curr_pipe)

        # no more possible moves for this pipe so roll it back entirely
        set_of_moves = self.shrink()
        while set_of_moves[-1].move_type != ROLLBACK:
            set_of_moves += self.shrink()

        # also rollback the previous pipes if they were following the walls
        while not self.possibles.exist(self.curr_pipe):
            moves_to_revert_next_pipe = self.shrink()
            set_of_moves += self.shrink()
            if len(moves_to_revert_next_pipe) == 0:
                # we reverted up to the very first pipe, so there is no solution
                break

        return set_of_moves

    def choose_next_pipe(self):
        # instead of picking the next pipe in the list, try to select one in a smart way.
        # We give a score to all pipes and pick the one with the best score :
        # - higher score for pipes against the wall, ideally in a corner
        # - better score for longer pipes which errors can be spotted quicker
        best_score = 0
        best_pipe = self.curr_pipe
        for i in range(self.curr_pipe, len(self.pipe_ends)):
            score = 0
            start = self.pipe_ends[self.original_id(i)][0]
            target = self.pipe_ends[self.original_id(i)][1]
            start_adj = start.adjacent_points()
            target_adj = target.adjacent_points()

            # increase score if close to walls (even more if 2 walls or more)
            start_walls = len([x for x in start_adj if self.is_wall(x)])
            target_walls = len([x for x in target_adj if self.is_wall(x)])
            wall_nb = max(start_walls, target_walls)
            score += max(wall_nb, 2) * 10

            # increase score if the distance between the start and target is high
            distance = self.shortest_path(start, target, self.original_id(i))
            if distance > self.grid_size/2:
                score += distance * 2
            if score > best_score:
                best_pipe = i
                best_score = score

        logging.debug("Choosing next pipe {0}".format(self.original_id(best_pipe)))

        # flip the next pipe with the one we want to process
        if best_pipe != self.curr_pipe:
            original_best_pipe_id = self.pipes_mapping[best_pipe]
            self.pipes_mapping[best_pipe] = self.pipes_mapping[self.curr_pipe]
            self.pipes_mapping[self.curr_pipe] = original_best_pipe_id


if __name__ == "__main__":
    setup_logging()
    (size, pipes) = Samples.get_puzzle("12")
    engine = ShortestPathEngine(size, pipes)
    while not engine.solved:
        for next_move in engine.next_moves():
            logging.debug(next_move)
    logging.info(engine.display())
