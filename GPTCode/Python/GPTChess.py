import pygame
import sys
import random
import copy
import time

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE_SQUARE = (240, 217, 181)
BLACK_SQUARE = (181, 136, 99)
HIGHLIGHT_FROM = (0, 255, 0, 100)  # Semi-transparent green
HIGHLIGHT_TO = (255, 0, 0, 100)    # Semi-transparent red
WHITE_PIECE_COLOR = (255, 255, 255)
BLACK_PIECE_COLOR = (0, 0, 0)
INFO_BG_COLOR = (50, 50, 50)
INFO_TEXT_COLOR = (255, 255, 255)

# Set up the display
WIN = pygame.display.set_mode((WIDTH, HEIGHT + 100))
pygame.display.set_caption("Chess AI vs. Chess AI")

# Chess Logic Constants
WHITE_PIECES = ['K', 'Q', 'R', 'B', 'N', 'P']
BLACK_PIECES = ['k', 'q', 'r', 'b', 'n', 'p']
EMPTY = ' '

# Fonts
INFO_FONT = pygame.font.SysFont('Arial', 24)

# Define piece sizes relative to square size
PIECE_RADIUS = SQUARE_SIZE // 4
PIECE_WIDTH = SQUARE_SIZE // 2
PIECE_HEIGHT = SQUARE_SIZE // 2

def initialize_board():
    board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p'] * 8,
        [EMPTY] * 8,
        [EMPTY] * 8,
        [EMPTY] * 8,
        [EMPTY] * 8,
        ['P'] * 8,
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]
    return board

def is_in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def get_all_possible_moves(board, color):
    moves = []
    for i in range(8):
        for j in range(8):
            piece = board[i][j]
            if piece == EMPTY:
                continue
            if color == 'white' and piece in WHITE_PIECES:
                piece_moves = get_piece_moves(board, i, j, piece, color)
                for move in piece_moves:
                    moves.append(((i, j), move))
            elif color == 'black' and piece in BLACK_PIECES:
                piece_moves = get_piece_moves(board, i, j, piece, color)
                for move in piece_moves:
                    moves.append(((i, j), move))
    return moves

def get_piece_moves(board, x, y, piece, color):
    directions = []
    moves = []
    if piece.upper() == 'P':
        if color == 'white':
            # Move forward
            if is_in_bounds(x-1, y) and board[x-1][y] == EMPTY:
                moves.append((x-1, y))
            # Capture diagonally
            if y > 0 and is_in_bounds(x-1, y-1) and board[x-1][y-1] in BLACK_PIECES:
                moves.append((x-1, y-1))
            if y < 7 and is_in_bounds(x-1, y+1) and board[x-1][y+1] in BLACK_PIECES:
                moves.append((x-1, y+1))
        else:
            if is_in_bounds(x+1, y) and board[x+1][y] == EMPTY:
                moves.append((x+1, y))
            if y > 0 and is_in_bounds(x+1, y-1) and board[x+1][y-1] in WHITE_PIECES:
                moves.append((x+1, y-1))
            if y < 7 and is_in_bounds(x+1, y+1) and board[x+1][y+1] in WHITE_PIECES:
                moves.append((x+1, y+1))
    elif piece.upper() == 'N':
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if is_in_bounds(nx, ny):
                target = board[nx][ny]
                if target == EMPTY or (color == 'white' and target in BLACK_PIECES) or (color == 'black' and target in WHITE_PIECES):
                    moves.append((nx, ny))
    elif piece.upper() == 'B':
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    elif piece.upper() == 'R':
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    elif piece.upper() == 'Q':
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                      (-1, 0), (1, 0), (0, -1), (0, 1)]
    elif piece.upper() == 'K':
        king_moves = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        for dx, dy in king_moves:
            nx, ny = x + dx, y + dy
            if is_in_bounds(nx, ny):
                target = board[nx][ny]
                if target == EMPTY or (color == 'white' and target in BLACK_PIECES) or (color == 'black' and target in WHITE_PIECES):
                    moves.append((nx, ny))
    if directions:
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while is_in_bounds(nx, ny):
                target = board[nx][ny]
                if target == EMPTY:
                    moves.append((nx, ny))
                else:
                    if (color == 'white' and target in BLACK_PIECES) or (color == 'black' and target in WHITE_PIECES):
                        moves.append((nx, ny))
                    break
                nx += dx
                ny += dy
    return moves

def make_move(board, move):
    (x1, y1), (x2, y2) = move
    piece = board[x1][y1]
    board[x2][y2] = piece
    board[x1][y1] = EMPTY

def find_king(board, color):
    king = 'K' if color == 'white' else 'k'
    for i in range(8):
        for j in range(8):
            if board[i][j] == king:
                return (i, j)
    return None

def is_in_check(board, color):
    king_pos = find_king(board, color)
    if not king_pos:
        return True  # King is missing, considered in check
    opponent = 'black' if color == 'white' else 'white'
    opponent_moves = get_all_possible_moves(board, opponent)
    for move in opponent_moves:
        _, (x, y) = move
        if (x, y) == king_pos:
            return True
    return False

def has_any_moves(board, color):
    moves = get_all_possible_moves(board, color)
    for move in moves:
        temp_board = copy.deepcopy(board)
        make_move(temp_board, move)
        if not is_in_check(temp_board, color):
            return True
    return False

def is_checkmate(board, color):
    if is_in_check(board, color) and not has_any_moves(board, color):
        return True
    return False

def is_stalemate(board, color):
    if not is_in_check(board, color) and not has_any_moves(board, color):
        return True
    return False

