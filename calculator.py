import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import ast
import math
import operator

# --- SAFE EXPRESSION EVALUATION ---
# We deliberately avoid Python's built-in eval() here. eval() on raw user
# keystrokes would let someone type things like "__import__('os').system(...)"
# into the calculator and execute arbitrary code. Instead we parse the
# expression into an AST ourselves and only ever evaluate node types and
# function names we've explicitly whitelisted below.

_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}

_ALLOWED_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_ALLOWED_FUNCS = {
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x)),
    "asin": lambda x: math.degrees(math.asin(x)),
    "acos": lambda x: math.degrees(math.acos(x)),
    "atan": lambda x: math.degrees(math.atan(x)),
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "exp": math.exp,
    "abs": abs,
    "factorial": lambda x: math.factorial(int(x)),
}

_ALLOWED_CONSTS = {
    "pi": math.pi,
    "e": math.e,
}


class CalcError(Exception):
    pass


def safe_eval(expr):
    """Safely evaluates a restricted arithmetic/scientific expression."""
    expr = expr.strip()
    if not expr:
        raise CalcError("Empty expression")
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError:
        raise CalcError("Invalid expression")
    return _eval_node(node)


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalcError("Invalid literal")
    if isinstance(node, ast.BinOp):
        op_func = _ALLOWED_BINOPS.get(type(node.op))
        if not op_func:
            raise CalcError("Operator not allowed")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        try:
            return op_func(left, right)
        except ZeroDivisionError:
            raise CalcError("Division by zero")
    if isinstance(node, ast.UnaryOp):
        op_func = _ALLOWED_UNARYOPS.get(type(node.op))
        if not op_func:
            raise CalcError("Operator not allowed")
        return op_func(_eval_node(node.operand))
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise CalcError("Function not allowed")
        if node.keywords:
            raise CalcError("Keyword arguments not allowed")
        args = [_eval_node(a) for a in node.args]
        try:
            return _ALLOWED_FUNCS[node.func.id](*args)
        except ValueError:
            raise CalcError("Math domain error")
        except OverflowError:
            raise CalcError("Result too large")
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        raise CalcError(f"Unknown identifier '{node.id}'")
    raise CalcError("Expression not allowed")


def _format_result(value):
    if isinstance(value, float):
        if math.isinf(value) or math.isnan(value):
            raise CalcError("Result is undefined")
        if value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


# --- GUI ---

def open_calculator(parent_window):
    parent_window.withdraw()
    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - Calculator")
    window.geometry("420x600+150+70")
    window.resizable(False, False)
    window.config(bg="#ababab")

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text="🧮 Calculator", font=("Arial", 16, "bold"), bg="#ababab").pack(pady=(12, 5))

    notebook = ttk.Notebook(window)
    notebook.pack(padx=10, pady=5, fill="both", expand=True)

    simple_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(simple_tab, text="  Simple  ")
    _build_simple_calculator(simple_tab)

    complex_tab = tk.Frame(notebook, bg="#ababab")
    notebook.add(complex_tab, text="  Complex / Scientific  ")
    _build_complex_calculator(complex_tab)

    ttk.Button(window, text="⬅ Back to Hub", command=on_close).pack(pady=10)


def _make_display(parent):
    display_var = tk.StringVar(value="")
    display = ttk.Entry(parent, textvariable=display_var, font=("Arial", 20), justify="right")
    display.pack(fill="x", padx=10, pady=(10, 8), ipady=8)
    return display_var


