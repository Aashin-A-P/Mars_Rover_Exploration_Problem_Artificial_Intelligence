import math

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

def is_valid(grid, x, y):
    rows, cols = len(grid), len(grid[0])
    return 0 <= x < rows and 0 <= y < cols and grid[x][y] != 1  # 1 = crater


# =============================
# Evaluation Function
# =============================
def evaluate(state, sites, player_positions):
    """
    Score = sites collected by current player - opponent's sites
    """
    scores = [0, 0]  # [Player1, Player2]
    for site in sites:
        if player_positions[0] == site:
            scores[0] += 1
        elif player_positions[1] == site:
            scores[1] += 1
    return scores[0] - scores[1]


# =============================
# Generate Legal Moves
# =============================
def get_moves(grid, pos):
    moves = []
    for dx, dy in MOVES:
        nx, ny = pos[0] + dx, pos[1] + dy
        if is_valid(grid, nx, ny):
            moves.append((nx, ny))
    return moves


# =============================
# Minimax with Alpha-Beta Pruning
# =============================
def minimax(grid, sites, positions, depth, alpha, beta, maximizing_player):
    """
    grid       : 2D list (0 = empty, 1 = crater, 2 = site)
    sites      : set of site positions
    positions  : [(x1,y1), (x2,y2)] positions of the two rovers
    depth      : search depth
    alpha/beta : pruning bounds
    maximizing_player : 0 for Player1, 1 for Player2
    """
    if depth == 0 or not sites:
        return evaluate(grid, sites, positions), None

    best_move = None

    if maximizing_player == 0:  # Player 1's turn
        max_eval = -math.inf
        for move in get_moves(grid, positions[0]):
            new_positions = (move, positions[1])
            new_sites = sites.copy()
            if move in new_sites:
                new_sites.remove(move)
            eval_score, _ = minimax(grid, new_sites, new_positions, depth - 1, alpha, beta, 1)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move

    else:  # Player 2's turn
        min_eval = math.inf
        for move in get_moves(grid, positions[1]):
            new_positions = (positions[0], move)
            new_sites = sites.copy()
            if move in new_sites:
                new_sites.remove(move)
            eval_score, _ = minimax(grid, new_sites, new_positions, depth - 1, alpha, beta, 0)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move
