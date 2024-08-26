import tkinter as tk
import socket
import threading

class GameClient:
    def __init__(self, root, host='localhost', port=12346):
        self.root = root
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
            print("Connected to server")
        except Exception as e:
            print(f"Connection error: {e}")
            return

        self.root.title("Chess Game Client")
        self.create_ui()
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def create_ui(self):
        # Create your UI elements here
        self.label = tk.Label(self.root, text="Client Connected", font=("Arial", 16))
        self.label.pack(pady=20)
        print("UI Created")

    def send_message(self, message):
        try:
            self.client.send(message.encode('utf-8'))
            print(f"Sent: {message}")
        except Exception as e:
            print(f"Send error: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    print(f"Received: {message}")
                else:
                    break
            except Exception as e:
                print(f"Receive error: {e}")
                break

if __name__ == "__main__":
    root = tk.Tk()
    client = GameClient(root)
    root.mainloop()
