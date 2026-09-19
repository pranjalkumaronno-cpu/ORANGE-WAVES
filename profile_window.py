import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import user_profile
import gui_components


def open_profile_view(parent_window, trigger_relogin_callback):
    parent_window.withdraw()
    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - User Profile Portfolio")
    window.geometry("600x520+50+50")
    window.resizable(False, False)

    bg_canvas = tk.Canvas(window, highlightthickness=0)
    bg_canvas.pack(fill="both", expand=True)
    bg_canvas.bind("<Configure>", lambda event: gui_components.draw_gradient(bg_canvas))

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    active_user = user_profile.get_logged_in_user()
    user_records = user_profile._get_active_profile()
    user_gmail = user_records.get("gmail", "Not Provided") if user_records else "None"
    # FIX: active_user could be None if this window is somehow opened without a
    # logged-in session; guard before calling .upper() on it.
    display_name = active_user.upper() if active_user else "UNKNOWN"

    tk.Label(window, text=f"👤 {display_name}'S PORTFOLIO", font=("Arial", 18, "bold"), fg="#fff", bg="#ffa6a6").place(relx=0.5, y=35, anchor="center")
    tk.Label(window, text=f"Registered Email: {user_gmail}", font=("Arial", 10), fg="#fff", bg="#802323").place(relx=0.5, y=70, anchor="center")

    lvl, current_prog, max_needed, rank_title = user_profile.calculate_level_info()

    card = tk.Frame(window, bg="#ffffff", bd=1, relief="solid")
    card.place(x=50, y=105, width=500, height=110)

    tk.Label(card, text=f"Current Level: {lvl}", font=("Arial", 14, "bold"), bg="#ffffff", fg="#000").pack(pady=5)
    tk.Label(card, text=f"Rank Title: {rank_title}", font=("Arial", 11, "italic"), bg="#ffffff", fg="#555").pack()

    xp_progress = ttk.Progressbar(card, orient="horizontal", mode="determinate", length=400)
    xp_progress.pack(pady=8)
    xp_progress["value"] = (current_prog / max_needed) * 100

    tk.Label(card, text=f"Progress: {current_prog}/{max_needed} XP (Total accumulated: {user_profile.get_xp()} XP)", font=("Arial", 9), bg="#ffffff", fg="#444").pack()

    marks_frame = tk.LabelFrame(window, text=" 📜 Last Saved Academic Matrix Performance ", bg="#d6d6d6", fg="#000", font=("Arial", 10, "bold"))
    marks_frame.place(x=50, y=235, width=500, height=180)

    saved_marks = user_profile.get_saved_marks()

    if not saved_marks:
        tk.Label(marks_frame, text="No computational metrics recorded yet.\nRun the Marks Calculator to link scores here!", font=("Arial", 10, "italic"), bg="#d6d6d6", fg="#555").pack(pady=50)
    else:
        row_idx = 0
        for sub, score in saved_marks.items():
            tk.Label(marks_frame, text=f"• {sub}:", font=("Arial", 10, "bold"), bg="#d6d6d6").grid(row=row_idx, column=0, padx=25, pady=4, sticky="w")
            tk.Label(marks_frame, text=f"{score:.2f}% Match Performance Level", font=("Arial", 10), bg="#d6d6d6", fg="#b02c2c" if score < 75 else "#1c7a1c").grid(row=row_idx, column=1, padx=10, pady=4, sticky="w")
            row_idx += 1

    def trigger_logout():
        if messagebox.askyesno("Log Out", "Are you sure you want to log out of your profile session?"):
            user_profile.logout_user()
            window.destroy()
            trigger_relogin_callback()

    ttk.Button(window, text="⬅ Return to Suite Hub", command=on_close).place(x=50, y=440, width=220, height=35)
    ttk.Button(window, text="🚪 Log Out Profile", command=trigger_logout).place(x=330, y=440, width=220, height=35)