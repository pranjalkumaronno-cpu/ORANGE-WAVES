import tkinter as tk
from tkinter import ttk
import gui_components


def open_marks_selector_window(parent_window, open_main_window_func):
    parent_window.withdraw()
    selector = tk.Toplevel(parent_window)
    selector.title("ORANGE WAVES - Marks Matrix Setup")
    selector.geometry("782x441")
    selector.resizable(False, False)

    bg_canvas = tk.Canvas(selector, highlightthickness=0)
    bg_canvas.pack(fill="both", expand=True)
    bg_canvas.bind("<Configure>", lambda event: gui_components.draw_gradient(bg_canvas))

    def on_close():
        selector.destroy()
        parent_window.deiconify()

    selector.protocol("WM_DELETE_WINDOW", on_close)

    welcome_label = tk.Label(selector, text="MARKS PERFORMANCE MATRIX", font=("Arial", 22, "bold"), fg="#fff", bg="#ffa6a6")
    welcome_label.place(relx=0.5, y=60, anchor="center")

    tk.Label(selector, text="Select Academic Stream:", font=("Arial", 11, "bold"), fg="#fff", bg="#802323").place(x=220, y=180)

    stream_var = tk.StringVar(value="Science")
    stream_dropdown = ttk.Combobox(selector, textvariable=stream_var, values=["Science", "Commerce", "Art", "Non High School Student"], state="readonly", width=22)
    stream_dropdown.place(x=420, y=180)

    split_var = tk.BooleanVar(value=False)
    split_checkbox = tk.Checkbutton(selector, text="Split Marks (Project / Assessment / Exam)", variable=split_var, font=("Arial", 10), fg="#000", bg="#ababab")
    split_checkbox.place(relx=0.5, y=240, anchor="center")

    def launch_matrix():
        chosen_stream = stream_var.get()
        is_split = split_var.get()
        selector.destroy()
        open_main_window_func(chosen_stream=chosen_stream, split_marks=is_split)

    launch_btn = ttk.Button(selector, text="Launch Matrix Calculator", command=launch_matrix)
    launch_btn.place(relx=0.5, y=320, width=220, height=40, anchor="center")