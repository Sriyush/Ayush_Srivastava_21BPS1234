import tkinter as tk


class WelcomePage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(expand=True, fill=tk.BOTH)
        self.label = tk.Label(self.frame, text="Welcome to 'Last Man Standing Chess'", font=("Arial", 24))
        self.label.pack(pady=20)


        self.play_button = tk.Button(self.frame, text="Play With Another Client", font=("Arial", 16), command=lambda: self.start_game())
        self.play_button.pack(pady=20)

        self.play_button = tk.Button(self.frame, text="Rules", font=("Arial", 16), command=print("Rules"))
        self.play_button.pack(pady=20)
    def start_game(self):
        self.frame.pack_forget()
        import engine
        engine.GameBoard(self.root) 

root = tk.Tk()
root.geometry("600x600")
app = WelcomePage(root)
root.mainloop()
