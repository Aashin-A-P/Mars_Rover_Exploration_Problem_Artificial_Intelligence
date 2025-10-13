import pygame
from grid import MarsGrid
from search import bfs, dfs, ucs, a_star
from csp import backtracking_csp
from visualize import animate_path, animate_adversarial, animate_csp

def main():
    mars = MarsGrid()
    mars.add_rover((0,0))   # Rover 1
    mars.add_rover((5,5))   # Rover 2

    grid = mars.get_grid()
    start, goal = mars.rovers[0], list(mars.sites)[0]

    print("Start:", start, "Goal:", goal)
    print("Sites:", mars.sites)
    print("Craters:", mars.craters)

    print("\n=== Mars Rover Exploration Menu ===")
    print("1. BFS\n2. DFS\n3. UCS\n4. A*\n5. CSP\n6. Adversarial\n7. Run ALL")
    choice = input("Choose algorithm: ")

    pygame.init()
    rows, cols = len(grid), len(grid[0])
    screen = pygame.display.set_mode((cols*60, rows*60))
    pygame.display.set_caption("Mars Rover Exploration")

    if choice=="1":
        path=bfs(grid,start,goal); print("BFS Path:",path)
        if path: animate_path(screen,grid,start,path,goal=goal,save_gif=True,gif_name="bfs.gif")

    elif choice=="2":
        path=dfs(grid,start,goal); print("DFS Path:",path)
        if path: animate_path(screen,grid,start,path,goal=goal,save_gif=True,gif_name="dfs.gif")

    elif choice=="3":
        path=ucs(grid,start,goal); print("UCS Path:",path)
        if path: animate_path(screen,grid,start,path,goal=goal,save_gif=True,gif_name="ucs.gif")

    elif choice=="4":
        path=a_star(grid,start,goal); print("A* Path:",path)
        if path: animate_path(screen,grid,start,path,goal=goal,save_gif=True,gif_name="astar.gif")

    elif choice=="5":
        assignment,cost=backtracking_csp(mars.rovers,list(mars.sites))
        print("CSP Assignment:",assignment,"Total Cost:",cost)
        animate_csp(screen,grid,mars.rovers,assignment,bfs,save_gif=True,gif_name="csp.gif")

    elif choice=="6":
        print("Adversarial Simulation (NASA vs ISRO)")
        animate_adversarial(screen,grid,mars.rovers[0],mars.rovers[1],
                            mars.sites.copy(),save_gif=True,gif_name="adversarial.gif")

    elif choice=="7":
        # Run BFS, DFS, UCS, A*
        paths={"bfs":bfs(grid,start,goal),"dfs":dfs(grid,start,goal),
               "ucs":ucs(grid,start,goal),"astar":a_star(grid,start,goal)}
        for name,path in paths.items():
            print(f"{name.upper()} Path:",path)
            if path: animate_path(screen,grid,start,path,goal=goal,save_gif=True,gif_name=f"{name}.gif")

        # Run CSP
        assignment,cost=backtracking_csp(mars.rovers,list(mars.sites))
        print("CSP Assignment:",assignment,"Total Cost:",cost)
        animate_csp(screen,grid,mars.rovers,assignment,bfs,save_gif=True,gif_name="csp.gif")

        # Run Adversarial
        print("Adversarial Simulation (NASA vs ISRO)")
        animate_adversarial(screen,grid,mars.rovers[0],mars.rovers[1],
                            mars.sites.copy(),save_gif=True,gif_name="adversarial.gif")
    else:
        print("Invalid choice.")

if __name__=="__main__":
    main()
