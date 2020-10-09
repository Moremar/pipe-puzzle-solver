from tkinter import Canvas, Label, IntVar, Button, Checkbutton, Tk, Frame, GROOVE, CENTER
import logging

from utils import setup_logging
from pipe_engine import Move, PipeEngine, GROW, SHRINK, ROLLBACK
from empty_cells_checker_engine import EmptyCellsCheckerEngine
from point import Point
from samples import Samples


# TODO handle when no solution
# TODO ability to set the start/end of the pipes manually in the canvas
# TODO ability to change the grid size

# TK config
CELL_SIZE = 32
DOT_SIZE = CELL_SIZE // 2
PIPE_SIZE = CELL_SIZE // 4
SLEEP_TIME = 1  # time in ms between 2 moves

# colors
WHITE = "ghost white"
LIME_GREEN = "lime green"
RED = "red2"
BLUE = "royal blue"
YELLOW = "yellow"
PURPLE = "purple"
PINK = "hot pink"
BEIGE = "thistle"
BLACK = "black"
LIGHT_BLUE = "sky blue"
GREEN = "green",
LIGHT_PINK = "pink"
ORANGE = "dark orange"
GOLD = "goldenrod"
TURQUOISE = "turquoise"
BROWN = "brown"
MAGENTA = "magenta"

PIPE_COLORS = {
    0: LIME_GREEN,
    1: RED,
    2: BLUE,
    3: YELLOW,
    4: PURPLE,
    5: PINK,
    6: BEIGE,
    7: BLACK,
    8: LIGHT_BLUE,
    9: GREEN,
    10: LIGHT_PINK,
    11: ORANGE,
    12: GOLD,
    13: TURQUOISE,
    14: BROWN,
    15: MAGENTA
}


def create_circle_widget(canvas: Canvas, x: int, y: int, color: str, circle_size: int):
    """create a centered circle on cell (x, y)"""
    # in the canvas the 1st axis is horizontal and the 2nd is vertical
    # we want the opposite so we flip x and y for the canvas
    # to create an ellipsis, we give (x0, y0) and (x1, y1) that define the containing rectangle
    pad = (CELL_SIZE - circle_size) / 2
    i0 = 5 + y * CELL_SIZE + pad + 1
    j0 = 5 + x * CELL_SIZE + pad + 1
    i1 = 5 + (y + 1) * CELL_SIZE - pad
    j1 = 5 + (x + 1) * CELL_SIZE - pad
    return canvas.create_oval(i0, j0, i1, j1, fill=color, outline="")


def create_rectangle_widget(canvas: Canvas, x0: int, y0: int, x1: int, y1: int, color: str):
    """create a rectangle to link 2 dots of a pipe"""
    # in the canvas the 1st axis is horizontal and the 2nd is vertical
    # we want the opposite so we flip x and y for the canvas
    horizontal = (x0 == x1)
    if horizontal:
        i0 = 5 + min(y0, y1) * CELL_SIZE + (CELL_SIZE/2)
        j0 = 5 + min(x0, x1) * CELL_SIZE + (CELL_SIZE/2) - (PIPE_SIZE/2)
        i1 = 5 + max(y0, y1) * CELL_SIZE + (CELL_SIZE/2)
        j1 = 5 + max(x0, x1) * CELL_SIZE + (CELL_SIZE/2) + (PIPE_SIZE/2)
    else:
        i0 = 5 + min(y0, y1) * CELL_SIZE + (CELL_SIZE/2) - (PIPE_SIZE/2)
        j0 = 5 + min(x0, x1) * CELL_SIZE + (CELL_SIZE/2)
        i1 = 5 + max(y0, y1) * CELL_SIZE + (CELL_SIZE/2) + (PIPE_SIZE/2)
        j1 = 5 + max(x0, x1) * CELL_SIZE + (CELL_SIZE/2)
    return canvas.create_rectangle(i0, j0, i1, j1, fill=color, outline="")


class Pipe:
    def __init__(self, canvas: Canvas, pipe_id: int, head: Point, tail: Point):
        self.canvas = canvas   # a pipe can draw itself so it needs the container canvas
        self.pipe_id = pipe_id
        self.color = PIPE_COLORS[pipe_id]
        self.head = head
        self.tail = tail
        self.path = [self.head]
        self.head_widgets = create_circle_widget(self.canvas, self.head.x, self.head.y, self.color, DOT_SIZE + 10),
        self.tail_widget = create_circle_widget(self.canvas, self.tail.x, self.tail.y, self.color,  DOT_SIZE + 10),
        self.path_widgets = []
        self.connector_widgets = []  # line between 2 consecutive pipes cells to show the link

    def grow(self, x: int, y: int):
        curr = self.path[-1]
        self.path.append(Point(x, y))
        self.connector_widgets.append(create_rectangle_widget(self.canvas, curr.x, curr.y, x, y, self.color))
        self.path_widgets.append(create_circle_widget(self.canvas, x, y, self.color, DOT_SIZE))

    def shrink(self):
        self.path.pop()
        self.canvas.delete(self.path_widgets.pop())
        self.canvas.delete(self.connector_widgets.pop())

    def reset(self):
        while len(self.path_widgets) > 0:
            self.shrink()


