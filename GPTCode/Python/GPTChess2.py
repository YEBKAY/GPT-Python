import random
import copy

# Define constants for piece types and colors
WHITE, BLACK = 'white', 'black'
PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 'P', 'N', 'B', 'R', 'Q', 'K'

# Mapping from piece symbols to their full names (optional)
piece_names = {
    'P': 'Pawn',
    'N': 'Knight',
    'B': 'Bishop',
    'R': 'Rook',
    'Q': 'Queen',
    'K': 'King'
}

class Piece:
    def __init__(self, type, color):
        self.type = type  # 'P', 'N', 'B', 'R', 'Q', 'K'
        self.color = color  # 'white' or 'black'
        self.has_moved = False  # Useful for castling and pawn's first move

    def __repr__(self):
        return self.type if self.color == WHITE else self.type.lower()

class Board:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_turn = WHITE
        self.move_history = []

    def create_initial_board(self):
        # Initialize an 8x8 board with starting positions
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place pawns
        for i in range(8):
            board[1][i] = Piece(PAWN, BLACK)
            board[6][i] = Piece(PAWN, WHITE)
        
        # Place other pieces
        placement = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]
        for i, piece in enumerate(placement):
            board[0][i] = Piece(piece, BLACK)
            board[7][i] = Piece(piece, WHITE)
        
        return board

    def print_board(self):
        print("  +------------------------+")
        for row in range(8):
            print(8 - row, end=' | ')
            for col in range(8):
                piece = self.board[row][col]
                print(piece if piece else '.', end=' ')
            print('|')
        print("  +------------------------+")
        print("    a b c d e f g h\n")

    def is_in_bounds(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8

    def get_piece_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            return []
        moves = []
        directions = []
        if piece.type == PAWN:
            dir = -1 if piece.color == WHITE else 1
            # Move forward
            if self.is_in_bounds(row + dir, col) and not self.board[row + dir][col]:
                moves.append((row + dir, col))
                # First move can move two squares
                if not piece.has_moved and self.is_in_bounds(row + 2*dir, col) and not self.board[row + 2*dir][col]:
                    moves.append((row + 2*dir, col))
            # Captures
            for dc in [-1, 1]:
                new_row, new_col = row + dir, col + dc
                if self.is_in_bounds(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if target and target.color != piece.color:
                        moves.append((new_row, new_col))
        elif piece.type == KNIGHT:
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                           (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc
                if self.is_in_bounds(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if not target or target.color != piece.color:
                        moves.append((new_row, new_col))
        elif piece.type in [BISHOP, ROOK, QUEEN]:
            if piece.type == BISHOP:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            elif piece.type == ROOK:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            elif piece.type == QUEEN:
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                              (-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                new_row, new_col = row + dr, col + dc
                while self.is_in_bounds(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if not target:
                        moves.append((new_row, new_col))
                    else:
                        if target.color != piece.color:
                            moves.append((new_row, new_col))
                        break
                    new_row += dr
                    new_col += dc
        elif piece.type == KING:
            king_moves = [(-1, -1), (-1, 0), (-1, 1),
                          (0, -1),          (0, 1),
                          (1, -1),  (1, 0), (1, 1)]
            for dr, dc in king_moves:
                new_row, new_col = row + dr, col + dc
                if self.is_in_bounds(new_row, new_col):
                    target = self.board[new_row][new_col]
                    if not target or target.color != piece.color:
                        moves.append((new_row, new_col))
            # Castling (simplified, not checking all conditions)
            if not piece.has_moved:
                # Kingside
                if all(self.board[row][c] is None for c in range(col+1, 7)):
                    rook = self.board[row][7]
                    if rook and rook.type == ROOK and not rook.has_moved:
                        moves.append((row, col + 2))
                # Queenside
                if all(self.board[row][c] is None for c in range(1, col)):
                    rook = self.board[row][0]
                    if rook and rook.type == ROOK and not rook.has_moved:
                        moves.append((row, col - 2))
        return moves

    def get_all_legal_moves(self, color):
        moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in self.get_piece_moves(row, col):
                        moves.append(((row, col), move))
        return moves

    def make_move(self, from_pos, to_pos):
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True
        # Handle castling (move the rook)
        if piece.type == KING and abs(to_col - from_col) == 2:
            if to_col > from_col:  # Kingside
                rook = self.board[from_row][7]
                self.board[from_row][5] = rook
                self.board[from_row][7] = None
                rook.has_moved = True
            else:  # Queenside
                rook = self.board[from_row][0]
                self.board[from_row][3] = rook
                self.board[from_row][0] = None
                rook.has_moved = True
        # Handle pawn promotion (auto promote to Queen)
        if piece.type == PAWN and (to_row == 0 or to_row == 7):
            self.board[to_row][to_col] = Piece(QUEEN, piece.color)
        # Record the move
        self.move_history.append((from_pos, to_pos, piece, target))

    def is_in_check(self, color):
        # Find the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == KING and piece.color == color:
                    king_pos = (row, col)
                    break
        # Check all opponent's moves to see if any can capture the king
        opponent = BLACK if color == WHITE else WHITE
        opponent_moves = self.get_all_legal_moves(opponent)
        for move in opponent_moves:
            _, to_pos = move
            if to_pos == king_pos:
                return True
        return False

    def has_legal_moves(self, color):
        moves = self.get_all_legal_moves(color)
        for move in moves:
            # Make the move on a copy of the board and check for check
            board_copy = copy.deepcopy(self)
            board_copy.make_move(move[0], move[1])
            if not board_copy.is_in_check(color):
                return True
        return False

    def is_checkmate(self, color):
        return self.is_in_check(color) and not self.has_legal_moves(color)

    def is_stalemate(self, color):
        return not self.is_in_check(color) and not self.has_legal_moves(color)

def select_random_move(moves):
    return random.choice(moves) if moves else None

def play_game():
    board = Board()
    board.print_board()
    while True:
        current_color = board.current_turn
        legal_moves = board.get_all_legal_moves(current_color)
        # Filter out moves that would put the king in check
        safe_moves = []
        for move in legal_moves:
            board_copy = copy.deepcopy(board)
            board_copy.make_move(move[0], move[1])
            if not board_copy.is_in_check(current_color):
                safe_moves.append(move)
        if not safe_moves:
            if board.is_in_check(current_color):
                print(f"Checkmate! {BLACK if current_color == WHITE else WHITE} wins.")
            else:
                print("Stalemate! It's a draw.")
            break
        # Select a random move
        move = select_random_move(safe_moves)
        from_pos, to_pos = move
        board.make_move(from_pos, to_pos)
        print(f"{current_color.capitalize()} moves from {pos_to_notation(from_pos)} to {pos_to_notation(to_pos)}")
        board.print_board()
        # Check for checkmate or stalemate
        opponent = BLACK if current_color == WHITE else WHITE
        if board.is_checkmate(opponent):
            print(f"Checkmate! {current_color.capitalize()} wins.")
            break
        if board.is_stalemate(opponent):
            print("Stalemate! It's a draw.")
            break
        # Switch turns
        board.current_turn = opponent

def pos_to_notation(pos):
    row, col = pos
    return f"{chr(ord('a') + col)}{8 - row}"

if __name__ == "__main__":
    play_game()