def draw_board(win, board, selected_move=None):
    # Draw squares
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE_SQUARE if (row + col) % 2 == 0 else BLACK_SQUARE
            pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Highlight selected move
    if selected_move:
        ((x1, y1), (x2, y2)) = selected_move
        # Highlight from square
        s_from = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s_from.fill(HIGHLIGHT_FROM)
        win.blit(s_from, (y1 * SQUARE_SIZE, x1 * SQUARE_SIZE))
        # Highlight to square
        s_to = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s_to.fill(HIGHLIGHT_TO)
        win.blit(s_to, (y2 * SQUARE_SIZE, x2 * SQUARE_SIZE))
    
    # Draw pieces
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != EMPTY:
                draw_piece(win, piece, row, col)

def draw_piece(win, piece, row, col):
    center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
    center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
    color = WHITE_PIECE_COLOR if piece.isupper() else BLACK_PIECE_COLOR
    
    # Define piece type
    piece_type = piece.upper()
    
    if piece_type == 'P':  # Pawn
        pygame.draw.circle(win, color, (center_x, center_y), PIECE_RADIUS)
    elif piece_type == 'R':  # Rook
        pygame.draw.rect(win, color, (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4, SQUARE_SIZE//2, SQUARE_SIZE//2))
    elif piece_type == 'N':  # Knight
        # Draw a simple triangle to represent the knight
        points = [
            (center_x, center_y - PIECE_RADIUS),
            (center_x - PIECE_RADIUS, center_y + PIECE_RADIUS),
            (center_x + PIECE_RADIUS, center_y + PIECE_RADIUS)
        ]
        pygame.draw.polygon(win, color, points)
    elif piece_type == 'B':  # Bishop
        # Draw a diagonal line to represent the bishop
        pygame.draw.line(win, color, (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4),
                         (col * SQUARE_SIZE + 3*SQUARE_SIZE//4, row * SQUARE_SIZE + 3*SQUARE_SIZE//4), 4)
        pygame.draw.line(win, color, (col * SQUARE_SIZE + 3*SQUARE_SIZE//4, row * SQUARE_SIZE + SQUARE_SIZE//4),
                         (col * SQUARE_SIZE + SQUARE_SIZE//4, row * SQUARE_SIZE + 3*SQUARE_SIZE//4), 4)
    elif piece_type == 'Q':  # Queen
        # Draw a star to represent the queen
        points = [
            (center_x, center_y - PIECE_RADIUS),
            (center_x + PIECE_RADIUS//2, center_y + PIECE_RADIUS//2),
            (center_x - PIECE_RADIUS//2, center_y + PIECE_RADIUS//2)
        ]
        pygame.draw.polygon(win, color, points)
    elif piece_type == 'K':  # King
        # Draw a simple crown
        pygame.draw.line(win, color, (center_x - PIECE_RADIUS, center_y), (center_x + PIECE_RADIUS, center_y), 4)
        pygame.draw.line(win, color, (center_x - PIECE_RADIUS//2, center_y - PIECE_RADIUS//2),
                         (center_x, center_y - PIECE_RADIUS), 4)
        pygame.draw.line(win, color, (center_x + PIECE_RADIUS//2, center_y - PIECE_RADIUS//2),
                         (center_x, center_y - PIECE_RADIUS), 4)

def display_info(win, text):
    info_rect = pygame.Rect(0, HEIGHT, WIDTH, 100)
    pygame.draw.rect(win, INFO_BG_COLOR, info_rect)
    info_text = INFO_FONT.render(text, True, INFO_TEXT_COLOR)
    text_rect = info_text.get_rect(center=(WIDTH//2, HEIGHT + 50))
    win.blit(info_text, text_rect)

def main():
    board = initialize_board()
    clock = pygame.time.Clock()
    current_color = 'white'
    move_count = 1
    running = True
    game_over = False
    selected_move = None
    info = f"{current_color.capitalize()}'s turn"

    while running:
        clock.tick(10)  # Limit to 10 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # Get all legal moves
            all_moves = get_all_possible_moves(board, current_color)
            legal_moves = []
            for move in all_moves:
                temp_board = copy.deepcopy(board)
                make_move(temp_board, move)
                if not is_in_check(temp_board, current_color):
                    legal_moves.append(move)
            
            if not legal_moves:
                if is_in_check(board, current_color):
                    winner = 'Black' if current_color == 'white' else 'White'
                    info = f"Checkmate! {winner} wins!"
                else:
                    info = "Stalemate! It's a draw."
                game_over = True
            else:
                # AI selects a random move
                selected_move = random.choice(legal_moves)
                make_move(board, selected_move)
                (x1, y1), (x2, y2) = selected_move
                piece = board[x2][y2]
                from_square = f"{chr(y1 + ord('a'))}{8 - x1}"
                to_square = f"{chr(y2 + ord('a'))}{8 - x2}"
                info = f"Move {move_count}: {current_color.capitalize()} {piece.upper()} from {from_square} to {to_square}"
                move_count += 1

                # Check for checkmate or stalemate after the move
                opponent = 'black' if current_color == 'white' else 'white'
                if is_checkmate(board, opponent):
                    info = f"Checkmate! {current_color.capitalize()} wins!"
                    game_over = True
                elif is_stalemate(board, opponent):
                    info = "Stalemate! It's a draw."
                    game_over = True
                else:
                    # Switch turn
                    current_color = opponent

                # Pause to visualize the move
                time.sleep(1)

        # Draw everything
        draw_board(WIN, board, selected_move if not game_over else None)
        if game_over:
            display_info(WIN, info)
        else:
            display_info(WIN, info if 'info' in locals() else f"{current_color.capitalize()}'s turn")
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
