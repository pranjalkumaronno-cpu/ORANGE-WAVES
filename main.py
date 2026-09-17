import os 
import tkinter as tk 
from tkinter import ttk 
from tkinter import messagebox
 
try: 
    from PIL import Image, ImageTk 
    HAS_PIL = True 
except ImportError: 
    HAS_PIL = False 
 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
 
# --- INITIAL ROOT SETUP --- 
orange_waves = tk.Tk() 
orange_waves.title("ORANGE WAVES") 
orange_waves.geometry("782x441") 
 
bg_canvas = tk.Canvas(orange_waves, highlightthickness=0) 
bg_canvas.pack(fill="both", expand=True) 
 
def draw_gradient(canvas): 
    width = canvas.winfo_width() 
    height = canvas.winfo_height() 
    if width <= 1 or height <= 1: 
        return 
    canvas.delete("all") 
    r1, g1, b1 = 255, 166, 166 
    r2, g2, b2 = 102, 1, 1 
    for y in range(height): 
        ratio = y / height 
        r = int(r1 + (r2 - r1) * ratio) 
        g = int(g1 + (g2 - g1) * ratio) 
        b = int(b1 + (b2 - b1) * ratio) 
        color = f"#{r:02x}{g:02x}{b:02x}" 
        canvas.create_line(0, y, width, y, fill=color) 
 
bg_canvas.bind("<Configure>", lambda event: draw_gradient(bg_canvas)) 
orange_waves.update_idletasks() 
orange_waves.geometry("+50+50") 
 
if HAS_PIL: 
    try: 
        icon_path = os.path.join(BASE_DIR, "assets", "images", "orange waves logo.png") 
        orange_waves_img = Image.open(icon_path) 
        orange_waves_img = ImageTk.PhotoImage(orange_waves_img) 
        orange_waves.iconphoto(False, orange_waves_img) 
    except Exception: 
        pass 
 
