import socket
import threading
import json

class ChessServer:
    def __init__(self, host='localhost', port=12346):
        self.host = host
        self.port = port
        self.clients = []
        self.colors = {}
        self.board = [
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"]
        ]
        self.current_turn = 'w'
        self.setup_done = {'w': False, 'b': False}
        self.start_server()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(2)
        print("Server started. Waiting for clients...")
        self.accept_clients()

    def accept_clients(self):
        while len(self.clients) < 2:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            color = 'w' if len(self.clients) == 1 else 'b'
            self.colors[client_socket] = color
            client_socket.send(json.dumps({'color': color}).encode('utf-8'))
            print(f"Client connected from {addr} as {color}")
            threading.Thread(target=self.client_handler, args=(client_socket,)).start()

            if len(self.clients) == 2:
                self.send_board_to_clients()

    def client_handler(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    print(f"Received: {message}")
                    self.handle_message(message, client_socket)
                else:
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
        client_socket.close()

    def handle_message(self, message, sender_socket):
        try:
            print(f"Received message: {message}")
            data = json.loads(message)
            print(f"Parsed data: {data}")
            if 'initial_board' in data:
                self.handle_initial_board(data, sender_socket)
            elif 'start' in data and 'end' in data:
                self.process_move(data, sender_socket)
            elif 'place' in data and 'piece' in data:
                self.process_place(data, sender_socket)
            else:
                print(f"Unexpected message format: {message}")
        except json.JSONDecodeError:
            print("Error handling message: Invalid JSON format")
        except Exception as e:
            print(f"Exception in handle_message: {e}")


    def handle_initial_board(self, data, sender_socket):
        color = self.colors[sender_socket]
        player_board = data['initial_board']
        
        print(f"Setting up board for player {color}.")
        print(f"Received board: {player_board}")

        if color == 'w':
            self.board[4] = player_board[4]  # Using only the last row (index 4)
            print(f"White pieces set at row 4: {self.board[4]}")
        elif color == 'b':
            # Convert 'w' to 'b' for black pieces and place them in the first row (index 0)
            self.board[0] = [piece.replace('w', 'b') if piece.startswith('w') else piece for piece in player_board[4]]
            print(f"Black pieces set at row 0: {self.board[0]}")
        
        self.setup_done[color] = True
        
        # Check if both setups are done
        if all(self.setup_done.values()):
            print(f"Both players have set up their pieces. Sending board to clients...")
            self.send_board_to_clients()
        else:
            print(f"Waiting for the other player to set up. Current board state: {self.board}")




    def send_board_to_clients(self):
        board_message = json.dumps({'board': self.board, 'turn': self.current_turn})
        for client in self.clients:
            client.send(board_message.encode('utf-8'))

    def process_move(self, move_data, sender_socket):
        start_r, start_c = move_data['start']
        end_r, end_c = move_data['end']
        piece = self.board[start_r][start_c]
        player_color = self.colors[sender_socket]

        if piece.startswith(player_color) and player_color == self.current_turn:
            if self.board[end_r][end_c] == "--" or self.board[end_r][end_c][0] != piece[0]:
                self.board[end_r][end_c] = piece
                self.board[start_r][start_c] = "--"
                self.switch_turn()
                self.send_board_to_clients()
        else:
            error_message = json.dumps({'error': 'Invalid move or not your turn.'})
            sender_socket.send(error_message.encode('utf-8'))

    def process_place(self, place_data, sender_socket):
        row, col = place_data['place']
        piece = place_data['piece']
        player_color = self.colors[sender_socket]

        if isinstance(piece, str) and piece.startswith(player_color):
            self.board[row][col] = piece
            print(f"Piece placed: {piece} at {row}, {col} by {player_color}")
            self.send_board_to_clients()
        else:
            error_message = json.dumps({'error': 'Invalid piece placement.'})
            sender_socket.send(error_message.encode('utf-8'))


    def switch_turn(self):
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

if __name__ == '__main__':
    ChessServer()
