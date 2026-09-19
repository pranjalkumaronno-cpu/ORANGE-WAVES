import tkinter as tk


def draw_gradient(canvas):
    """Draws a beautiful custom dark red to coral gradient background."""
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
        # FIX: format spec was "{r*:02x*}" (invalid syntax, SyntaxError on import).
        # Correct form is "{r:02x}".
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, y, width, y, fill=color)


def draw_gauge(canvas, percentage, label="Performance"):
    """Draws a custom visual gauge/chart element on a canvas."""
    canvas.delete("gauge_elements")
    width = int(canvas.winfo_width()) if canvas.winfo_width() > 1 else 300
    height = int(canvas.winfo_height()) if canvas.winfo_height() > 1 else 340
    cx, cy, r = width // 2, height // 2, min(width, height) // 3
    canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#ffffff", outline="#ccc", tags="gauge_elements")
    extent = -(percentage / 100.0) * 359.9
    canvas.create_arc(cx - r, cy - r, cx + r, cy + r, start=90, extent=extent, fill="#ff6600", outline="", tags="gauge_elements")
    # FIX: same invalid format-spec syntax as above ("{percentage*:.1f*}").
    canvas.create_text(cx, cy, text=f"{percentage:.1f}%", font=("Arial", 16, "bold"), fill="#000", tags="gauge_elements")
    canvas.create_text(cx, cy + r + 20, text=label, font=("Arial", 11, "bold"), fill="#333", tags="gauge_elements")