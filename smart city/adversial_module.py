from typing import List, Tuple, Optional
from utils import in_bounds, neighbors4, cell_cost, manhattan, Grid, Pos

GamePos = Tuple[Pos, Pos, bool]

def legal_moves(grid: Grid, p: Pos):
    moves = [v for v in neighbors4(p) if in_bounds(grid,v) and cell_cost(grid[v[0]][v[1]])<float('inf')]
    return moves or [p]

def terminal(bot, drone, goal, max_steps, steps):
    if bot == drone: return -1000
    if bot == goal: return 1000
    if steps >= max_steps: return 200 - manhattan(bot, goal) + (manhattan(bot, drone)//2)
    return None

def heuristic(bot, drone, goal):
    return 100 - manhattan(bot, goal) + (manhattan(bot, drone)//2)

def alphabeta(grid, state, goal, depth, alpha, beta, steps, max_steps):
    bot, drone, bot_turn = state
    term = terminal(bot, drone, goal, max_steps, steps)
    if term is not None: return term, None
    if depth == 0: return heuristic(bot, drone, goal), None

    if bot_turn:
        best, move = -1e9, None
        for m in legal_moves(grid, bot):
            val, _ = alphabeta(grid, (m, drone, False), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val > best: best, move = val, m
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best, move
    else:
        worst, move = 1e9, None
        for m in legal_moves(grid, drone):
            val, _ = alphabeta(grid, (bot, m, True), goal, depth-1, alpha, beta, steps+1, max_steps)
            if val < worst: worst, move = val, m
            beta = min(beta, worst)
            if beta <= alpha: break
        return worst, move

def simulate_pursuit(grid, start, goal, drone_start, depth=4, max_steps=24):
    bot = start
    drone = drone_start
    steps = 0
    frames = [(bot, drone)]  # ✅ both defined before used

    while steps < max_steps:
        # Robot’s move
        _, move = alphabeta(grid, (bot, drone, True), goal, depth, -1e9, 1e9, steps, max_steps)
        bot = move or bot
        steps += 1
        frames.append((bot, drone))
        if bot == goal or bot == drone:
            break

        # Drone’s move
        _, gmove = alphabeta(grid, (bot, drone, False), goal, depth, -1e9, 1e9, steps, max_steps)
        drone = gmove or drone
        steps += 1
        frames.append((bot, drone))
        if bot == goal or bot == drone:
            break

    return frames

