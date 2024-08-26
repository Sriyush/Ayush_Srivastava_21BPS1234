import socket
import threading
import json

class ChessServer:
    def __init__(self, host='localhost', port=12346):
        self.host = host
        self.port = port
        self.clients = []
        self.colors = {}  # To track client colors
        self.board = [
            ["bP", "bH1", "bP", "bH2", "bP"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--"],
            ["wP", "wH1", "wP", "wH2", "wP"],
        ]
        self.current_turn = 'w'
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
            data = json.loads(message)
            if 'start' in data and 'end' in data:
                self.process_move(data, sender_socket)
            else:
                print(f"Unexpected message format: {message}")
        except json.JSONDecodeError:
            print("Error handling message: Invalid JSON format")

    def process_move(self, move_data, sender_socket):
        start_r, start_c = move_data['start']
        end_r, end_c = move_data['end']
        piece = self.board[start_r][start_c]
        player_color = self.colors[sender_socket]

        # Check if the piece belongs to the player and if it's the player's turn
        if piece.startswith(player_color) and player_color == self.current_turn:
            # Update board state
            if self.board[end_r][end_c] == "--" or self.board[end_r][end_c][0] != piece[0]:
                self.board[end_r][end_c] = piece
                self.board[start_r][start_c] = "--"
                self.switch_turn()

                # Notify both clients
                move_update = {
                    'board': self.board,
                    'turn': self.current_turn
                }
                message = json.dumps(move_update)
                for client in self.clients:
                    client.send(message.encode('utf-8'))
        else:
            # Send an error message if the move is invalid
            error_message = json.dumps({'error': 'Invalid move or not your turn.'})
            sender_socket.send(error_message.encode('utf-8'))

    def switch_turn(self):
        self.current_turn = 'b' if self.current_turn == 'w' else 'w'

if __name__ == "__main__":
    ChessServer()
