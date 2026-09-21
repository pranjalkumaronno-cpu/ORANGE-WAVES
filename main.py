import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Interconnecting modules via import statements
import gui_components
import app_logic
import marks_selector
import goal_setter
import grammar_checker
import calculator
import user_profile
import notes_mindmaps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- INITIAL ROOT SETUP (THE MAIN HUB) ---
orange_waves = tk.Tk()
orange_waves.title("ORANGE WAVES")
orange_waves.resizable(False, False)

hub_canvas = tk.Canvas(orange_waves, highlightthickness=0)
hub_canvas.pack(fill="both", expand=True)
hub_canvas.bind("<Configure>", lambda event: gui_components.draw_gradient(hub_canvas))

style_ow = ttk.Style(orange_waves)
style_ow.theme_use("clam")

hub_widgets = []


# --- AUTHENTICATION PORTAL GENERATOR ---
def build_auth_portal_directly():
    orange_waves.geometry("450x520+150+100")

    for widget in orange_waves.winfo_children():
        if widget != hub_canvas:
            widget.destroy()

    notebook = ttk.Notebook(orange_waves)
    notebook.place(x=30, y=40, width=390, height=440)

    login_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(login_tab, text="  Sign In  ")

    tk.Label(
        login_tab, text="🔑 USER SIGN IN",
        font=("Arial", 14, "bold"), bg="#ababab"
    ).pack(pady=25)

    tk.Label(
        login_tab, text="Username:", bg="#ababab",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=40)

    l_user = ttk.Entry(login_tab, width=32)
    l_user.pack(pady=5)

    tk.Label(
        login_tab, text="Password:", bg="#ababab",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=40)

    l_pass = ttk.Entry(login_tab, width=32, show="*")
    l_pass.pack(pady=5)

    def process_login():
        ok, msg = user_profile.login_user(l_user.get(), l_pass.get())
        if ok:
            messagebox.showinfo(
                "Success",
                f"Welcome back, {user_profile.get_logged_in_user()}!"
            )
            notebook.destroy()
            start_app_flow()
        else:
            messagebox.showerror(
                "Error",
                "Invalid username or password match parameters."
            )

    ttk.Button(
        login_tab,
        text="Secure Log In",
        command=process_login
    ).pack(pady=35, ipadx=40, ipady=8)

    signup_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(signup_tab, text="  Create Profile  ")

    tk.Label(
        signup_tab, text="📝 REGISTRATION PORTAL",
        font=("Arial", 14, "bold"), bg="#ababab"
    ).pack(pady=20)

    tk.Label(
        signup_tab, text="Choose Username:",
        bg="#ababab", font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=40)

    s_user = ttk.Entry(signup_tab, width=32)
    s_user.pack(pady=3)

    tk.Label(
        signup_tab, text="Account Gmail:",
        bg="#ababab", font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=40)

    s_mail = ttk.Entry(signup_tab, width=32)
    s_mail.pack(pady=3)

    tk.Label(
        signup_tab, text="Secure Password:",
        bg="#ababab", font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=40)

    s_pass = ttk.Entry(signup_tab, width=32, show="*")
    s_pass.pack(pady=3)

    def process_signup():
        ok, msg = user_profile.register_user(
            s_user.get(), s_mail.get(), s_pass.get()
        )
        if ok:
            messagebox.showinfo(
                "Success",
                "Account built! You can sign in now."
            )
            notebook.select(0)
        else:
            messagebox.showerror("Failed Registration", msg)

    ttk.Button(
        signup_tab,
        text="Complete Sign Up",
        command=process_signup
    ).pack(pady=25, ipadx=30, ipady=8)


