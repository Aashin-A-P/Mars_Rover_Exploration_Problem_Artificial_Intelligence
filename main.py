import pygame, math
from grid import MarsGrid
from search import bfs, dfs, ucs, a_star
from csp import backtracking_csp
from adversarial_search import minimax
from visualize import animate_path

def main():
    # ✅ Generate ONE grid and reuse it
    mars = MarsGrid(6, 6, num_craters=5, num_sites=3)
    mars.add_rover((0, 0))
    mars.add_rover((5, 5))
    grid = mars.get_grid()
    start, goal = mars.rovers[0], list(mars.sites)[0]

    print("Start:", start, "Goal:", goal)
    print("Sites:", mars.sites)
    print("Craters:", mars.craters)

    print("\n=== Mars Rover Exploration Menu ===")
    print("1. BFS")
    print("2. DFS")
    print("3. UCS")
    print("4. A*")
    print("5. CSP (multi-rover assignment)")
    print("6. Adversarial Search (NASA vs ISRO)")
    print("7. Run ALL searches (BFS, DFS, UCS, A*) and save GIFs for comparison")
    choice = input("Choose algorithm: ")

    pygame.init()
    rows, cols = len(grid), len(grid[0])
    screen = pygame.display.set_mode((cols * 60, rows * 60))
    pygame.display.set_caption("Mars Rover Exploration")

    if choice == "1":
        path = bfs(grid, start, goal)
        print("BFS Path:", path)
        if path:
            animate_path(screen, grid, start, path, save_gif=True, gif_name="bfs.gif")

    elif choice == "2":
        path = dfs(grid, start, goal)
        print("DFS Path:", path)
        if path:
            animate_path(screen, grid, start, path, save_gif=True, gif_name="dfs.gif")

    elif choice == "3":
        path = ucs(grid, start, goal)
        print("UCS Path:", path)
        if path:
            animate_path(screen, grid, start, path, save_gif=True, gif_name="ucs.gif")

    elif choice == "4":
        path = a_star(grid, start, goal)
        print("A* Path:", path)
        if path:
            animate_path(screen, grid, start, path, save_gif=True, gif_name="astar.gif")

    elif choice == "5":
        assignment, cost = backtracking_csp(mars.rovers, list(mars.sites))
        print("CSP Assignment:", assignment, "Total Cost:", cost)

    elif choice == "6":
        score, move = minimax(grid, mars.sites, (mars.rovers[0], mars.rovers[1]),
                              depth=3, alpha=-math.inf, beta=math.inf, maximizing_player=0)
        print("Adversarial Score (Player1):", score, "Best Move:", move)

    elif choice == "7":  # ✅ Run all searches on SAME grid
        paths = {
            "bfs": bfs(grid, start, goal),
            "dfs": dfs(grid, start, goal),
            "ucs": ucs(grid, start, goal),
            "astar": a_star(grid, start, goal)
        }
        for name, path in paths.items():
            print(f"{name.upper()} Path:", path)
            if path:
                animate_path(screen, grid, start, path, save_gif=True, gif_name=f"{name}.gif")

    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
