import random

class Snake:
    def __init__(self, window_width, window_height, cell_size):
        self.window_width = window_width
        self.window_height = window_height
        self.cell_size = cell_size
        start_x = (window_width // 2) // cell_size * cell_size
        start_y = (window_height // 2) // cell_size * cell_size
        self.body = [(start_x, start_y)]
        self.direction = (1, 0)
        self.size = 5

    def move(self):
        head_x = self.body[0][0] + self.direction[0] * self.cell_size
        head_y = self.body[0][1] + self.direction[1] * self.cell_size
        head = (head_x, head_y)
        self.body.insert(0, head)
        if len(self.body) > self.size:
            self.body.pop()

    def change_direction(self, new_dir):
        if (new_dir[0], new_dir[1]) != (-self.direction[0], -self.direction[1]):
            self.direction = (new_dir[0], new_dir[1])