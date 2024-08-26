import tkinter as tk
from tkinter import simpledialog


class WelcomePage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.label = tk.Label(self.frame, text="Welcome to 'Last Man Standing Chess'", font=("Arial", 24))
        self.label.pack(pady=20)

        self.play_button = tk.Button(self.frame, text="Play With Another Client", font=("Arial", 16), command=lambda: self.select_pieces())
        self.play_button.pack(pady=20)

        self.rules_button = tk.Button(self.frame, text="Rules", font=("Arial", 16), command=lambda: print("Rules"))
        self.rules_button.pack(pady=20)

    def select_pieces(self):
        num_pawns = simpledialog.askinteger("Input", "Number of Pawns:", parent=self.root, minvalue=0, maxvalue=5)
        num_hero1 = simpledialog.askinteger("Input", "Number of Hero1:", parent=self.root, minvalue=0, maxvalue=5)
        num_hero2 = simpledialog.askinteger("Input", "Number of Hero2:", parent=self.root, minvalue=0, maxvalue=5)

        if num_pawns + num_hero1 + num_hero2 != 5:
            tk.messagebox.showerror("Error", "Total pieces must be exactly 5.")
            return

        self.player_board = self.create_custom_board(num_pawns, num_hero1, num_hero2)
        self.start_game()


    def create_custom_board(self, num_pawns, num_hero1, num_hero2):
        board = [["--"] * 5 for _ in range(5)]
        row = 4  # Place pieces on the 5th row for the white player (adjust for black as needed)
        col = 0
        for _ in range(num_pawns):
            board[row][col] = "wP"
            col += 1
        for _ in range(num_hero1):
            board[row][col] = "wH1"
            col += 1
        for _ in range(num_hero2):
            board[row][col] = "wH2"
            col += 1
        return board

    def start_game(self):
        if not hasattr(self, 'player_board'):
            print("Player setup not yet initialized.")
            return
        self.frame.pack_forget()
        import engine
        game_board = engine.GameBoard(self.root, player_board=self.player_board)  # Pass custom board
        game_board.initialize_board(self.player_board)  # Initialize with player's chosen 

root = tk.Tk()
root.geometry("600x600")
app = WelcomePage(root)
root.mainloop()
