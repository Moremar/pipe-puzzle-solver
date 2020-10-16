from tkinter import Tk, Label, Frame, Button, Checkbutton, Radiobutton, Entry, Canvas, StringVar, IntVar, ttk
from tkinter.constants import GROOVE, X, Y, LEFT, RIGHT, NW, END
import logging
import re

from utils import setup_logging
from pipe_engine import Move, PipeEngine, GROW, SHRINK, ROLLBACK
from shortest_path_engine import ShortestPathEngine
from point import Point
from samples import Samples


# TK config
CELL_SIZE = 32
DOT_SIZE = CELL_SIZE // 2
PIPE_SIZE = CELL_SIZE // 4
SLEEP_TIME = 1  # time in ms between 2 moves
MAX_PIPES_NUMBER = 16

# colors
WHITE = "white"
GREEN = "lime green"
RED = "red2"
BLUE = "royal blue"
YELLOW = "gold"
PURPLE = "MediumOrchid2"
PINK = "magenta"
BEIGE = "thistle"
BLACK = "black"
LIGHT_BLUE = "sky blue"
GREY = "grey"
DARK_GREEN = "green4",
LIGHT_PINK = "pink"
ORANGE = "dark orange"
TURQUOISE = "turquoise"
BROWN = "brown"
LIGHT_GREEN = "lawn green"
BACKGROUND_BLUE = "lavender"
DARK_PURPLE = "dark violet"

