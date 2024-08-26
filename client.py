import socket
import json
import threading

def setup_client_socket(host, port, receive_callback):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, receive_callback))
    receive_thread.start()
    
    return client_socket

def send_initial_board_to_server(client_socket, board):
    setup_message = json.dumps({'initial_board': board})
    client_socket.send(setup_message.encode('utf-8'))
    print("Initial board setup sent to server.")

def send_message(client_socket, start_r, start_c, end_r, end_c):
    move_data = {
        'start': [start_r, start_c],
        'end': [end_r, end_c]
    }
    message = json.dumps(move_data)
    try:
        client_socket.send(message.encode('utf-8'))
        print(f"Sent: {message}")
    except Exception as e:
        print(f"Send error: {e}")

def receive_messages(client_socket, receive_callback):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Received from server: {message}")
                receive_callback(message)
            else:
                break
        except Exception as e:
            print(f"Receive error: {e}")
            break
