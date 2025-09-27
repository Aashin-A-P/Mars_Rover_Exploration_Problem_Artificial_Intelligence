class MarsGrid:
    def __init__(self):
        # 0 = empty, 1 = crater, 2 = site
        self.grid = [
            [0,0,0,0,2,0],
            [0,1,1,0,0,0],
            [0,0,0,0,1,0],
            [0,2,1,0,0,0],
            [0,0,0,0,0,1],
            [0,0,0,2,0,0]
        ]
        self.rows, self.cols = len(self.grid), len(self.grid[0])

        # fixed sets
        self.craters={(1,1),(1,2),(2,4),(3,2),(4,5)}
        self.sites={(0,4),(3,1),(5,3)}
        self.rovers=[]

    def add_rover(self,pos):
        if self.grid[pos[0]][pos[1]]==0:
            self.rovers.append(pos)
            return True
        return False

    def get_grid(self):
        return self.grid