# --- AUTHENTICATION INTERACTION HOOK PIPELINES ---
def start_app_flow():
    global hub_widgets

    # Expanded so the new Notes & Mind Maps row fits cleanly.
    orange_waves.geometry("782x540+50+50")

    hub_title = tk.Label(
        orange_waves,
        text="ORANGE WAVES SUITE",
        font=("Arial", 28, "bold"),
        fg="#fff",
        bg="#ffa6a6"
    )
    hub_title.place(relx=0.5, y=45, anchor="center")
    hub_widgets.append(hub_title)

    user = user_profile.get_logged_in_user()
    display_user = user.upper() if user else "UNKNOWN"

    hub_subtitle = tk.Label(
        orange_waves,
        text=f"Logged in workspace: active session for {display_user}",
        font=("Arial", 12, "italic"),
        fg="#fff",
        bg="#ffa6a6"
    )
    hub_subtitle.place(relx=0.5, y=88, anchor="center")
    hub_widgets.append(hub_subtitle)

    btn_profile = ttk.Button(
        orange_waves,
        text="👤 View User Profile",
        command=lambda: profile_window.open_profile_view(
            orange_waves, trigger_session_restart
        )
    )
    btn_profile.place(x=120, y=145, width=240, height=45)
    hub_widgets.append(btn_profile)

    btn_marks = ttk.Button(
        orange_waves,
        text="📊 Marks Calculator",
        command=lambda: marks_selector.open_marks_selector_window(
            orange_waves, open_main_window
        )
    )
    btn_marks.place(x=420, y=145, width=240, height=45)
    hub_widgets.append(btn_marks)

    btn_goals = ttk.Button(
        orange_waves,
        text="🎯 Goal & XP Setter",
        command=lambda: goal_setter.open_goal_setter(
            orange_waves,
            get_marks_summary_func=user_profile.get_saved_marks
        )
    )
    btn_goals.place(x=120, y=220, width=240, height=45)
    hub_widgets.append(btn_goals)

    btn_grammar = ttk.Button(
        orange_waves,
        text="✍️ Grammar Checker",
        command=lambda: grammar_checker.open_grammar_checker(orange_waves)
    )
    btn_grammar.place(x=420, y=220, width=240, height=45)
    hub_widgets.append(btn_grammar)

    btn_calculator = ttk.Button(
        orange_waves,
        text="🧮 Calculator",
        command=lambda: calculator.open_calculator(orange_waves)
    )
    btn_calculator.place(x=120, y=295, width=240, height=45)
    hub_widgets.append(btn_calculator)

    # NEW FEATURE: Notes & Mind Maps
    btn_notes_maps = ttk.Button(
        orange_waves,
        text="🧠 Notes & Mind Maps",
        command=lambda: notes_mindmaps.open_notes_mindmaps(orange_waves)
    )
    btn_notes_maps.place(x=420, y=295, width=240, height=45)
    hub_widgets.append(btn_notes_maps)

    # Small help text
    learning_hint = tk.Label(
        orange_waves,
        text="Create notes and mind maps — matching titles/subtopics connect automatically.",
        font=("Arial", 9, "italic"),
        fg="#fff",
        bg="#ffa6a6"
    )
    learning_hint.place(relx=0.5, y=385, anchor="center")
    hub_widgets.append(learning_hint)


def trigger_session_restart():
    global hub_widgets

    for widget in hub_widgets:
        widget.destroy()
    hub_widgets.clear()
    build_auth_portal_directly()