style_ow = ttk.Style(orange_waves) 
style_ow.theme_use("clam") 
 
 
# --- STEP 3: MAIN DYNAMIC CALCULATOR & GRAPHING APPLICATION --- 
def open_main_window(chosen_stream, num_subjects=4, split_marks=False, subjects_override=None): 
    orange_waves.withdraw() 
    
    main = tk.Toplevel(orange_waves) 
    main.title(f"Marks Performance Matrix - {chosen_stream.upper()}") 
    main.config(bg="#ababab") 
    
    # Dynamically expand window height if there are many subjects
    window_height = max(460, 120 + (num_subjects * 45))
    # Splitting into project/assessment/exam needs more horizontal room for the extra columns
    window_width = 1080 if split_marks else 820
    main.geometry(f"{window_width}x{window_height}") 
    main.geometry("+50+50") 
    
    def on_close(): 
        main.destroy() 
        orange_waves.deiconify() 
        
    main.protocol("WM_DELETE_WINDOW", on_close) 
    
    # Build the subject list based on selection
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
        subjects = stream_subjects.get(chosen_stream, ["Subject 1", "Subject 2", "Subject 3", "Subject 4"])
    
    # Each entry in row_entries is a dict of the fields relevant to that row.
    # Non-split:  {'total': Entry, 'obtained': Entry}
    # Split:      {'proj_total': Entry, 'proj_obtained': Entry,
    #              'assess_total': Entry, 'assess_obtained': Entry,
    #              'exam_total': Entry, 'exam_obtained': Entry}
    row_entries = []
    
    # Wrap standard layout in a canvas with a scrollbar in case user adds tons of subjects
    form_width = 680 if split_marks else 440
    container = tk.Frame(main, bg="#ababab")
    container.place(x=20, y=20, width=form_width, height=window_height - 90)
    
    form_frame = tk.LabelFrame(container, text=f" Input Marks ({chosen_stream}) ", bg="#ababab", fg="#000", font=("Arial", 11, "bold"))
    form_frame.pack(fill="both", expand=True)
    
    tk.Label(form_frame, text="Subject Name", bg="#ababab", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=8, pady=5, sticky="w")
    
    if split_marks:
        tk.Label(form_frame, text="Project\nTotal", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Project\nObtained", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(form_frame, text="Assessment\nTotal", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Assessment\nObtained", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=4, padx=5, pady=5)
        tk.Label(form_frame, text="Exam\nTotal", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=5, padx=5, pady=5)
        tk.Label(form_frame, text="Exam\nObtained", bg="#ababab", font=("Arial", 9, "bold")).grid(row=0, column=6, padx=5, pady=5)
    else:
        tk.Label(form_frame, text="Total Marks", bg="#ababab", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(form_frame, text="Obtained Marks", bg="#ababab", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10, pady=5)
    
    for idx, sub in enumerate(subjects):
        tk.Label(form_frame, text=sub, bg="#ababab", font=("Arial", 10)).grid(row=idx+1, column=0, padx=8, pady=8, sticky="w")
        
        if split_marks:
            proj_total_entry = ttk.Entry(form_frame, width=6, justify="center")
            proj_total_entry.grid(row=idx+1, column=1, padx=5, pady=8)
            proj_total_entry.insert(0, "20")
            
            proj_obt_entry = ttk.Entry(form_frame, width=6, justify="center")
            proj_obt_entry.grid(row=idx+1, column=2, padx=5, pady=8)
            proj_obt_entry.insert(0, "0")
            
            assess_total_entry = ttk.Entry(form_frame, width=6, justify="center")
            assess_total_entry.grid(row=idx+1, column=3, padx=5, pady=8)
            assess_total_entry.insert(0, "10")
            
            assess_obt_entry = ttk.Entry(form_frame, width=6, justify="center")
            assess_obt_entry.grid(row=idx+1, column=4, padx=5, pady=8)
            assess_obt_entry.insert(0, "0")
            
            exam_total_entry = ttk.Entry(form_frame, width=6, justify="center")
            exam_total_entry.grid(row=idx+1, column=5, padx=5, pady=8)
            exam_total_entry.insert(0, "70")
            
            exam_obt_entry = ttk.Entry(form_frame, width=6, justify="center")
            exam_obt_entry.grid(row=idx+1, column=6, padx=5, pady=8)
            exam_obt_entry.insert(0, "0")
            
            row_entries.append({
                "proj_total": proj_total_entry,
                "proj_obtained": proj_obt_entry,
                "assess_total": assess_total_entry,
                "assess_obtained": assess_obt_entry,
                "exam_total": exam_total_entry,
                "exam_obtained": exam_obt_entry,
            })
        else:
            total_entry = ttk.Entry(form_frame, width=8, justify="center")
            total_entry.grid(row=idx+1, column=1, padx=10, pady=8)
            total_entry.insert(0, "100")
            
            obt_entry = ttk.Entry(form_frame, width=8, justify="center")
            obt_entry.grid(row=idx+1, column=2, padx=10, pady=8)
            obt_entry.insert(0, "0")
            
            row_entries.append({
                "total": total_entry,
                "obtained": obt_entry,
            })
 
    chart_x = 720 if split_marks else 480
    chart_width = 340 if split_marks else 310
    chart_canvas = tk.Canvas(main, bg="#E4E2E2", highlightthickness=1, highlightbackground="#000") 
    chart_canvas.place(x=chart_x, y=30, width=chart_width, height=340) 
 
    def _safe_float(entry):
        raw = entry.get()
        try:
            return float(raw) if raw else 0.0
        except ValueError:
            return 0.0
 
    def calculate_and_draw():
        chart_canvas.delete("gauge_elements")
        
        total_obtained = 0.0
        max_possible = 0.0
        
        for row in row_entries:
            try:
                if split_marks:
                    proj_total = max(_safe_float(row["proj_total"]), 0)
                    assess_total = max(_safe_float(row["assess_total"]), 0)
                    exam_total = max(_safe_float(row["exam_total"]), 0)
                    proj_obt = min(max(_safe_float(row["proj_obtained"]), 0), proj_total)
                    assess_obt = min(max(_safe_float(row["assess_obtained"]), 0), assess_total)
                    exam_obt = min(max(_safe_float(row["exam_obtained"]), 0), exam_total)
                    max_possible += (proj_total + assess_total + exam_total)
                    total_obtained += (proj_obt + assess_obt + exam_obt)
                else:
                    subj_total = max(_safe_float(row["total"]), 0)
                    obtained = min(max(_safe_float(row["obtained"]), 0), subj_total)
                    max_possible += subj_total
                    total_obtained += obtained
            except ValueError:
                pass 
        
        percentage = (total_obtained / max_possible) * 100 if max_possible > 0 else 0
        
        result_lbl.config(text=f"Aggregate Score: {total_obtained:.1f} / {max_possible:.1f} ({percentage:.2f}%)")
        
        chart_canvas.create_text(chart_width // 2, 30, text="TOTAL PERFORMANCE CHART", fill="#000", font=("Arial", 11, "bold"), tags="gauge_elements")
        chart_canvas.create_rectangle(60, 80, 100, 280, fill="#d0d0d0", outline="#777", tags="gauge_elements")
        
        pixel_height = (percentage / 100) * 200
        y_top = 280 - pixel_height
        
        bar_color = "#e66767" if percentage < 40 else "#f5cd79" if percentage < 75 else "#3dc1d3"
        
        if pixel_height > 0:
            chart_canvas.create_rectangle(60, y_top, 100, 280, fill=bar_color, outline="", tags="gauge_elements")
            
        chart_canvas.create_text(140, y_top if y_top < 270 else 270, text=f"{percentage:.1f}%", fill="#000", font=("Arial", 12, "bold"), anchor="w", tags="gauge_elements")
        chart_canvas.create_text(35, 80, text="100%", fill="#555", font=("Arial", 8), tags="gauge_elements")
        chart_canvas.create_text(35, 180, text="50%", fill="#555", font=("Arial", 8), tags="gauge_elements")
        chart_canvas.create_text(35, 280, text="0%", fill="#555", font=("Arial", 8), tags="gauge_elements")
 
    btn_calc = ttk.Button(main, text="CALCULATE PERFORMANCE GRAPH", command=calculate_and_draw)
    btn_calc.place(x=20, y=window_height - 60, width=form_width, height=45)
    
    result_lbl = tk.Label(main, text="Aggregate Score: 0.0 / 0.0 (0.00%)", bg="#ababab", fg="#000", font=("Arial", 12, "bold"))
    result_lbl.place(x=chart_x, y=window_height - 55, width=chart_width)
    
    calculate_and_draw()
 
 
# --- STEP 2: STREAM SELECTION POPUP WITH DYNAMIC INPUT CONFIGURATION --- 
def open_selection_window(): 
    select_win = tk.Toplevel(orange_waves) 
    select_win.title("Select Your Stream") 
    select_win.geometry("380x420") 
    select_win.config(bg="#545454") 
    select_win.geometry("+200+150") 
    select_win.resizable(False, False) 
    
    def handle_selection(stream): 
        split = split_marks_var.get()
        if stream == "Non High School Student":
            try:
                count = int(num_subs_entry.get())
                if count <= 0:
                    raise ValueError
                select_win.destroy() 
                open_main_window(stream, num_subjects=count, split_marks=split)
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid positive number of subjects.")
        else:
            select_win.destroy() 
            open_main_window(stream, split_marks=split) 
 
    label = tk.Label(select_win, text="CHOOSE YOUR CATEGORY", bg="#545454", fg="#ffffff", font=("Courier", 12, "bold")) 
    label.pack(pady=10) 
 
    # Dynamic Entry configuration for Custom Number of Subjects
    non_hs_frame = tk.Frame(select_win, bg="#444444", bd=1, relief="solid")
    non_hs_frame.pack(fill="x", padx=30, pady=5)
    
    lbl_count = tk.Label(non_hs_frame, text="For Non High School Status:\nEnter No. of Subjects:", bg="#444444", fg="#fff", font=("Arial", 9))
    lbl_count.pack(side="left", padx=5, pady=5)
    
    num_subs_entry = ttk.Entry(non_hs_frame, width=5, justify="center")
    num_subs_entry.pack(side="right", padx=10, pady=5)
    num_subs_entry.insert(0, "5") # Default placeholder value
 
    # --- Total Marks / Project+Exam split toggle ---
    split_frame = tk.Frame(select_win, bg="#444444", bd=1, relief="solid")
    split_frame.pack(fill="x", padx=30, pady=8)
 
    split_marks_var = tk.BooleanVar(value=False)
    split_check = tk.Checkbutton(
        split_frame,
        text="Add Project / Assessment / External marks separately?\n(otherwise just enter Total & Obtained marks)",
        variable=split_marks_var,
        bg="#444444", fg="#fff", selectcolor="#333333",
        activebackground="#444444", activeforeground="#fff",
        font=("Arial", 9), justify="left", anchor="w",
        wraplength=300,
    )
    split_check.pack(padx=5, pady=5, anchor="w")
 
    def handle_science_selection():
        split = split_marks_var.get()
 
        sci_win = tk.Toplevel(select_win)
        sci_win.title("Science - Choose Your Subjects")
        sci_win.geometry("300x260")
        sci_win.config(bg="#545454")
        sci_win.resizable(False, False)
        sci_win.geometry("+220+180")
 
        tk.Label(sci_win, text="Which subjects do you have?", bg="#545454", fg="#fff",
                 font=("Arial", 10, "bold"), wraplength=260).pack(pady=(15, 5))
        tk.Label(sci_win, text="(Chemistry & English are included by default)", bg="#545454",
                 fg="#cccccc", font=("Arial", 8), wraplength=260).pack(pady=(0, 10))
 
        phy_var = tk.BooleanVar(value=True)
        maths_var = tk.BooleanVar(value=False)
        bio_var = tk.BooleanVar(value=False)
 
        for label, var in (("Physics", phy_var), ("Maths", maths_var), ("Biology", bio_var)):
            tk.Checkbutton(
                sci_win, text=label, variable=var,
                bg="#545454", fg="#fff", selectcolor="#333333",
                activebackground="#545454", activeforeground="#fff",
                font=("Arial", 10), anchor="w",
            ).pack(fill="x", padx=40, pady=3)
 
        def confirm_science():
            chosen = []
            if phy_var.get():
                chosen.append("Physics")
            chosen.append("Chemistry")
            if maths_var.get():
                chosen.append("Maths")
            if bio_var.get():
                chosen.append("Biology")
            chosen.append("English")
 
            if not (phy_var.get() or maths_var.get() or bio_var.get()):
                messagebox.showerror("Invalid Input", "Please select at least one of Physics, Maths or Biology.")
                return
 
            sci_win.destroy()
            select_win.destroy()
            open_main_window("Science", subjects_override=chosen, split_marks=split)
 
        ttk.Button(sci_win, text="CONTINUE", style="r.TButton", command=confirm_science).pack(pady=15, padx=40, fill="x")
 
    streams = ["Art", "Commerce", "Science", "Non High School Student"] 
    for stream in streams: 
        # Apply specific logic style visual indicator separation
        btn_style = "r.TButton"
        if stream == "Science":
            command = handle_science_selection
        else:
            command = lambda s=stream: handle_selection(s)
        btn = ttk.Button( 
            select_win, 
            text=stream, 
            style=btn_style, 
            command=command
        ) 
        btn.pack(fill="x", padx=30, pady=5) 
 
 
# --- BUTTON LAYOUT MAPPINGS --- 
style_ow.configure("r.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 11, "bold"), cursor="arrow") 
style_ow.map("r.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")]) 
 
r = ttk.Button(master=orange_waves, text="MARKS \n CALCULATOR", style="r.TButton", command=open_selection_window) 
r.place(x=50, y=55, width=151, height=57) 
 
style_ow.configure("b.TButton", background="#545454", foreground="#ffffff", borderwidth=3, relief=tk.RAISED, font=("Courier", 11, "bold"), cursor="arrow") 
style_ow.map("b.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")]) 
b = ttk.Button(master=orange_waves, text="GOALS SETTER", style="b.TButton") 
b.place(x=230, y=55, width=151, height=57) 
 
style_ow.configure("b1.TButton", background="#545454", foreground="#ffffff", borderwidth=3, font=("Courier", 11, "bold"), cursor="arrow") 
style_ow.map("b1.TButton", background=[("active", "#000000")], foreground=[("active", "#ff8080")]) 
b1 = ttk.Button(master=orange_waves, text="CALCULATOR", style="b1.TButton") 
b1.place(x=418, y=55, width=151, height=57) 
 
orange_waves.mainloop()


    







    

    










 
