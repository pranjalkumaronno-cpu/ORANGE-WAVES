import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import user_profile  # Interconnected Profile System


def open_goal_setter(parent_window, get_marks_summary_func=None):
    parent_window.withdraw()
    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - Goal & XP Tracker")
    window.geometry("920x620+50+50")
    window.config(bg="#ababab")

    # Track which static/manual task rows have already granted XP to prevent abuse
    rewarded_tasks = set()
    # FIX: separate tracker for the physical-activity listbox, keyed by list index,
    # so unchecking then rechecking the same item can't farm XP repeatedly.
    phys_rewarded_indices = set()

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    # --- 🏆 GAMIFICATION PROFILE PANEL ---
    xp_frame = tk.LabelFrame(window, text=" 🏆 Level & Progression Profile ", bg="#d6d6d6", fg="#000", font=("Arial", 10, "bold"))
    xp_frame.pack(fill="x", padx=25, pady=10)

    lvl_lbl = tk.Label(xp_frame, text="Level: --", font=("Arial", 11, "bold"), bg="#d6d6d6")
    lvl_lbl.pack(side="left", padx=15, pady=8)

    title_lbl = tk.Label(xp_frame, text="Rank: --", font=("Arial", 10, "italic"), bg="#d6d6d6", fg="#444")
    title_lbl.pack(side="left", padx=10, pady=8)

    xp_progress = ttk.Progressbar(xp_frame, orient="horizontal", mode="determinate", length=350)
    xp_progress.pack(side="left", padx=20, pady=8)

    xp_lbl = tk.Label(xp_frame, text="XP: 0/0", font=("Arial", 9, "bold"), bg="#d6d6d6")
    xp_lbl.pack(side="left", padx=10, pady=8)

    def update_profile_display():
        """Pulls numbers from user_profile to redraw progression bars."""
        lvl, current_prog, max_needed, rank_title = user_profile.calculate_level_info()
        lvl_lbl.config(text=f"Level: {lvl}")
        title_lbl.config(text=f"Rank: {rank_title}")
        xp_lbl.config(text=f"{current_prog} / {max_needed} XP (Total: {user_profile.get_xp()})")
        pct = (current_prog / max_needed) * 100
        xp_progress["value"] = pct

    # Initialize layout metrics on load
    update_profile_display()

    # --- MAIN CONTROLLERS & FRAMES ---
    main_frame = tk.Frame(window, bg="#ababab")
    main_frame.pack(fill="both", expand=True, padx=15, pady=5)

    # 🏃‍♂️ LEFT SIDE: PHYSICAL SCHEDULE
    phys_frame = tk.LabelFrame(main_frame, text=" 🏃‍♂️ Physical & Fitness Goals ", bg="#d6d6d6", fg="#000", font=("Arial", 11, "bold"))
    phys_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

    tk.Label(phys_frame, text="Activity Description:", bg="#d6d6d6", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")

    phys_entry = ttk.Entry(phys_frame, width=28)
    phys_entry.grid(row=0, column=1, padx=10, pady=10)

    phys_listbox = tk.Listbox(phys_frame, bg="#ffffff", height=14, width=42, font=("Arial", 10))
    phys_listbox.grid(row=2, column=0, columnspan=2, padx=15, pady=10)

    def add_physical_item():
        text = phys_entry.get().strip()
        if text:
            phys_listbox.insert(tk.END, f"☐  {text}")
            phys_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Empty Target", "Please type a physical goal activity first!")

    add_phys_btn = ttk.Button(phys_frame, text="Add Activity", command=add_physical_item)
    add_phys_btn.grid(row=1, column=0, columnspan=2, pady=5)

    # 📚 RIGHT SIDE: ACADEMIC SCHEDULE
    acad_frame = tk.LabelFrame(main_frame, text=" 📚 Academic & Study Planner ", bg="#d6d6d6", fg="#000", font=("Arial", 11, "bold"))
    acad_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

    acad_canvas_frame = tk.Frame(acad_frame, bg="#ffffff", bd=1, relief="sunken")
    acad_canvas_frame.place(x=15, y=120, width=390, height=270)

    checklist_inner = tk.Frame(acad_canvas_frame, bg="#ffffff")
    checklist_inner.pack(fill="both", expand=True, padx=5, pady=5)

    checklist_items = []

    def clear_academic_view():
        nonlocal checklist_items
        for item in checklist_inner.winfo_children():
            item.destroy()
        checklist_items.clear()
        rewarded_tasks.clear()

    def add_custom_academic_row():
        row_idx = len(checklist_items)
        var = tk.BooleanVar(value=False)

        ent = ttk.Entry(checklist_inner, width=28)
        ent.grid(row=row_idx, column=1, padx=5, pady=4, sticky="w")

        # FIX: manual rows previously awarded XP on every single check (toggle
        # on/off/on/off = infinite XP). Give each row a unique key and only
        # award once per key, same protection the auto-generated rows already had.
        row_key = f"manual_row_{row_idx}"

        def on_toggle():
            if var.get() and row_key not in rewarded_tasks:
                rewarded_tasks.add(row_key)
                user_profile.add_xp(5)
                messagebox.showinfo("Task Complete!", "+5 XP Earned! Keep it up.")
                update_profile_display()

        chk = tk.Checkbutton(checklist_inner, variable=var, bg="#ffffff", activebackground="#ffffff", command=on_toggle)
        chk.grid(row=row_idx, column=0, padx=5, pady=4)

        checklist_items.append({"var": var, "entry": ent, "static_text": None})

    def generate_from_calculator():
        clear_academic_view()
        if not get_marks_summary_func:
            messagebox.showerror("Error", "Pipeline system connection error.")
            return

        marks_data = get_marks_summary_func()
        if not marks_data or len(marks_data) == 0:
            messagebox.showinfo("No Data Found", "No calculator records found yet. Please compute your marks first or build manually!")
            return

        row_count = 0
        for sub_name, percent in marks_data.items():
            var = tk.BooleanVar(value=False)
            # FIX: format spec was "{percent*:.1f*}" (invalid syntax).
            status_text = f"Review {sub_name} (Current Level: {percent:.1f}%)"

            # Context-closure logic to match unique row string indexes cleanly
            def make_cmd(txt=status_text, v=var):
                return lambda: check_static_task(txt, v)

            chk = tk.Checkbutton(checklist_inner, text=status_text, variable=var, font=("Arial", 9), bg="#ffffff", anchor="w", command=make_cmd())
            chk.grid(row=row_count, column=0, columnspan=2, padx=10, pady=5, sticky="w")

            checklist_items.append({"var": var, "entry": None, "static_text": status_text})
            row_count += 1

    def check_static_task(task_key, variable_state):
        """Validates triggers so clicking a subject list item awards XP only once."""
        if variable_state.get() and task_key not in rewarded_tasks:
            rewarded_tasks.add(task_key)
            user_profile.add_xp(5)
            messagebox.showinfo("Task Complete!", f"+5 XP Granted for: {task_key}")
            update_profile_display()

    # Strategy Option Panel Anchors
    tk.Label(acad_frame, text="Choose Strategy:", bg="#d6d6d6", font=("Arial", 10, "bold")).place(x=15, y=15)

    strategy_auto_btn = ttk.Button(acad_frame, text="🤖 Auto-Build From Marks", command=generate_from_calculator)
    strategy_auto_btn.place(x=15, y=45, width=190, height=30)

    strategy_manual_btn = ttk.Button(acad_frame, text="✍️ Build Manually", command=lambda: [clear_academic_view(), add_custom_academic_row()])
    strategy_manual_btn.place(x=215, y=45, width=190, height=30)

    add_manual_row_btn = ttk.Button(acad_frame, text="+ Add Entry Line", command=add_custom_academic_row)
    add_manual_row_btn.place(x=15, y=85, width=120, height=25)

    # --- FOOTER INTERFACES ---
    footer_frame = tk.Frame(window, bg="#ababab")
    footer_frame.pack(fill="x", side="bottom", pady=15)

    def toggle_listbox_item(event):
        """Double clicking a physical schedule list item awards 5 XP and checks it, once per item."""
        try:
            index = phys_listbox.curselection()
            val = phys_listbox.get(index)
            idx_num = index[0] if isinstance(index, tuple) else index

            if val.startswith("☐"):
                phys_listbox.delete(index)
                phys_listbox.insert(idx_num, val.replace("☐", "☑", 1))
                # FIX: only award XP the first time this index is checked off.
                if idx_num not in phys_rewarded_indices:
                    phys_rewarded_indices.add(idx_num)
                    user_profile.add_xp(5)
                    messagebox.showinfo("Task Complete!", "+5 XP Earned for Physical Activity!")
                    update_profile_display()
            elif val.startswith("☑"):
                phys_listbox.delete(index)
                phys_listbox.insert(idx_num, val.replace("☑", "☐", 1))
                # Note: unchecking does not refund XP, and re-checking (above)
                # will no longer re-award it since idx_num stays in phys_rewarded_indices.
        except IndexError:
            pass

    phys_listbox.bind("<Double-1>", toggle_listbox_item)

    ttk.Button(footer_frame, text="💾 Save Schedules", command=lambda: messagebox.showinfo("Saved", "Schedules archived successfully!")).pack(side="left", padx=50)
    ttk.Button(footer_frame, text="⬅ Back to Hub Menu", command=on_close).pack(side="right", padx=50)