import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# --- SETUP NOTE ---
# This module uses the free LanguageTool grammar/spelling/punctuation engine
# through the 'language_tool_python' package. It needs to be installed once:
#
#     pip install language_tool_python
#
# There are two ways this can talk to LanguageTool:
#
#   USE_LOCAL_SERVER = True  (the active setting below)
#     Runs LanguageTool as a local server on your own machine instead of a
#     shared public one. No rate limit at all, and no internet needed after
#     the one-time setup. Requires:
#       1. Java installed (Java 8+; check with `java -version` in a terminal).
#          If missing, install a JRE from https://adoptium.net/
#       2. The FIRST time this runs, language_tool_python downloads the
#          LanguageTool engine (~200MB) automatically — that one download
#          does need internet, and can take a minute or two, plus the local
#          server itself takes a few seconds to spin up on each app launch.
#     After that first download, everything runs fully offline and instantly.
#
#   USE_LOCAL_SERVER = False
#     Uses LanguageTool's public web API instead. No Java required, but it's
#     shared by everyone on the internet and rate-limited (~20 requests/min,
#     sometimes less if your network's IP is busy) — this is what was
#     triggering the "rate limit reached" errors.

USE_LOCAL_SERVER = True

try:
    import language_tool_python
    _LT_AVAILABLE = True
except ImportError:
    _LT_AVAILABLE = False

_tool_cache = {"tool": None}


def _get_tool():
    """Lazily creates a single shared LanguageTool client for the app's lifetime."""
    if _tool_cache["tool"] is None:
        if USE_LOCAL_SERVER:
            _tool_cache["tool"] = language_tool_python.LanguageTool("en-US")
        else:
            _tool_cache["tool"] = language_tool_python.LanguageToolPublicAPI("en-US")
    return _tool_cache["tool"]


def _is_rate_limit_error(exc):
    text = str(exc).lower()
    return "rate limit" in text or "429" in text or "too many requests" in text


def _rep_text(replacement):
    """A 'replacement' from the API can be a dict like {'value': 'word'} or a plain string."""
    if isinstance(replacement, dict):
        return replacement.get("value", "")
    return str(replacement)


def _classify(match):
    """Buckets a LanguageTool match into one of our highlight categories."""
    category = (getattr(match, "category", "") or "").upper()
    issue_type = (getattr(match, "ruleIssueType", "") or "").lower()

    if "MISSPELL" in category or "TYPOS" in category or issue_type == "misspelling":
        return "err_spelling"
    if "PUNCTUATION" in category:
        return "err_punctuation"
    if issue_type == "grammar" or "GRAMMAR" in category:
        return "err_grammar"
    return "err_style"


_TAG_COLORS = {
    "err_spelling": {"foreground": "#b02c2c", "underline": True},
    "err_punctuation": {"foreground": "#1d5fa8", "underline": True},
    "err_grammar": {"foreground": "#c07a00", "underline": True},
    "err_style": {"foreground": "#6a3fa0", "underline": True},
}

_LEGEND = [
    ("err_spelling", "Spelling"),
    ("err_grammar", "Grammar"),
    ("err_punctuation", "Punctuation"),
    ("err_style", "Style / Other"),
]


