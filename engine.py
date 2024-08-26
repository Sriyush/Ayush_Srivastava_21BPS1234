import tkinter as tk
import socket
import threading
import json

class GameBoard:
    def __init__(self, root, host='localhost', port=12346,player_board=None):
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
        self.current_turn = 'w'
        self.selected_piece = None
        self.available_moves = []
        self.player_color = None
        self.symbols = {
            'wP': '♙', 'bP': '♟',
            'wH1': '♖', 'bH1': '♜',
            'wH2': '♗', 'bH2': '♝'
        }
        self.create_ui()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def initialize_board(self, player_setup=None):
        if player_setup:
            if self.player_color == 'w':
                self.board[4] = player_setup 
                self.board[0] = [piece.replace('w', 'b') for piece in player_setup]
            elif self.player_color == 'b':
                self.board[0] = player_setup 
                self.board[4] = [piece.replace('b', 'w') for piece in player_setup]
        self.send_initial_board_to_server()



    def send_initial_board_to_server(self):
        setup_message = json.dumps({'initial_board': self.board})
        self.client_socket.send(setup_message.encode('utf-8'))
        print("Initial board setup sent to server.")


    def create_ui(self):
        self.root.title("Chess Game")
        player_b_label = tk.Label(self.root, text="Player B", font=("Arial", 16))
        # player_b_label.pack(pady=10)
        self.create_board()
        player_a_label = tk.Label(self.root, text="Player A", font=("Arial", 16))
        # player_a_label.pack(pady=10)
        self.create_move_history()
        self.create_exit_button()
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

    def append_to_history(self, piece, move):
        self.move_history.config(state=tk.NORMAL)
        self.move_history.insert(tk.END, f"{piece} : {move}\n")
        self.move_history.config(state=tk.DISABLED)
    
    def send_message(self, start_r, start_c, end_r, end_c):
        # descrip = self.get_move_description(start_r, start_c, end_r, end_c)
        move_data = {
            'start': [start_r, start_c],
            'end': [end_r, end_c],
            # 'descrip': descrip
        }
        message = json.dumps(move_data)
        try:
            self.client_socket.send(message.encode('utf-8'))
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Send error: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"Received from server: {message}")
                    self.handle_message(message)
                else:
                    break
            except Exception as e:
                print(f"Receive error: {e}")
                break
    
    def handle_message(self, message):
        try:
            data = json.loads(message)
            if 'color' in data:
                self.player_color = data['color']
                print(f"Assigned color: {self.player_color}")
            elif 'board' in data:
                self.board = data['board']
                self.current_turn = data['turn']
                self.update_board()
            elif 'error' in data:
                print(f"Server error: {data['error']}")
            # elif 'descrip' in data:
            #     self.append_to_history("Move", data['descrip'])
            else:
                print(f"Unexpected message format: {message}")
        except json.JSONDecodeError:
            print("Error handling message: Invalid JSON format")

    def select_piece(self, r, c):
        piece = self.board[r][c]
        if self.selected_piece:
            start_r, start_c = self.selected_piece
            if (r, c) in self.available_moves:
                self.move_piece(start_r, start_c, r, c)
                self.send_message(start_r, start_c, r, c)
                self.switch_turn()
            self.deselect()
        elif piece != "--" and piece[0] == self.player_color:
            if self.current_turn == self.player_color:
                self.selected_piece = (r, c)
                self.show_available_moves(r, c)

    def deselect(self):
        self.selected_piece = None
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
                return self.get_pawn_moves(piece, r, c)
            elif piece[2] == "1":
                return self.get_h1_moves(r, c)
            elif piece[2] == "2":
                return self.get_h2_moves(r, c)
        return []

    def get_pawn_moves(self, piece, r, c):
        moves = []
        direction = -1 if piece.startswith("w") else 1

        if 0 <= r + direction < 5 and self.board[r + direction][c] == "--":
            moves.append((r + direction, c))

        if 0 <= c - 1 < 5 and self.board[r][c - 1] == "--":
            moves.append((r, c - 1))

        if 0 <= c + 1 < 5 and self.board[r][c + 1] == "--":
            moves.append((r, c + 1))
        
        if 0 <= r - direction < 5 and self.board[r - direction][c] == "--":
            moves.append((r - direction, c))
        
        return moves

    def get_h1_moves(self, r, c):
        moves = []
        for dr, dc in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                if self.board[nr][nc] == "--":
                    moves.append((nr, nc))
                elif self.board[nr][nc][0] != self.board[r][c][0]:  
                    moves.append((nr, nc))
        return moves

    def get_h2_moves(self, r, c):
        moves = []
        for dr, dc in [(2, 2), (2, -2), (-2, 2), (-2, -2)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:
                if self.board[nr][nc] == "--" or self.board[nr][nc][0] != self.board[r][c][0]:
                    moves.append((nr, nc))
        return moves

    def move_piece(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        if self.board[end_r][end_c] == "--" or self.board[end_r][end_c][0] != piece[0]:
            move_description = self.get_move_description(start_r, start_c, end_r, end_c)
            self.append_to_history(piece, move_description)
            self.board[end_r][end_c] = piece
            self.board[start_r][start_c] = "--"
        self.deselect()
        self.update_board()

    def switch_turn(self):
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

    def update_board(self):
        for r in range(5):
            for c in range(5):
                piece = self.board[r][c]
                symbol = self.symbols.get(piece, "")
                bg = "white" if (r + c) % 2 == 0 else "gray"
                if (r, c) in self.available_moves:
                    bg = "yellow"
                self.labels[r][c].config(text=symbol, bg=bg)

    def get_move_description(self, start_r, start_c, end_r, end_c):
        piece = self.board[start_r][start_c]
        
        direction = "Move"
        
        if piece[1] == "P":
            if end_r < start_r:
                if piece[0] == "w":
                    direction = "F"
                else:
                    direction = "B"
            elif end_r > start_r:
                if piece[0] == "w":
                    direction = "B" 
                else:
                    direction = "F"
            elif end_c > start_c:
                if piece[0] == "w":
                    direction = "R"
                else:
                    direction = "L"
            elif end_c < start_c:
                if piece[0] == "w":
                    direction = "L"
                else:
                    direction = "R"
        

        elif piece[2] == "1": 
            if end_r - start_r == 2 or start_r - end_r == 2:
                if piece[0] == "w":
                    direction = "F" if end_r < start_r else "B"
                else:
                    direction = "B" if end_r < start_r else "F"
            elif end_c - start_c == 2 or start_c - end_c == 2:
                if piece[1] == "b":
                    direction = "R" if end_c > start_c else "L"
                else:
                    direction = "L" if end_c > start_c else "R"

        elif piece[2] == "2": 
                    if end_r < start_r:
                        if end_c > start_c:
                            if piece[0] == "w":
                                direction = "FR"
                            else:
                                direction = "BL"
                        else:
                            if piece[0] == "w":
                                direction = "FL"
                            else:
                                direction = "BR"
                    else:
                        if end_c > start_c:
                            if piece[0] == "w":
                                direction = "BR"
                            else:
                                direction = "FL"
                        else:
                            if piece[0] == "w":
                                direction = "BL"
                            else:
                                direction = "FR"
            
        return direction

if __name__ == "__main__":
    root = tk.Tk()
    game = GameBoard(root)
    root.mainloop()
# {piece} from ({start_r}, {start_c}) to ({end_r}, {end_c}) - 