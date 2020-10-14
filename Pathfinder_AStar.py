import pygame
import math
from queue import PriorityQueue


class Grid:
    def __init__(self, width, rows, win):
        self.rows = rows
        self.width = width
        self.win = win
        self.grid = [[Spot(width // self.rows, i, j) for j in range(self.rows)]
                     for i in range(self.rows)]
        self.start = None
        self.end = None
        self.gap = self.width // self.rows

    def draw(self):
        self.win.fill((255, 255, 255))

        for row in self.grid:
            for spot in row:
                spot.draw(self.win)

        for i in range(self.rows+1):
            pygame.draw.line(self.win, (0, 0, 0), (0, i*self.gap),
                             (self.width, i*self.gap), 1)
            pygame.draw.line(self.win, (0, 0, 0), (i*self.gap, 0),
                             (i * self.gap, self.width), 1)

        pygame.display.update()

    def handle_click(self, position):
        x = position[0] // self.gap
        y = position[1] // self.gap

        spot = self.grid[x][y]

        if not self.start:
            self.start = spot
            self.start.make_start()
        elif not self.end and spot != self.start:
            self.end = spot
            self.end.make_end()
        elif spot != self.start and spot != self.end:
            self.grid[x][y].make_barrier()

    def handle_right_click(self, position):
        x = position[0] // self.gap
        y = position[1] // self.gap

        spot = self.grid[x][y]

        spot.reset()

        if spot == self.start:
            self.start = None

        if spot == self.end:
            self.end = None

    def solve(self):
        count = 0
        open_set = PriorityQueue()
        open_set.put((0, count, self.start))
        came_from = {}
        g_score = {spot: float("inf") for row in self.grid for spot in row}
        g_score[self.start] = 0
        f_score = {spot: float("inf") for row in self.grid for spot in row}
        f_score[self.start] = self.start.manhattan_distance(
            self.end.get_position())

        open_set_hash = {self.start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            open_set_hash.remove(current)

            if current == self.end:
                reconstruct_path(came_from, self.end)
                self.end.make_end()
                return True

            for neighbor in current.neighbors:
                temp_g_score = g_score[current] + 1

                if temp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g_score
                    f_score[neighbor] = temp_g_score + \
                        neighbor.manhattan_distance(self.end.get_position())
                    if neighbor not in open_set_hash:
                        count += 1
                        open_set.put((f_score[neighbor], count, neighbor))
                        open_set_hash.add(neighbor)
                        neighbor.make_open()

            self.draw()

            if current != self.start:
                current.make_closed()

        return False


class Spot:
    def __init__(self, width, row, col):
        self.value = 'EMPTY'
        self.width = width
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = (255, 255, 255)
        self.neighbors = []

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def is_closed(self):
        return self.color == (255, 0, 0)

    def make_start(self):
        self.color = (0, 0, 255)

    def make_end(self):
        self.color = (255, 255, 0)

    def make_barrier(self):
        self.color = (0, 0, 0)

    def make_open(self):
        self.color = (0, 255, 0)

    def make_closed(self):
        self.color = (255, 0, 0)

    def reset(self):
        self.color = (255, 255, 255)

    def make_path(self):
        self.color = (128, 0, 128)

    def manhattan_distance(self, end):
        return abs(self.row - end[0]) + abs(self.col - end[1])

    def get_position(self):
        return self.row, self.col

    def update_neighbours(self, grid, total_rows):
        self.neighbors = []
        # DOWN
        if self.row < total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def is_barrier(self):
        return self.color == (0, 0, 0)


def reconstruct_path(came_from, current):
    while current in came_from:
        current = came_from[current]
        current.make_path()


def main():
    rows = 50
    width = 900

    win = pygame.display.set_mode((width, width))
    pygame.display.set_caption('Pathfinder')
    grid = Grid(width, rows, win)
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                position = pygame.mouse.get_pos()
                grid.handle_click(position)

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                position = pygame.mouse.get_pos()
                grid.handle_right_click(position)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and grid.start and grid.end:
                    for row in grid.grid:
                        for spot in row:
                            spot.update_neighbours(grid.grid, rows)

                    grid.solve()

                if event.key == pygame.K_c:
                    grid = Grid(width, rows, win)

        grid.draw()


main()
pygame.quit()