# --- MARKS PERFORMANCE CALCULATOR WINDOW RUNNER ---
def open_main_window(
    chosen_stream,
    num_subjects=4,
    split_marks=False,
    subjects_override=None
):
    orange_waves.withdraw()

    main = tk.Toplevel(orange_waves)
    main.title(f"Marks Performance Matrix - {chosen_stream.upper()}")
    main.config(bg="#ababab")

    window_height = max(460, 120 + (num_subjects * 45))
    window_width = 1080 if split_marks else 820

    main.geometry(f"{window_width}x{window_height}")
    main.geometry("+50+50")

    def on_close():
        main.destroy()
        orange_waves.deiconify()

    main.protocol("WM_DELETE_WINDOW", on_close)

    if subjects_override is not None:
        subjects = subjects_override
    elif chosen_stream == "Non High School Student":
        subjects = [f"Subject {i+1}" for i in range(num_subjects)]
    else:
        stream_subjects = {
            "Art": ["History", "Geography", "Pol Science", "English"],
            "Commerce": ["Accountancy", "Business Studies", "Economics", "English"],
            "Science": ["Physics", "Chemistry", "Mathematics", "English"]
        }
        subjects = stream_subjects.get(
            chosen_stream,
            ["Subject 1", "Subject 2", "Subject 3", "Subject 4"]
        )

    row_entries = []
    form_width = 680 if split_marks else 440

    container = tk.Frame(main, bg="#ababab")
    container.place(
        x=20, y=20,
        width=form_width,
        height=window_height - 90
    )

    form_frame = tk.LabelFrame(
        container,
        text=f" Input Marks ({chosen_stream}) ",
        bg="#ababab",
        fg="#000",
        font=("Arial", 11, "bold")
    )
    form_frame.pack(fill="both", expand=True)

    tk.Label(
        form_frame, text="Subject Name",
        bg="#ababab", font=("Arial", 10, "bold")
    ).grid(row=0, column=0, padx=8, pady=5, sticky="w")

    if split_marks:
        headings = [
            "Project\nTotal", "Project\nObtained",
            "Assessment\nTotal", "Assessment\nObtained",
            "Exam\nTotal", "Exam\nObtained"
        ]
        for col, heading in enumerate(headings, start=1):
            tk.Label(
                form_frame,
                text=heading,
                bg="#ababab",
                font=("Arial", 9, "bold")
            ).grid(row=0, column=col, padx=5, pady=5)
    else:
        tk.Label(
            form_frame, text="Total Marks",
            bg="#ababab", font=("Arial", 10, "bold")
        ).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(
            form_frame, text="Obtained Marks",
            bg="#ababab", font=("Arial", 10, "bold")
        ).grid(row=0, column=2, padx=10, pady=5)

    for idx, sub in enumerate(subjects):
        tk.Label(
            form_frame, text=sub,
            bg="#ababab", font=("Arial", 10)
        ).grid(
            row=idx + 1, column=0,
            padx=8, pady=8, sticky="w"
        )

        if split_marks:
            entries = {}

            for key, default, col in [
                ("proj_total", "20", 1),
                ("proj_obtained", "0", 2),
                ("assess_total", "10", 3),
                ("assess_obtained", "0", 4),
                ("exam_total", "70", 5),
                ("exam_obtained", "0", 6),
            ]:
                entry = ttk.Entry(
                    form_frame, width=6, justify="center"
                )
                entry.grid(
                    row=idx + 1,
                    column=col,
                    padx=5,
                    pady=8
                )
                entry.insert(0, default)
                entries[key] = entry

            row_entries.append(entries)

        else:
            total_entry = ttk.Entry(
                form_frame, width=10, justify="center"
            )
            total_entry.grid(
                row=idx + 1, column=1,
                padx=10, pady=8
            )
            total_entry.insert(0, "100")

            obtained_entry = ttk.Entry(
                form_frame, width=10, justify="center"
            )
            obtained_entry.grid(
                row=idx + 1, column=2,
                padx=10, pady=8
            )
            obtained_entry.insert(0, "0")

            row_entries.append({
                "total": total_entry,
                "obtained": obtained_entry,
            })

    results_container = tk.Frame(main, bg="#ababab")
    results_container.place(
        x=form_width + 40,
        y=20,
        width=window_width - form_width - 60,
        height=window_height - 90
    )

    results_frame = tk.LabelFrame(
        results_container,
        text=" 📈 Performance Results ",
        bg="#ababab",
        fg="#000",
        font=("Arial", 11, "bold")
    )
    results_frame.pack(fill="both", expand=True)

    gauge_canvas = tk.Canvas(
        results_frame,
        bg="#ffffff",
        highlightthickness=0
    )
    gauge_canvas.pack(
        fill="both", expand=True,
        padx=15, pady=15
    )

    summary_lbl = tk.Label(
        results_frame,
        text="Enter marks and press Calculate",
        font=("Arial", 10, "italic"),
        bg="#ababab",
        fg="#555"
    )
    summary_lbl.pack(pady=(0, 10))

    last_calculated = {"subject_marks": None}

    def redraw_gauge(percentage):
        gauge_canvas.update_idletasks()
        gui_components.draw_gauge(
            gauge_canvas,
            percentage,
            label=chosen_stream
        )

    def run_calculation():
        total_obtained, max_possible, percentage = (
            app_logic.process_marks_summary(
                row_entries, split_marks
            )
        )
        subject_marks = app_logic.build_per_subject_marks(
            row_entries, subjects, split_marks
        )
        last_calculated["subject_marks"] = subject_marks

        summary_lbl.config(
            text=(
                f"Total: {total_obtained:.2f} / "
                f"{max_possible:.2f}  •  "
                f"Overall: {percentage:.1f}%"
            )
        )
        redraw_gauge(percentage)

    def save_to_profile():
        if not last_calculated["subject_marks"]:
            messagebox.showwarning(
                "Nothing to Save",
                "Please press Calculate before saving results to your profile."
            )
            return

        user_profile.save_calculated_marks(
            last_calculated["subject_marks"]
        )
        messagebox.showinfo(
            "Saved",
            "Your results have been linked to your profile.\n"
            "Check the Goal & XP Setter's 'Auto-Build From Marks' option!"
        )

    button_bar = tk.Frame(main, bg="#ababab")
    button_bar.place(
        x=20, y=window_height - 60,
        width=window_width - 40, height=40
    )

    ttk.Button(
        button_bar,
        text="🧮 Calculate",
        command=run_calculation
    ).place(x=0, y=0, width=150, height=35)

    ttk.Button(
        button_bar,
        text="💾 Save to Profile",
        command=save_to_profile
    ).place(x=160, y=0, width=170, height=35)

    ttk.Button(
        button_bar,
        text="⬅ Back to Hub",
        command=on_close
    ).place(
        relx=1.0, x=-150, y=0,
        width=150, height=35, anchor="ne"
    )


# --- APP BOOTSTRAP ---
# profile_window is imported here to keep the startup imports clean.
import profile_window

build_auth_portal_directly()
orange_waves.mainloop()
