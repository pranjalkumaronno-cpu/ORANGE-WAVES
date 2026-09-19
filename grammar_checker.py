import tkinter as tk
from tkinter import ttk


def open_grammar_checker(parent_window):
    parent_window.withdraw()
    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - Grammar Checker")
    window.geometry("600x400+100+100")
    window.config(bg="#ababab")

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text="✍️ Grammar & Text Checker", font=("Arial", 18, "bold"), bg="#ababab").pack(pady=20)
    tk.Label(window, text="Analyze and check your essays or reports here.", font=("Arial", 11), bg="#ababab").pack(pady=10)
    # Ready for your custom layout widgets later!

    ttk.Button(window, text="Back to Main Hub", command=on_close).pack(pady=40)