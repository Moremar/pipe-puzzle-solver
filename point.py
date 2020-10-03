class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def adjacent_points(self):
        return [Point(self.x, self.y + 1), Point(self.x, self.y - 1),
                Point(self.x + 1, self.y), Point(self.x - 1, self.y)]