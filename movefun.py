def get_pawn_moves(board, piece, r, c):
    moves = []
    direction = -1 if piece.startswith("w") else 1

    if 0 <= r + direction < 5 and board[r + direction][c] == "--":
        moves.append((r + direction, c))

    if 0 <= c - 1 < 5 and board[r][c - 1] == "--":
        moves.append((r, c - 1))

    if 0 <= c + 1 < 5 and board[r][c + 1] == "--":
        moves.append((r, c + 1))
    
    if 0 <= r - direction < 5 and board[r - direction][c] == "--":
        moves.append((r - direction, c))
    
    return moves

def get_h1_moves(board, r, c):
    moves = []
    for dr, dc in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 5 and 0 <= nc < 5:
            if board[nr][nc] == "--":
                moves.append((nr, nc))
            elif board[nr][nc][0] != board[r][c][0]:  
                moves.append((nr, nc))
    return moves

def get_h2_moves(board, r, c):
    moves = []
    for dr, dc in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 5 and 0 <= nc < 5:
            if board[nr][nc] == "--" or board[nr][nc][0] != board[r][c][0]:
                moves.append((nr, nc))
    return moves