def open_grammar_checker(parent_window):
    parent_window.withdraw()
    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - Grammar Checker")
    window.geometry("760x760+80+30")
    window.resizable(False, False)
    window.config(bg="#ababab")

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(window, text="✍️ Grammar, Spelling & Punctuation Checker", font=("Arial", 18, "bold"), bg="#ababab").pack(pady=(15, 5))
    tk.Label(window, text="Type or paste your essay below, then run a check.", font=("Arial", 10), bg="#ababab", fg="#333").pack(pady=(0, 10))

    if not _LT_AVAILABLE:
        tk.Label(
            window,
            text="⚠ The 'language_tool_python' package isn't installed.\nRun:  pip install language_tool_python   then restart the app.",
            font=("Arial", 10, "bold"), bg="#ffe1e1", fg="#802323", justify="left", padx=10, pady=8
        ).pack(fill="x", padx=20, pady=(0, 10))

    # --- ESSAY INPUT ---
    input_frame = tk.Frame(window, bg="#ababab")
    input_frame.pack(fill="both", expand=False, padx=20)

    essay_text = tk.Text(input_frame, height=12, wrap="word", font=("Arial", 11), undo=True)
    essay_scroll = ttk.Scrollbar(input_frame, orient="vertical", command=essay_text.yview)
    essay_text.config(yscrollcommand=essay_scroll.set)
    essay_text.pack(side="left", fill="both", expand=True)
    essay_scroll.pack(side="right", fill="y")

    for tag, cfg in _TAG_COLORS.items():
        essay_text.tag_config(tag, **cfg)

    # --- LEGEND ---
    legend_frame = tk.Frame(window, bg="#ababab")
    legend_frame.pack(fill="x", padx=20, pady=(6, 0))
    for tag, label in _LEGEND:
        swatch = tk.Label(legend_frame, text="■", fg=_TAG_COLORS[tag]["foreground"], bg="#ababab", font=("Arial", 11, "bold"))
        swatch.pack(side="left", padx=(0, 3))
        tk.Label(legend_frame, text=label, bg="#ababab", font=("Arial", 9)).pack(side="left", padx=(0, 15))

    # --- STATUS / HOVER MESSAGE BAR ---
    status_lbl = tk.Label(window, text="", font=("Arial", 9, "italic"), bg="#ababab", fg="#444", wraplength=700, justify="left", anchor="w")
    status_lbl.pack(fill="x", padx=20, pady=(6, 0))

    # --- ACTION BUTTONS ---
    btn_row = tk.Frame(window, bg="#ababab")
    btn_row.pack(pady=10)

    ttk.Button(btn_row, text="🔍 Check Grammar & Punctuation", command=lambda: run_check()).pack(side="left", padx=6)
    ttk.Button(btn_row, text="✅ Show Fully Corrected Text", command=lambda: show_corrected()).pack(side="left", padx=6)
    ttk.Button(btn_row, text="🧹 Clear", command=lambda: clear_all()).pack(side="left", padx=6)

    # --- ISSUES LIST ---
    tk.Label(window, text="Issues Found:", font=("Arial", 10, "bold"), bg="#ababab").pack(anchor="w", padx=20)

    issues_frame = tk.Frame(window, bg="#ababab")
    issues_frame.pack(fill="both", padx=20, pady=(2, 10))

    issues_list = tk.Listbox(issues_frame, height=6, font=("Arial", 9))
    issues_scroll = ttk.Scrollbar(issues_frame, orient="vertical", command=issues_list.yview)
    issues_list.config(yscrollcommand=issues_scroll.set)
    issues_list.pack(side="left", fill="both", expand=True)
    issues_scroll.pack(side="right", fill="y")

    # --- CORRECTED VERSION (hidden until requested) ---
    corrected_frame = tk.Frame(window, bg="#ababab")
    tk.Label(corrected_frame, text="Corrected Version:", font=("Arial", 10, "bold"), bg="#ababab").pack(anchor="w")

    corrected_inner = tk.Frame(corrected_frame, bg="#ababab")
    corrected_inner.pack(fill="both", expand=True, pady=(2, 5))

    corrected_text = tk.Text(corrected_inner, height=8, wrap="word", font=("Arial", 11), bg="#f5fff5")
    corrected_scroll = ttk.Scrollbar(corrected_inner, orient="vertical", command=corrected_text.yview)
    corrected_text.config(yscrollcommand=corrected_scroll.set, state="disabled")
    corrected_text.pack(side="left", fill="both", expand=True)
    corrected_scroll.pack(side="right", fill="y")

    def copy_corrected():
        corrected_text.config(state="normal")
        content = corrected_text.get("1.0", "end-1c")
        corrected_text.config(state="disabled")
        if content.strip():
            window.clipboard_clear()
            window.clipboard_append(content)
            messagebox.showinfo("Copied", "Corrected text copied to clipboard!")

    ttk.Button(corrected_frame, text="📋 Copy Corrected Text", command=copy_corrected).pack(anchor="e")

    # --- CORE LOGIC ---

    def clear_all():
        essay_text.delete("1.0", tk.END)
        for tag in list(essay_text.tag_names()):
            if tag.startswith("err_"):
                essay_text.tag_remove(tag, "1.0", "end")
        issues_list.delete(0, tk.END)
        status_lbl.config(text="")
        corrected_frame.pack_forget()

    def run_check():
        if not _LT_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "This feature needs the 'language_tool_python' package.\n\n"
                "Install it with:\n    pip install language_tool_python\n\n"
                "Then restart Orange Waves."
            )
            return

        text = essay_text.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Empty Essay", "Please type or paste some text to check first!")
            return

        # Clear previously highlighted regions and per-match hover tags
        for tag in list(essay_text.tag_names()):
            if tag.startswith("err_"):
                essay_text.tag_remove(tag, "1.0", "end")
        issues_list.delete(0, tk.END)
        status_lbl.config(text="Checking your essay... this can take a few seconds.")
        window.update_idletasks()

        try:
            tool = _get_tool()
            matches = tool.check(text)
        except Exception as e:
            if _is_rate_limit_error(e):
                messagebox.showerror(
                    "Rate Limit Reached",
                    "The free public grammar-checking service has a request limit, "
                    "and we've hit it for now.\n\n"
                    "Options:\n"
                    "  • Wait about a minute and try again.\n"
                    "  • Switch to a local, unlimited checker: open "
                    "grammar_checker.py and set USE_LOCAL_SERVER = True near the "
                    "top of the file (requires Java, see the comment there)."
                )
            else:
                messagebox.showerror("Check Failed", f"Couldn't reach the grammar checking service.\n\n{e}")
            status_lbl.config(text="")
            return

        if not matches:
            status_lbl.config(text="✅ No issues found — nice work!")
            return

        for i, match in enumerate(matches):
            offset = getattr(match, "offset", None)
            length = getattr(match, "errorLength", None) or getattr(match, "length", 0)
            if offset is None or not length:
                continue

            start_idx = essay_text.index(f"1.0+{offset}c")
            end_idx = essay_text.index(f"1.0+{offset + length}c")

            base_tag = _classify(match)
            per_match_tag = f"{base_tag}_{i}"

            essay_text.tag_add(base_tag, start_idx, end_idx)
            essay_text.tag_add(per_match_tag, start_idx, end_idx)

            replacements = [_rep_text(r) for r in (match.replacements or [])[:3] if _rep_text(r)]
            suggestion = ", ".join(replacements) if replacements else "(no suggestion)"

            entry_text = f"• {match.message}"
            if replacements:
                entry_text += f"  →  try: {suggestion}"
            issues_list.insert(tk.END, entry_text)

            def make_hover(msg=match.message, sug=suggestion):
                def on_enter(_e):
                    status_lbl.config(text=f"{msg}   |   Suggestion: {sug}")

                def on_leave(_e):
                    status_lbl.config(text="")

                return on_enter, on_leave

            on_enter, on_leave = make_hover()
            essay_text.tag_bind(per_match_tag, "<Enter>", on_enter)
            essay_text.tag_bind(per_match_tag, "<Leave>", on_leave)

        status_lbl.config(text=f"Found {len(matches)} issue(s). Hover the highlighted text above for details.")

    def show_corrected():
        if not _LT_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "This feature needs the 'language_tool_python' package.\n\n"
                "Install it with:\n    pip install language_tool_python\n\n"
                "Then restart Orange Waves."
            )
            return

        text = essay_text.get("1.0", "end-1c")
        if not text.strip():
            messagebox.showwarning("Empty Essay", "Please type or paste some text to check first!")
            return

        status_lbl.config(text="Generating the corrected version... this can take a few seconds.")
        window.update_idletasks()

        try:
            tool = _get_tool()
            # tool.correct() runs its own check() internally and applies the
            # top-ranked suggestion for every match it finds (spelling,
            # grammar, agreement/tense issues, and punctuation alike).
            corrected = tool.correct(text)
        except Exception as e:
            if _is_rate_limit_error(e):
                messagebox.showerror(
                    "Rate Limit Reached",
                    "The free public grammar-checking service has a request limit, "
                    "and we've hit it for now.\n\n"
                    "Options:\n"
                    "  • Wait about a minute and try again.\n"
                    "  • Switch to a local, unlimited checker: open "
                    "grammar_checker.py and set USE_LOCAL_SERVER = True near the "
                    "top of the file (requires Java, see the comment there)."
                )
            else:
                messagebox.showerror("Correction Failed", f"Couldn't reach the grammar checking service.\n\n{e}")
            status_lbl.config(text="")
            return

        corrected_text.config(state="normal")
        corrected_text.delete("1.0", tk.END)
        corrected_text.insert("1.0", corrected)
        corrected_text.config(state="disabled")

        corrected_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        status_lbl.config(text="Corrected version generated below.")

    ttk.Button(window, text="⬅ Back to Main Hub", command=on_close).pack(pady=(0, 15))