
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

orange_waves = tk.Tk()
orange_waves.title("ORANGE WAVES")
orange_waves.geometry("782x441")

# --- GRADIENT BACKGROUND CONFIGURATION ---
# Create a canvas to hold the smooth gradient
bg_canvas = tk.Canvas(orange_waves, highlightthickness=0)
bg_canvas.pack(fill="both", expand=True)

def draw_gradient(canvas):
    
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    
    r1, g1, b1 = 255, 166, 166  # Top color: Orange
    r2, g2, b2 = 102, 1, 1       # Bottom color: Black

    for y in range(height):
        ratio = y / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, width, y, fill=color)

# Bind the gradient drawing to window resizing so it stays responsive
bg_canvas.bind("<Configure>", lambda event: draw_gradient(bg_canvas))
# ----------------------------------------

orange_waves.update_idletasks()

geometryX = 0
geometryY = 0
orange_waves.geometry("+%d+%d"%(geometryX, geometryY))

# Handle the window icon
try:
    orange_waves_img = Image.open(os.path.join(BASE_DIR, "assets", "images", "orange waves logo.png"))
    orange_waves_img = ImageTk.PhotoImage(orange_waves_img)
    orange_waves.iconphoto(False, orange_waves_img)
except Exception:
    pass # Falls back gracefully if the image path isn't found during testing

style = ttk.Style(orange_waves)
style.theme_use("clam")

# Button Styling R
style.configure("r.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 13, "bold"), cursor="arrow")
style.map("r.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

r = ttk.Button(master=orange_waves, text="MARKS \n CALCULATOR", style="r.TButton")
r.place(x=50, y=55, width=151, height=57)

# Button Styling B
style.configure("b.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 13, "bold"), cursor="arrow")
style.map("b.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

b = ttk.Button(master=orange_waves, text="GOALS SETTER", style="b.TButton")
b.place(x=230, y=55, width=151, height=57)

# Button Styling B1
style.configure("b1.TButton", background="#545454", foreground="#ffffff", borderwidth=3, font=("Courier", 13, "bold"), cursor="arrow")
style.map("b1.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

b1 = ttk.Button(master=orange_waves, text="CALCULATOR", style="b1.TButton")
b1.place(x=418, y=55, width=151, height=57)

orange_waves.mainloop()
