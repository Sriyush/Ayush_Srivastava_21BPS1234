import tkinter as tk
from movedesc import get_move_description
from movefun import get_pawn_moves, get_h1_moves, get_h2_moves
from client import setup_client_socket, send_message, receive_messages, send_initial_board_to_server
import socket
import json
class GameBoard:
    def __init__(self, root, host='localhost', port=12346, player_board=None):
        self.host = host
        self.port = port
        self.root = root
        self.board = player_board if player_board is not None else [
            ["bP", "bH1", "bP", "bH2", "bP"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["wP", "wH1", "wP", "wH2", "wP"],
        ]
        self.curr = 'w'
        self.selec = None
        self.available_moves = []
        self.player_color = None
        self.symbols = {
            'wP': '♙', 'bP': '♟',
            'wH1': '♖', 'bH1': '♜',
            'wH2': '♗', 'bH2': '♝'
        }
        self.create_ui()
        self.client_socket = setup_client_socket(self.host, self.port, self.handle_message)

    def initialize_board(self, player_setup=None):
        if player_setup:
            if self.player_color == 'w':
                self.board[4] = player_setup 
                self.board[0] = [piece.replace('w', 'b') for piece in player_setup]
            elif self.player_color == 'b':
                self.board[0] = player_setup 
                self.board[4] = [piece.replace('b', 'w') for piece in player_setup]
        send_initial_board_to_server(self.client_socket, self.board)

    def create_ui(self):
        self.root.title("Chess Game")
        # player_b_label = tk.Label(self.root, text="Player B", font=("Arial", 16))
        # player_b_label.grid(row=0, column=0, columnspan=5, pady=10)
        self.create_board()
        # player_a_label = tk.Label(self.root, text="Player A", font=("Arial", 16))
        # player_a_label.grid(row=1, column=0, columnspan=5, pady=10)
        self.create_move_history()
        self.create_exit_button()

    def create_board(self):
        self.labels = [[None for _ in range(5)] for _ in range(5)]
        for r in range(5):
            for c in range(5):
                piece = self.board[r][c]
                symbol = self.symbols.get(piece, "")
                bg = "white" if (r + c) % 2 == 0 else "gray"
                label = tk.Label(self.root, text=symbol, font=("Arial", 20), width=4, height=2, borderwidth=2, relief="solid", bg=bg)
                label.grid(row=r, column=c)
                label.bind("<Button-1>", lambda e, r=r, c=c: self.select_piece(r, c))
                self.labels[r][c] = label

    def create_move_history(self):
        self.move_history = tk.Text(self.root, height=10, width=30, state=tk.DISABLED)
        self.move_history.grid(row=5, column=0, columnspan=5)

    def create_exit_button(self):
        self.exit_button = tk.Button(self.root, text="Exit", font=("Arial", 16), command=self.exit_game)
        self.exit_button.grid(row=6, column=0, columnspan=5, pady=10)

    def exit_game(self):
        try:
            self.client_socket.close()
            print("Connection closed.")
        except Exception as e:
            print(f"Error closing connection: {e}")
        finally:
            self.root.quit()

    def append_to_history(self, piece, move):
        self.move_history.config(state=tk.NORMAL)
        self.move_history.insert(tk.END, f"{piece} : {move}\n")
        self.move_history.config(state=tk.DISABLED)

    def send_message(self, start_r, start_c, end_r, end_c):
        send_message(self.client_socket, start_r, start_c, end_r, end_c)

    def handle_message(self, message):
        try:
            data = json.loads(message)
            if 'color' in data:
                self.player_color = data['color']
                print(f"Assigned color: {self.player_color}")
            elif 'board' in data:
                self.board = data['board']
                self.curr = data['turn']
                self.update_board()
            elif 'error' in data:
                print(f"Server error: {data['error']}")
            else:
                print(f"Unexpected message format: {message}")
        except json.JSONDecodeError:
            print("Error handling message: Invalid JSON format")

    def select_piece(self, r, c):
        piece = self.board[r][c]
        if self.selec:
            start_r, start_c = self.selec
            if (r, c) in self.available_moves:
                self.move_piece(start_r, start_c, r, c)
                self.send_message(start_r, start_c, r, c)
                self.switch_turn()
            self.deselect()
        elif piece != "--" and piece[0] == self.player_color:
            if self.curr == self.player_color:
                self.selec = (r, c)
                self.show_available_moves(r, c)

    def deselect(self):
        self.selec = None
        self.available_moves = []
        self.update_board()

    def show_available_moves(self, r, c):
        piece = self.board[r][c]
        self.available_moves = self.get_moves_for_piece(piece, r, c)
        for move in self.available_moves:
            mr, mc = move
            self.labels[mr][mc].config(bg="yellow")

    def get_moves_for_piece(self, piece, r, c):
        if piece.startswith("w") or piece.startswith("b"):
            if piece[1] == "P":
                return get_pawn_moves(self.board, piece, r, c)
            elif piece[2] == "1":
                return get_h1_moves(self.board, r, c)
            elif piece[2] == "2":
                return get_h2_moves(self.board, r, c)
        return []

    def move_piece(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        if self.board[end_r][end_c] == "--" or self.board[end_r][end_c][0] != piece[0]:
            move_description = get_move_description(self.board, start_r, start_c, end_r, end_c)
            self.append_to_history(piece, move_description)
            self.board[end_r][end_c] = piece
            self.board[start_r][start_c] = "--"
        self.deselect()
        self.update_board()

    def switch_turn(self):
        self.curr = 'b' if self.curr == 'w' else 'w'

    def update_board(self):
        for r in range(5):
            for c in range(5):
                piece = self.board[r][c]
                symbol = self.symbols.get(piece, "")
                bg = "white" if (r + c) % 2 == 0 else "gray"
                if (r, c) in self.available_moves:
                    bg = "yellow"
                self.labels[r][c].config(text=symbol, bg=bg)

if __name__ == "__main__":
    root = tk.Tk()
    game = GameBoard(root)
    root.mainloop()
