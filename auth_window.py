import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import user_profile

def build_auth_portal(parent_window, on_success_callback):
    """Builds the login and sign-up panels directly onto the root canvas frame securely."""
    # Temporarily set window parameters for a compact login layout
    parent_window.geometry("450x520+150+100")
    parent_window.deiconify()
    
    # Clear any previous widget traces from past sessions
    for widget in parent_window.winfo_children():
        if isinstance(widget, ttk.Notebook) or isinstance(widget, tk.Label):
            widget.destroy()

    notebook = ttk.Notebook(parent_window)
    notebook.place(x=30, y=40, width=390, height=440)
    
    # --- TAB 1: LOGIN INTERFACE FRAME ---
    login_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(login_tab, text="  Sign In  ")
    
    tk.Label(login_tab, text="🔑 USER SIGN IN", font=("Arial", 14, "bold"), bg="#ababab").pack(pady=25)
    
    tk.Label(login_tab, text="Username:", bg="#ababab", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
    l_user = ttk.Entry(login_tab, width=32)
    l_user.pack(pady=5)
    
    tk.Label(login_tab, text="Password:", bg="#ababab", font=("Arial", 10, "bold")).pack(anchor="w", padx=40)
    l_pass = ttk.Entry(login_tab, width=32, show="*")
    l_pass.pack(pady=5)
    
    def process_login():
        ok, msg = user_profile.login_user(l_user.get(), l_pass.get())
        if ok:
            messagebox.showinfo("Success", f"Welcome back, {user_profile.get_logged_in_user()}!")
            notebook.destroy() # Clear out login layout cleanly
            on_success_callback()
        else:
            messagebox.showerror("Error", "Invalid username or password match parameters.")
            
    ttk.Button(login_tab, text="Secure Log In", command=process_login).pack(pady=35, width=180, height=35)
    
    # --- TAB 2: SIGN UP INTERFACE FRAME ---
    signup_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(signup_tab, text="  Create Profile  ")
    
    tk.Label(signup_tab, text="📝 REGISTRATION PORTAL", font=("Arial", 14, "bold"), bg="#ababab").pack(pady=20)
    
    tk.Label(signup_tab, text="Choose Username:", bg="#ababab", font=("Arial", 9, "bold")).pack(anchor="w", padx=40)
    s_user = ttk.Entry(signup_tab, width=32)
    s_user.pack(pady=3)
    
    tk.Label(signup_tab, text="Account Gmail:", bg="#ababab", font=("Arial", 9, "bold")).pack(anchor="w", padx=40)
    s_mail = ttk.Entry(signup_tab, width=32)
    s_mail.pack(pady=3)
    
    tk.Label(signup_tab, text="Secure Password:", bg="#ababab", font=("Arial", 9, "bold")).pack(anchor="w", padx=40)
    s_pass = ttk.Entry(signup_tab, width=32, show="*")
    s_pass.pack(pady=3)
    
    def process_signup():
        ok, msg = user_profile.register_user(s_user.get(), s_mail.get(), s_pass.get())
        if ok:
            messagebox.showinfo("Success", "Account built! You can sign in now.")
            notebook.select(0) # Swap back visually to login panel
        else:
            messagebox.showerror("Failed Registration", msg)
            
    ttk.Button(signup_tab, text="Complete Sign Up", command=process_signup).pack(pady=25, width=180, height=35)
