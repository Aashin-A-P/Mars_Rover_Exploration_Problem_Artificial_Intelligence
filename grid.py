import random

class MarsGrid:
    def __init__(self, rows, cols, num_craters=5, num_sites=3):
        self.rows, self.cols = rows, cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.craters, self.sites, self.rovers = set(), set(), []
        self.generate_craters(num_craters)
        self.generate_sites(num_sites)

    def generate_craters(self, num_craters):
        while len(self.craters) < num_craters:
            x, y = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.grid[x][y] == 0:
                self.grid[x][y] = 1
                self.craters.add((x, y))

    def generate_sites(self, num_sites):
        while len(self.sites) < num_sites:
            x, y = random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)
            if self.grid[x][y] == 0:
                self.grid[x][y] = 2
                self.sites.add((x, y))

    def add_rover(self, pos):
        if self.grid[pos[0]][pos[1]] == 0:
            self.rovers.append(pos)
            return True
        return False

    def get_grid(self):
        return self.grid
