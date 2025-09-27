from grid import MarsGrid
from search import bfs, dfs, ucs, a_star
from csp import backtracking_csp
from adversarial import minimax
from visualize import run_visualization, animate_path

import math

def cost_fn(x, y):
    return 1  # extend with terrain cost later if needed

if __name__ == "__main__":
    # Build Grid
    mars = MarsGrid(6, 6, num_craters=5, num_sites=3)
    mars.add_rover((0, 0))
    mars.add_rover((5, 5))
    grid = mars.get_grid()

    start = mars.rovers[0]
    goal = list(mars.sites)[0]

    print("Start:", start, "Goal:", goal)

    # Run Searches
    path_bfs = bfs(grid, start, goal)
    path_dfs = dfs(grid, start, goal)
    path_ucs = ucs(grid, start, goal, cost_fn)
    path_astar = a_star(grid, start, goal, cost_fn)

    print("BFS Path:", path_bfs)
    print("DFS Path:", path_dfs)
    print("UCS Path:", path_ucs)
    print("A* Path:", path_astar)

    # CSP Assignment
    assignment, cost = backtracking_csp(mars.rovers, list(mars.sites))
    print("CSP Assignment:", assignment, "with cost:", cost)

    # Adversarial Example
    score, move = minimax(grid, mars.sites, (mars.rovers[0], mars.rovers[1]),
                          depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=0)
    print("Adversarial Score (Player1):", score, "Best Move:", move)

    # Visualization (show BFS path for demo)
    if path_bfs:
        animate_path(None, grid, start, path_bfs)  # pygame animation