def _build_simple_calculator(parent):
    display_var = _make_display(parent)

    def press(chars):
        display_var.set(display_var.get() + chars)

    def clear():
        display_var.set("")

    def backspace():
        display_var.set(display_var.get()[:-1])

    def equals():
        expr = display_var.get()
        try:
            result = safe_eval(expr)
            display_var.set(_format_result(result))
        except CalcError as e:
            messagebox.showerror("Calculation Error", str(e))
        except Exception:
            messagebox.showerror("Calculation Error", "Invalid expression")

    grid_frame = tk.Frame(parent, bg="#ababab")
    grid_frame.pack(padx=10, pady=5)

    # (label shown on button, text actually inserted, or a command)
    layout = [
        [("C", None, clear), ("⌫", None, backspace), ("(", "(", None), (")", ")", None)],
        [("7", "7", None), ("8", "8", None), ("9", "9", None), ("÷", "/", None)],
        [("4", "4", None), ("5", "5", None), ("6", "6", None), ("×", "*", None)],
        [("1", "1", None), ("2", "2", None), ("3", "3", None), ("-", "-", None)],
        [("0", "0", None), (".", ".", None), ("=", None, equals), ("+", "+", None)],
    ]

    for r, row in enumerate(layout):
        for c, (label, insert_text, cmd) in enumerate(row):
            action = cmd if cmd else (lambda t=insert_text: press(t))
            btn = ttk.Button(grid_frame, text=label, command=action)
            btn.grid(row=r, column=c, padx=4, pady=4, ipadx=10, ipady=14, sticky="nsew")

    for c in range(4):
        grid_frame.grid_columnconfigure(c, weight=1)


def _build_complex_calculator(parent):
    display_var = _make_display(parent)

    def press(chars):
        display_var.set(display_var.get() + chars)

    def clear():
        display_var.set("")

    def backspace():
        display_var.set(display_var.get()[:-1])

    def wrap_func(name):
        """Wraps the current display in func(...) — e.g. '45' -> 'sqrt(45)'.
        If the display is empty, just starts typing the function call instead,
        so users can also build nested expressions manually."""
        def _inner():
            current = display_var.get()
            if current == "":
                press(f"{name}(")
            else:
                display_var.set(f"{name}({current})")
        return _inner

    def square():
        current = display_var.get()
        if current:
            display_var.set(f"({current})**2")

    def reciprocal():
        current = display_var.get()
        if current:
            display_var.set(f"1/({current})")

    def equals():
        expr = display_var.get()
        try:
            result = safe_eval(expr)
            display_var.set(_format_result(result))
        except CalcError as e:
            messagebox.showerror("Calculation Error", str(e))
        except Exception:
            messagebox.showerror("Calculation Error", "Invalid expression")

    grid_frame = tk.Frame(parent, bg="#ababab")
    grid_frame.pack(padx=10, pady=5)

    layout = [
        [("sin", wrap_func("sin")), ("cos", wrap_func("cos")), ("tan", wrap_func("tan")), ("√", wrap_func("sqrt")), ("^", lambda: press("**"))],
        [("asin", wrap_func("asin")), ("acos", wrap_func("acos")), ("atan", wrap_func("atan")), ("log", wrap_func("log")), ("ln", wrap_func("ln"))],
        [("C", clear), ("⌫", backspace), ("(", lambda: press("(")), (")", lambda: press(")")), ("%", lambda: press("%"))],
        [("7", lambda: press("7")), ("8", lambda: press("8")), ("9", lambda: press("9")), ("÷", lambda: press("/")), ("π", lambda: press("pi"))],
        [("4", lambda: press("4")), ("5", lambda: press("5")), ("6", lambda: press("6")), ("×", lambda: press("*")), ("e", lambda: press("e"))],
        [("1", lambda: press("1")), ("2", lambda: press("2")), ("3", lambda: press("3")), ("-", lambda: press("-")), ("x²", square)],
        [("0", lambda: press("0")), (".", lambda: press(".")), ("=", equals), ("+", lambda: press("+")), ("1/x", reciprocal)],
    ]

    for r, row in enumerate(layout):
        for c, (label, cmd) in enumerate(row):
            btn = ttk.Button(grid_frame, text=label, command=cmd)
            btn.grid(row=r, column=c, padx=3, pady=3, ipadx=4, ipady=8, sticky="nsew")

    for c in range(5):
        grid_frame.grid_columnconfigure(c, weight=1)

    tk.Label(
        parent,
        text="Trig functions use degrees. Tip: type or wrap a value, then press a\nfunction button — e.g. enter 45 then press √ to get sqrt(45).",
        font=("Arial", 8, "italic"), bg="#ababab", fg="#444", justify="left"
    ).pack(pady=(4, 0), padx=10, anchor="w")