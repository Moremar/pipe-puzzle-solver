# directions
LEFT, UP, RIGHT, DOWN = ("left", "up", "right", "down")


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __hash__(self):
        # hash the Point object as the tuple (x, y)
        return (self.x, self.y).__hash__()

    def adjacent_points(self):
        """All 4 adjacent points"""
        return [self.adj(UP), self.adj(RIGHT), self.adj(DOWN), self.adj(LEFT)]

    def adj(self, direction: str):
        """Adjacent point in the given direction"""
        if direction == LEFT:
            return Point(self.x, self.y - 1)
        elif direction == UP:
            return Point(self.x - 1, self.y)
        elif direction == RIGHT:
            return Point(self.x, self.y + 1)
        elif direction == DOWN:
            return Point(self.x + 1, self.y)
        else:
            raise Exception("Invalid direction: " + direction)

    @staticmethod
    def next_dir(direction: str):
        return UP if direction == LEFT else RIGHT if direction == UP else DOWN if direction == RIGHT else LEFT

    @staticmethod
    def prev_dir(direction: str):
        return UP if direction == RIGHT else LEFT if direction == UP else DOWN if direction == LEFT else RIGHT
