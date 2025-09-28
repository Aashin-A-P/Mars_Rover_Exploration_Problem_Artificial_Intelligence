class MarsGrid:
    def __init__(self):
        # 0 = empty, 1 = crater, 2 = site
        self.grid = [
            [0,0,0,0,2,0],
            [0,1,0,1,0,0],
            [0,0,2,0,1,0],
            [0,1,0,0,0,0],
            [0,0,0,1,0,2],
            [2,0,0,0,0,0]
        ]
        self.rows, self.cols = len(self.grid), len(self.grid[0])

        self.craters = {(1,1),(1,3),(2,4),(3,1),(4,3)}
        self.sites   = {(0,4),(2,2),(4,5),(5,0)}

        self.rovers = []

    def add_rover(self,pos):
        if self.grid[pos[0]][pos[1]] == 0:
            self.rovers.append(pos)
            return True
        return False

    def get_grid(self):
        return self.grid