PIPE_COLORS = {
    0: RED,
    1: BLUE,
    2: GREEN,
    3: YELLOW,
    4: PURPLE,
    5: TURQUOISE,
    6: PINK,
    7: ORANGE,
    8: BROWN,
    9: GREY,
    10: BLACK,
    11: DARK_GREEN,
    12: LIGHT_GREEN,
    13: DARK_PURPLE,
    14: LIGHT_BLUE,
    15: BEIGE,
    16: LIGHT_PINK,
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
        i0 = 5 + min(y0, y1) * CELL_SIZE + (CELL_SIZE / 2)
        j0 = 5 + min(x0, x1) * CELL_SIZE + (CELL_SIZE / 2) - (PIPE_SIZE / 2)
        i1 = 5 + max(y0, y1) * CELL_SIZE + (CELL_SIZE / 2)
        j1 = 5 + max(x0, x1) * CELL_SIZE + (CELL_SIZE / 2) + (PIPE_SIZE / 2)
    else:
        i0 = 5 + min(y0, y1) * CELL_SIZE + (CELL_SIZE / 2) - (PIPE_SIZE / 2)
        j0 = 5 + min(x0, x1) * CELL_SIZE + (CELL_SIZE / 2)
        i1 = 5 + max(y0, y1) * CELL_SIZE + (CELL_SIZE / 2) + (PIPE_SIZE / 2)
        j1 = 5 + max(x0, x1) * CELL_SIZE + (CELL_SIZE / 2)
    return canvas.create_rectangle(i0, j0, i1, j1, fill=color, outline="")


# Class used only for the setup of the pipes from the GUI
# All these widgets are deleted once the actual resolution starts
# The GridManager then becomes in charge of drawing the widgets
class PipeSetup:
    def __init__(self, frame, start_entry, end_entry, start_widget, end_widget):
        self.frame = frame
        self.start_entry = start_entry
        self.end_entry = end_entry
        self.start_widget = start_widget
        self.end_widget = end_widget


class Pipe:
    def __init__(self, canvas: Canvas, pipe_id: int, head: Point, tail: Point):
        self.canvas = canvas  # a pipe can draw itself so it needs the container canvas
        self.pipe_id = pipe_id
        self.color = PIPE_COLORS[pipe_id]
        self.head = head
        self.tail = tail
        self.path = [self.head]
        self.head_widget = create_circle_widget(self.canvas, self.head.x, self.head.y, self.color, DOT_SIZE + 10),
        self.tail_widget = create_circle_widget(self.canvas, self.tail.x, self.tail.y, self.color, DOT_SIZE + 10),
        self.path_widgets = []
        self.connector_widgets = []  # line between 2 consecutive pipes cells to show the link

    def grow(self, x: int, y: int):
        curr = self.path[-1]
        if Point(x, y) not in curr.adjacent_points():
            # sanity check, should never happen
            raise Exception("Invalid GROW operation") 
        self.path.append(Point(x, y))
        
        self.connector_widgets.append(create_rectangle_widget(self.canvas, curr.x, curr.y, x, y, self.color))
        self.path_widgets.append(create_circle_widget(self.canvas, x, y, self.color, DOT_SIZE))

    def shrink(self):
        self.path.pop()
        self.canvas.delete(self.path_widgets.pop())
        self.canvas.delete(self.connector_widgets.pop())

    def reset(self):
        """Keep only the start and end nodes"""
        while len(self.path_widgets) > 0:
            self.shrink()

    def destroy(self):
        """Totally remove the widgets of that pipe (used on grid resize/clear)"""
        self.reset()
        self.canvas.delete(self.head_widget)
        self.canvas.delete(self.tail_widget)


class GridManager:
    def __init__(self, canvas: Canvas):
        self.canvas = canvas      # Canvas to draw to
        self.grid_size = 0        # number of cells on each axis of the maze
        self.pipe_ends = []       # start and end cells of each pipe
        self.grid_widgets = []    # graphical widgets of the grid lines
        self.pipes = []           # Pipe objects managing the graphical representation of pipes

    def reset(self):
        for pipe in self.pipes:
            pipe.reset()

    def destroy(self):
        """Delete all widgets of the grid"""
        for pipe in self.pipes:
            pipe.destroy()
        while len(self.grid_widgets) > 0:
            self.canvas.delete(self.grid_widgets.pop(0))
        self.pipe_ends.clear()
        self.pipes.clear()

    def draw_grid(self):
        self.destroy()
        self.grid_widgets.append(self.canvas.create_rectangle(
            5, 5, 5 + self.grid_size * CELL_SIZE, 5 + self.grid_size * CELL_SIZE, fill=BACKGROUND_BLUE, outline=""))
        for i in range(0, self.grid_size + 1):
            self.grid_widgets.append(self.canvas.create_line(5 + CELL_SIZE * i, 5,
                                                             5 + CELL_SIZE * i, 5 + self.grid_size * CELL_SIZE,
                                                             fill=BLACK))
        for j in range(0, self.grid_size + 1):
            self.grid_widgets.append(self.canvas.create_line(5, 5 + CELL_SIZE * j,
                                                             5 + self.grid_size * CELL_SIZE, 5 + CELL_SIZE * j,
                                                             fill=BLACK))

    def add_pipe(self, start_cell, end_cell):
        self.pipe_ends.append((start_cell, end_cell))
        self.pipes.append(Pipe(self.canvas, len(self.pipes), start_cell, end_cell))

    def load_maze(self, grid_size, pipe_ends):
        self.grid_size = grid_size
        self.draw_grid()
        for pipe in pipe_ends:
            self.add_pipe(pipe[0], pipe[1])

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

    def load_solution(self, paths: list):
        """used in non-interactive mode to load a calculated solution in the GUI"""
        for (pipe_id, pipe_path) in enumerate(paths):
            for (point, _moves) in pipe_path[1:]:
                self.pipes[pipe_id].grow(point.x, point.y)


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("Pipe puzzle solver")
        self.ready_for_run = True        # once the validation of manual pipes setup is done
        self.finished = False            # the resolution completed
        self.stopped = False             # the user interrupted the run
        self.running = False             # the resolution is running (used to avoid multiple callbacks)
        self.step_by_step_ready = False  # the grid is prepared for step by step run
        self.steps = 0
        self.moves = []  # get the moves by batch from the engine and process them 1 by 1
        self.pipes = []  # temporary structure to create the pipes from the UI

        # TODO add a way to load some sample for different sizes
        # self.grid_size, self.pipe_ends = Samples.get_puzzle("14")
        self.grid_size = 7
        self.pipe_ends = []

        # Pipe engine
        self.engine = self.new_pipe_engine()

        # TODO remove once tested on Windows
        # a fix for running on OSX - to center the title text vertically
        # if self.tk.call('tk', 'windowingsystem') == 'aqua':  # only for OSX
        #     s = ttk.Style()
        #     # Note: the name is specially for the text in the widgets
        #     # s.configure('TNotebook', padding=0)
        #     # s.configure('TNotebook.Tab', padding=(12, 8, 12, 0))
        #     # s.configure('TFrame', padding=(12, 8, 12, 0))

        # Define custom style for the ttk Notebook (tabs control) since the default is ugly on MacOS
        s = ttk.Style()
        s.theme_create("pipestyle", parent="classic", settings={
            "TNotebook": {
                "configure": {
                    "tabmargins": [2, 5, 2, 0],
                    "background": WHITE
                }
            },
            "TNotebook.Tab": {
                "configure": {
                    "padding": (10, 3),
                    "background": WHITE
                },
                "map": {
                    "background": [("selected", WHITE)],
                    "expand": [("selected", [1, 1, 1, 0])]
                }
            }
        })
        s.theme_use("pipestyle")

        # Frame
        self.frame = Frame(self, padx=5, pady=5, borderwidth=2, relief=GROOVE)
        self.frame.pack(padx=5, pady=5)

        # Canvas Grid
        self.canvas_frame = Frame(self.frame)
        self.canvas_frame.pack(side=LEFT, padx=5, pady=(20, 0))
        self.canvas = Canvas(self.canvas_frame,
                             width=10 + self.grid_size * CELL_SIZE,
                             height=10 + self.grid_size * CELL_SIZE,
                             bd=0, background=WHITE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_clicked)

        self.error_label = Label(self.canvas_frame, text="", fg=RED)
        self.error_label.pack(fill=X, side=LEFT, pady=5)

        # Grid manager to reflect the moves from the engine to the GUI
        self.grid_manager = GridManager(self.canvas)
        self.grid_manager.load_maze(self.grid_size, self.pipe_ends)

        # Config panel
        self.config_panel = Frame(self.frame, padx=5, pady=5)
        self.config_panel.pack(padx=0, side=RIGHT, fill=Y)

        self.tabs_control = ttk.Notebook(self.config_panel, style='TNotebook')
        manual_tab = Frame(self.tabs_control, padx=5, pady=5)
        sample_tab = Frame(self.tabs_control, padx=5, pady=5)

        self.tabs_control.add(manual_tab, text='Manual')
        self.tabs_control.add(sample_tab, text='Samples')
        self.tabs_control.pack(expand=1, fill="both")

        # Manual tab

        sv = StringVar()
        sv.set(self.grid_size)
        sv.trace("w", lambda name, index, mode, sv2=sv: self.on_grid_size_sv_changed(sv2))

        self.grid_size_frame = Frame(manual_tab)
        self.grid_size_frame.pack(fill=X)
        self.grid_size_label = Label(self.grid_size_frame, text="Grid size : ")
        self.grid_size_label.pack(side=LEFT, anchor=NW, pady=(3, 0))
        self.grid_size_entry = Entry(self.grid_size_frame, textvariable=sv, width=5)
        self.grid_size_entry.pack(side=LEFT, anchor=NW, fill=X)
        self.clear_button = Button(self.grid_size_frame, text="Clear", command=self.on_clear_clicked)
        self.clear_button.pack(side=RIGHT, padx=5)

        self.pipe_buttons_frame = Frame(manual_tab)
        self.pipe_buttons_frame.pack(fill=X, pady=5)
        self.add_pipe_button = Button(self.pipe_buttons_frame, text="Add Pipe", width=9, command=self.add_pipe_click)
        self.add_pipe_button.pack(side=LEFT, anchor=NW, padx=5)
        self.delete_pipe_button = Button(self.pipe_buttons_frame, text="Delete Pipe", width=9,
                                         command=self.delete_pipe_click)
        self.delete_pipe_button.pack(side=LEFT, anchor=NW)

        # empty originally, grows when the user adds some pipes from the UI
        self.pipes_list_frame = Frame(manual_tab)
        self.pipes_list_frame.pack(fill=X)

        # Samples tab

        self.samples_frame = Frame(sample_tab)
        self.samples_frame.pack(fill=X)
        self.samples_label = Label(self.samples_frame, text="Load a sample pipe puzzle :")
        self.samples_label.pack(side="top", fill=X, anchor=NW, pady=5)

        self.sample_radio_id = IntVar()
        for i in range(5, 14):
            frame = Frame(self.samples_frame)
            frame.pack(fill=X)
            name = str(i) + "x" + str(i)
            sample_radio = Radiobutton(
            frame, text=name, variable=self.sample_radio_id, value=i, command=self.on_sample_chosen)
            sample_radio.pack(side=LEFT, padx=70)

        # Footer
        self.footer = Frame(self, padx=5)
        self.footer.pack(fill=X)

        # Start / Stop / Reset buttons
        self.bottom_frame = Frame(self.footer, padx=5, pady=5)
        self.bottom_frame.pack()

        self.next_button = Button(self.footer, text="Next", command=self.next_button_click)
        self.next_button.pack(side=LEFT)

        self.run_button = Button(self.footer, text="Run", command=self.run_button_click)
        self.run_button.pack(side=LEFT)

        self.stop_button = Button(self.footer, text="Stop", command=self.stop_button_click)
        self.stop_button.pack(side=LEFT)

        self.reset_button = Button(self.footer, text="Reset", command=self.reset_button_click)
        self.reset_button.pack(side=LEFT)

        # steps count
        self.steps = 0
        self.steps_label1 = Label(self.footer, text="Steps : ")
        self.steps_label2 = Label(self.footer, text="0", width=5)
        self.steps_label2.pack(side="right")
        self.steps_label1.pack(side="right")

        # interactive mode (if true, show the steps in the GUI, else just show the result)
        self.interactive = IntVar()
        self.interactive_checkbox = Checkbutton(self.footer, text='Interactive', variable=self.interactive,
                                                onvalue=1, offvalue=0)
        self.interactive_checkbox.pack(side="right", padx=10)
        self.interactive_checkbox.select()

        # initialize the grid with the default size
        self.on_grid_size_changed()

    def on_sample_chosen(self):
        size = self.sample_radio_id.get()
        logging.info('Loading sample of size ' + str(size))
        self.grid_size, self.pipe_ends = Samples.get_puzzle(str(size))
        self.on_grid_size_changed()
        self.grid_manager.load_maze(self.grid_size, self.pipe_ends)
        self.ready_for_run = True
        self.init_run()

    def on_grid_size_sv_changed(self, sv):
        if re.match(r'^[0-9]+$', sv.get()):
            val = int(sv.get())
            if 3 < val < 16:
                logging.info('Setting grid size to ' + str(val))
                self.grid_size = val
                self.on_grid_size_changed()

    def on_grid_size_changed(self):
        self.canvas['width'] = 10 + self.grid_size * CELL_SIZE
        self.canvas['height'] = 10 + self.grid_size * CELL_SIZE
        self.grid_manager.grid_size = self.grid_size
        self.on_clear_clicked()

    def on_clear_clicked(self):
        self.grid_manager.draw_grid()
        for pipe in self.pipes:
            if pipe.start_widget is not None:
                self.canvas.delete(pipe.start_widget)
            if pipe.end_widget is not None:
                self.canvas.delete(pipe.end_widget)
            pipe.frame.destroy()
        self.pipes.clear()
        # At least 3 pipes must exist so create them and give focus to the first
        for i in range(3):
            self.add_pipe_click(focus=False)
        self.pipes[0].start_entry.focus_set()
        self.error_label["text"] = ""

    def on_canvas_clicked(self, event):
        cell_clicked = ((event.y - 10) // CELL_SIZE, (event.x - 10) // CELL_SIZE)
        too_small = cell_clicked[0] < 0 or cell_clicked[1] < 0
        too_big = cell_clicked[0] > self.grid_size - 1 or cell_clicked[1] > self.grid_size - 1
        if too_small or too_big:
            return
        focused_widget = self.focus_displayof()
        if focused_widget is None or type(focused_widget) != Entry:
            return

        updated_pipe = None
        for pipe in self.pipes:
            if pipe.start_entry == focused_widget or pipe.end_entry == focused_widget:
                updated_pipe = pipe
                break
        if updated_pipe is None:
            return
        updated_pipe_index = self.pipes.index(updated_pipe)
        focused_widget.delete(0, END)
        focused_widget.insert(0, str(cell_clicked))
        new_widget = create_circle_widget(
            self.canvas, cell_clicked[0], cell_clicked[1], PIPE_COLORS[updated_pipe_index], DOT_SIZE + 10)
        if updated_pipe.start_entry == focused_widget:
            if updated_pipe.start_widget is not None:
                # if we modify a pipe start/end that was already set, remove the previous one
                self.canvas.delete(updated_pipe.start_widget)
            updated_pipe.start_widget = new_widget
            # focus the end entry so we do not need to manually click on it
            updated_pipe.end_entry.focus_set()
        else:
            if updated_pipe.end_widget is not None:
                self.canvas.delete(updated_pipe.end_widget)
            updated_pipe.end_widget = new_widget
            # focus the next pipe if any, else create a new pipe
            if updated_pipe_index < len(self.pipes) - 1:
                self.pipes[updated_pipe_index + 1].start_entry.focus_set()
            else:
                self.add_pipe_click()
        self.ready_for_run = False

    def add_pipe_click(self, focus=True):
        if len(self.pipes) == MAX_PIPES_NUMBER:
            return
        color = PIPE_COLORS[len(self.pipes)]
        frame = Frame(self.pipes_list_frame)
        frame.pack(fill=X)
        canvas = Canvas(frame, width=20, height=20, bd=0, background=WHITE)
        canvas.pack(side=LEFT, anchor=NW, pady=1)
        canvas.create_oval(5, 5, 20, 20, fill=color, outline="")
        start_entry = Entry(frame, width=10)
        start_entry.pack(side=LEFT, anchor=NW)
        end_entry = Entry(frame, width=10)
        end_entry.pack(side=LEFT, anchor=NW, padx=3)
        self.pipes.append(PipeSetup(frame, start_entry, end_entry, None, None))
        if focus:
            start_entry.focus_set()
        self.ready_for_run = False

    def delete_pipe_click(self):
        pipe = self.pipes.pop()
        if pipe.start_widget is not None:
            self.canvas.delete(pipe.start_widget)
        if pipe.end_widget is not None:
            self.canvas.delete(pipe.end_widget)
        pipe.frame.destroy()
        self.ready_for_run = False

    def validate_pipes_setup(self) -> str:
        # delete the empty pipes at the end if any
        while len(self.pipes) > 0 and self.pipes[-1].start_widget is None and self.pipes[-1].end_widget is None:
            self.delete_pipe_click()
        if len(self.pipes) < 3:
            return "There must be at least 3 pipes."
        # Check all start/end cells are specified and have no duplicates
        used = []
        for (i, pipe) in enumerate(self.pipes):
            if pipe.start_widget is None:
                return "Pipe " + str(i) + " is missing a start cell."
            elif pipe.end_widget is None:
                return "Pipe " + str(i) + " is missing an end cell."
            elif pipe.start_entry.get() in used:
                return "Cell " + str(pipe.start_entry.get()) + " used by pipe " + str(i) + " is already used."
            elif pipe.end_entry.get() in used:
                return "Cell " + str(pipe.end_entry.get()) + " used by pipe " + str(i) + " is already used."
            used += [pipe.start_entry.get(), pipe.end_entry.get()]

        self.pipe_ends = []
        for pipe in self.pipes:
            match = re.match(r'^\(([0-9]+), ([0-9]+)\)$', pipe.start_entry.get())
            start_x, start_y = int(match.group(1)), int(match.group(2))
            match = re.match(r'^\(([0-9]+), ([0-9]+)\)$', pipe.end_entry.get())
            end_x, end_y = int(match.group(1)), int(match.group(2))
            self.pipe_ends.append((Point(start_x, start_y), Point(end_x, end_y)))
        return ""

    def next_button_click(self):
        if self.finished or self.running or self.stopped:
            return
        if not self.ready_for_run:
            if not self.init_run():
                return
            self.ready_for_run = True

        if not self.engine.solved:
            self.apply_one_move()
        else:
            self.steps_label2.config(text=str(self.steps))
            self.finished = True

    def run_button_click(self):
        if self.running:
            return
        if not self.init_run():
            return
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
                self.grid_manager.load_solution(self.engine.final_paths())
            self.steps_label2.config(text=str(self.steps))
            self.finished = True

    def apply_one_move(self):
        # get the next set of moves if no more moves in buffer
        if len(self.moves) == 0:
            self.moves += self.engine.next_moves()
        if len(self.moves) == 0:
            # The maze has no solution
            self.error_label["text"] += "The maze has no solution."
            self.finished = True
            return

        move = self.moves.pop(0)
        self.steps += 1
        if self.interactive.get() == 1:
            self.grid_manager.apply_move(move)
            if self.steps % 50 == 0:
                # refresh the counter every 50 moves to avoid blinking on refresh
                self.steps_label2.config(text=str(self.steps))

    def init_run(self):
        # ensure the specified pipes setup is valid
        if not self.ready_for_run:
            error = self.validate_pipes_setup()
            if len(error) > 0:
                self.error_label["text"] = error
                return False
            self.error_label["text"] = ""
            self.ready_for_run = True
        # reset pipe engine
        self.engine = self.new_pipe_engine()
        # reset pipes
        self.grid_manager.load_maze(self.grid_size, self.pipe_ends)
        # reset steps counter
        self.steps = 0
        self.steps_label2.config(text=str(self.steps))
        # reset flags
        self.step_by_step_ready = True
        self.stopped = False
        self.finished = False
        self.running = False
        self.moves = []
        return True

    def new_pipe_engine(self) -> PipeEngine:
        # return PathCheckerEngine(self.grid_size, self.pipe_ends)
        # return WallFollowerEngine(self.grid_size, self.pipe_ends)
        # return EmptyCellsCheckerEngine(self.grid_size, self.pipe_ends)
        return ShortestPathEngine(self.grid_size, self.pipe_ends)


setup_logging(logging.INFO)
app = App()
app.mainloop()
