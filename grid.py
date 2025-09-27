import random

class MarsGrid:
    def __init__(self, rows, cols, num_craters=5, num_sites=3):
        self.rows = rows
        self.cols = cols
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]  # 0 = free

        self.craters = set()
        self.sites = set()
        self.rovers = []

        self.generate_craters(num_craters)
        self.generate_sites(num_sites)

    def generate_craters(self, num_craters):
        while len(self.craters) < num_craters:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            if self.grid[x][y] == 0:
                self.grid[x][y] = 1  # crater
                self.craters.add((x, y))

    def generate_sites(self, num_sites):
        while len(self.sites) < num_sites:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.cols - 1)
            if self.grid[x][y] == 0:
                self.grid[x][y] = 2  # site
                self.sites.add((x, y))

    def add_rover(self, pos):
        if self.grid[pos[0]][pos[1]] == 0:
            self.rovers.append(pos)
            return True
        return False

    def get_grid(self):
        return self.grid