class GridManager:
    def __init__(self, canvas: Canvas, grid_size: int, pipe_ends: list):
        self.canvas = canvas
        self.grid_size = grid_size
        self.pipe_ends = pipe_ends

        # graphical representation of the output
        self.pipes = []

        # create the grid
        for i in range(0, self.grid_size + 1):
            self.canvas.create_line(5 + CELL_SIZE * i, 5,
                                    5 + CELL_SIZE * i, 5 + self.grid_size * CELL_SIZE,
                                    fill=BLACK)
        for j in range(0, self.grid_size + 1):
            self.canvas.create_line(5, 5 + CELL_SIZE * j,
                                    5 + self.grid_size * CELL_SIZE, 5 + CELL_SIZE * j,
                                    fill=BLACK)

        # Pipes
        for (i, pipe) in enumerate(self.pipe_ends):
            self.pipes.append(Pipe(self.canvas, i, pipe[0], pipe[1]))

    def reset(self):
        for pipe in self.pipes:
            pipe.reset()

    def apply_move(self, move: Move):
        """reflect a single move to the pipes in the GUI"""
        if move.move_type == GROW:
            self.pipes[move.pipe_id].grow(move.point.x, move.point.y)
        elif move.move_type == SHRINK:
            self.pipes[move.pipe_id].shrink()
        elif move.move_type == ROLLBACK:
            # do not touch the current pipe (it already has no path left)
            # but disconnect the previous pipe from the goal
            self.pipes[move.prev_pipe_id].shrink()
        else:
            raise Exception("Invalid move type " + move.move_type)

    def load(self, paths: list):
        """used in non-interactive mode to load a calculated solution in the GUI"""
        for (pipe_id, pipe_path) in enumerate(paths):
            for (point, _moves) in pipe_path[1:]:
                self.pipes[pipe_id].grow(point.x, point.y)


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.finished = False   # the resolution completed
        self.stopped = False    # the user interrupted the run
        self.running = False    # the resolution is running (used to avoid multiple callbacks)
        self.step_by_step_ready = False  # the grid is prepared for step by step run
        self.steps = 0
        self.moves = []  # get the moves by batch from the engine and process them 1 by 1

        self.grid_size, self.pipe_ends = Samples.get_puzzle("12")

        # Pipe engine
        self.engine = self.new_pipe_engine()

        # Title
        self.title_label = Label(self, text="PIPE PUZZLE SOLVER", justify=CENTER)
        self.title_label.pack()

        # Frame
        self.frame = Frame(self, padx=5, pady=5, borderwidth=2, relief=GROOVE)
        self.frame.pack()

        # Canvas Grid
        self.canvas = Canvas(self.frame,
                             width=10 + self.grid_size * CELL_SIZE,
                             height=10 + self.grid_size * CELL_SIZE,
                             bd=0, background=WHITE)
        self.canvas.pack()

        # Grid manager to reflect the moves from the engine to the GUI
        self.grid_manager = GridManager(self.canvas, self.grid_size, self.pipe_ends)

        # Start / Stop / Reset buttons
        self.bottom_frame = Frame(self, padx=5, pady=5)
        self.bottom_frame.pack()

        self.next_button = Button(self, text="Next", command=self.next_button_click)
        self.next_button.pack(side="left")

        self.run_button = Button(self, text="Run", command=self.run_button_click)
        self.run_button.pack(side="left")

        self.stop_button = Button(self, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side="left")

        self.reset_button = Button(self, text="Reset", command=self.reset_button_click)
        self.reset_button.pack(side="left")

        # steps count
        self.steps = 0
        self.steps_label1 = Label(self, text="Steps : ")
        self.steps_label2 = Label(self, text="0", width=5)
        self.steps_label2.pack(side="right")
        self.steps_label1.pack(side="right")

        # interactive mode (if true, show the steps in the GUI, else just show the result)
        self.interactive = IntVar()
        self.interactive_checkbox = Checkbutton(self, text='Interactive', variable=self.interactive,
                                                onvalue=1, offvalue=0)
        self.interactive_checkbox.pack(side="right", padx=10)
        self.interactive_checkbox.select()

    def next_button_click(self):
        if self.finished or self.running or self.stopped:
            return
        if not self.engine.solved:
            self.apply_one_move()
        else:
            self.steps_label2.config(text=str(self.steps))
            self.finished = True

    def run_button_click(self):
        if self.finished or self.running:
            return
        self.init_run()
        self.running = True
        self.start_run_loop()
        self.running = False

    def stop_button_click(self):
        self.stopped = True

    def reset_button_click(self):
        self.init_run()

    def start_run_loop(self):
        if self.finished or self.stopped:
            return
        if not self.engine.solved:
            self.apply_one_move()
            self.after(SLEEP_TIME, self.start_run_loop)
        else:
            if self.interactive.get() == 0:
                self.grid_manager.load(self.engine.final_paths())
            self.steps_label2.config(text=str(self.steps))
            self.finished = True

    def apply_one_move(self):
        # get the next set of moves if no more moves in buffer
        if len(self.moves) == 0:
            self.moves += self.engine.next_moves()

        move = self.moves.pop(0)
        self.steps += 1
        if self.interactive.get() == 1:
            self.grid_manager.apply_move(move)
            if self.steps % 50 == 0:
                # refresh the counter every 50 moves to avoid blinking on refresh
                self.steps_label2.config(text=str(self.steps))

    def init_run(self):
        # reset pipe engine
        self.engine = self.new_pipe_engine()
        # reset pipes (engine reset is done on Start)
        self.grid_manager.reset()
        # reset steps counter
        self.steps = 0
        self.steps_label2.config(text=str(self.steps))
        # reset flags
        self.step_by_step_ready = True
        self.stopped = False
        self.finished = False
        self.running = False

    def new_pipe_engine(self) -> PipeEngine:
        # return PathCheckerEngine(self.grid_size, self.pipe_ends)
        # return WallFollowerEngine(self.grid_size, self.pipe_ends)
        return EmptyCellsCheckerEngine(self.grid_size, self.pipe_ends)


setup_logging(logging.INFO)
app = App()
app.mainloop()
