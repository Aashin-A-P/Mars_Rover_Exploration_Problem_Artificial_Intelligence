import pygame, sys, random, imageio, numpy as np, hashlib

# ==================== CONFIGURATION ====================
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
FPS = 10
BASE_DEPTH_RED = 5     
BASE_DEPTH_WHITE = 6            
MAX_MOVES = 300       
NO_PROGRESS_LIMIT = 5
JITTER = 0.5
# =======================================================

RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
CROWN_COLOR = (255, 215, 0)

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Checkers AI vs AI (Smart Balanced Minimax)")
clock = pygame.time.Clock()

CROWN = pygame.Surface((45, 25))
pygame.draw.polygon(CROWN, CROWN_COLOR, [(0, 25), (22, 0), (45, 25), (0, 25)])


# ==================== PIECE CLASS ====================
class Piece:
    PADDING = 10
    OUTLINE = 2
    def __init__(self, row, col, color):
        self.row, self.col = row, col
        self.color = color
        self.king = False
        self.calc_pos()
    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2
    def make_king(self): self.king = True
    def move(self, row, col):
        self.row, self.col = row, col
        self.calc_pos()
    def draw(self, win):
        r = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, GREY, (self.x, self.y), r + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), r)
        if self.king:
            win.blit(CROWN, (self.x - 22, self.y - 12))


# ==================== BOARD CLASS ====================
class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(win, RED, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3: self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4: self.board[row].append(Piece(row, col, RED))
                    else: self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = 0, piece
        piece.move(row, col)
        if row == ROWS - 1 and piece.color == WHITE:
            piece.make_king(); self.white_kings += 1
        elif row == 0 and piece.color == RED:
            piece.make_king(); self.red_kings += 1

    def get_piece(self, row, col): return self.board[row][col]

    def remove(self, pieces):
        for p in pieces:
            self.board[p.row][p.col] = 0
            if p != 0:
                if p.color == RED: self.red_left -= 1
                else: self.white_left -= 1

    def winner(self):
        if self.red_left <= 0: return "WHITE"
        elif self.white_left <= 0: return "RED"
        return None

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0: piece.draw(win)

    def evaluate(self):
        # Smarter evaluation: pieces + kings + advancement
        red_score = self.red_left + self.red_kings * 1.5
        white_score = self.white_left + self.white_kings * 1.5
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    progress = (ROWS - row) if piece.color == RED else (row + 1)
                    if piece.color == RED: red_score += progress * 0.02
                    else: white_score += progress * 0.02
        return (white_score - red_score) + random.uniform(-JITTER, JITTER)

    def get_all_pieces(self, color):
        return [p for row in self.board for p in row if p != 0 and p.color == color]

    def get_valid_moves(self, piece):
        moves = {}; left, right, row = piece.col - 1, piece.col + 1, piece.row
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))
        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}; last = []
        for r in range(start, stop, step):
            if left < 0: break
            current = self.board[r][left]
            if current == 0:
                if skipped and not last: break
                elif skipped: moves[(r, left)] = last + skipped
                else: moves[(r, left)] = last
                if last:
                    row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color: break
            else: last = [current]
            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}; last = []
        for r in range(start, stop, step):
            if right >= COLS: break
            current = self.board[r][right]
            if current == 0:
                if skipped and not last: break
                elif skipped: moves[(r, right)] = last + skipped
                else: moves[(r, right)] = last
                if last:
                    row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color: break
            else: last = [current]
            right += 1
        return moves

    def deepcopy(self):
        new_board = Board.__new__(Board)
        new_board.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for r in range(ROWS):
            for c in range(COLS):
                p = self.board[r][c]
                if p != 0:
                    npiece = Piece(p.row, p.col, p.color)
                    npiece.king = p.king
                    new_board.board[r][c] = npiece
        new_board.red_left, new_board.white_left = self.red_left, self.white_left
        new_board.red_kings, new_board.white_kings = self.red_kings, self.white_kings
        return new_board

    def simulate_move(self, piece, move, skip):
        self.move(piece, move[0], move[1])
        if skip: self.remove(skip)
        return self


# ==================== MINIMAX ====================
def minimax(board, depth, alpha, beta, maximizing):
    winner = board.winner()
    if depth == 0 or winner:
        return board.evaluate(), board

    color = WHITE if maximizing else RED
    moves = get_all_moves(board, color)

    # No legal moves = losing position
    if not moves:
        return (-999 if maximizing else 999), board

    best_val = float('-inf') if maximizing else float('inf')
    best_moves = []

    for move in moves:
        val = minimax(move, depth - 1, alpha, beta, not maximizing)[0]
        if maximizing:
            if val > best_val: best_val, best_moves = val, [move]
            elif abs(val - best_val) < 1e-5: best_moves.append(move)
            alpha = max(alpha, val)
        else:
            if val < best_val: best_val, best_moves = val, [move]
            elif abs(val - best_val) < 1e-5: best_moves.append(move)
            beta = min(beta, val)
        if beta <= alpha: break

    return best_val, random.choice(best_moves)


def get_all_moves(board, color):
    moves = []
    for piece in board.get_all_pieces(color):
        valid = board.get_valid_moves(piece)
        for move, skip in valid.items():
            temp = board.deepcopy()
            temp_piece = temp.get_piece(piece.row, piece.col)
            new_board = temp.simulate_move(temp_piece, move, skip)
            moves.append(new_board)
    return moves


# ==================== MAIN LOOP ====================
def main():
    board = Board()
    turn = RED
    frames, seen, no_progress, moves = [], set(), 0, 0
    print("🔥 Starting AI vs AI Checkers...\n")

    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        winner = board.winner()
        if winner:
            print(f"🏆 Winner: {winner}")
            pygame.image.save(WIN, f"final_{winner}.png")
            break

        # If current player has no moves → other wins
        if not get_all_moves(board, turn):
            winner = "WHITE" if turn == RED else "RED"
            print(f"🏆 Winner (no moves left): {winner}")
            pygame.image.save(WIN, f"final_{winner}.png")
            break

        pos_hash = hashlib.md5(str(board.board).encode()).hexdigest()
        if pos_hash in seen: no_progress += 1
        else: no_progress = 0; seen.add(pos_hash)

        depth = BASE_DEPTH_WHITE if turn == WHITE else BASE_DEPTH_RED
        if no_progress > NO_PROGRESS_LIMIT:
            depth = 3
            print("⚠️  Forcing aggressive moves!")
            no_progress = 0

        val, new_board = minimax(board, depth, float('-inf'), float('inf'), turn == WHITE)
        board = new_board
        moves += 1

        board.draw(WIN)
        pygame.display.update()
        frame = pygame.surfarray.array3d(pygame.display.get_surface())
        frame = np.rot90(frame, 3)
        frame = np.fliplr(frame)
        frames.append(frame)
        turn = WHITE if turn == RED else RED

        if moves > MAX_MOVES:
            forced = "WHITE" if board.white_left > board.red_left else "RED"
            print(f"🏁 Max moves reached — Declaring winner: {forced}")
            pygame.image.save(WIN, f"final_{forced}.png")
            break

    pygame.quit()
    imageio.mimsave("checkers_ai.gif", frames, fps=2)
    print("🎞️ Saved game as checkers_ai.gif")


if __name__ == "__main__":
    main()
