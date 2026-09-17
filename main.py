# This code is generated using PyUIbuilder: https://pyuibuilder.com

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


orange_waves = tk.Tk()
orange_waves.title("ORANGE WAVES")
orange_waves.config(bg="#ccff00")
orange_waves.geometry("782x441")
orange_waves.update_idletasks()

geometryX = 0
geometryY = 0

orange_waves.geometry("+%d+%d"%(geometryX, geometryY))
orange_waves_img = Image.open(os.path.join(BASE_DIR, "assets", "images", "orange waves logo.png"))
orange_waves_img = ImageTk.PhotoImage(orange_waves_img)
orange_waves.iconphoto(False, orange_waves_img)


style = ttk.Style(orange_waves)
style.theme_use("clam")


style.configure("r.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 13, "bold"), cursor="arrow")
style.map("r.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

r = ttk.Button(master=orange_waves, text="MARKS \n CALCULATOR", style="r.TButton")
r.place(x=50, y=55, width=151, height=57)

style.configure("b.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 13, "bold"), cursor="arrow")
style.map("b.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

b = ttk.Button(master=orange_waves, text="GOALS SETTER", style="b.TButton")
b.place(x=230, y=55, width=151, height=57)

style.configure("b1.TButton", background="#545454", foreground="#ffffff", borderwidth=3, font=("Courier", 13, "bold"), cursor="arrow")
style.map("b1.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")])

b1 = ttk.Button(master=orange_waves, text="CALCULATOR", style="b1.TButton")
b1.place(x=418, y=55, width=151, height=57)


orange_waves.mainloop()