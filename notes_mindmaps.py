import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import math
import uuid
import user_profile


BG = "#ababab"
PANEL = "#f4f4f4"
ACCENT = "#8b0000"


def _normalise(value):
    return " ".join(str(value or "").strip().casefold().split())


def _get_notes():
    notes = user_profile.get_notes() or []
    changed = False
    for note in notes:
        if not note.get("id"):
            note["id"] = _new_id("note")
            changed = True
        if "parent_id" not in note:
            note["parent_id"] = None
            changed = True
    if changed:
        user_profile.save_notes(notes)
    return notes


def _get_mind_maps():
    maps = user_profile.get_mind_maps() or []
    changed = False
    for mind_map in maps:
        if not mind_map.get("id"):
            mind_map["id"] = _new_id("map")
            changed = True
        if "nodes" not in mind_map or not isinstance(mind_map["nodes"], list):
            mind_map["nodes"] = []
            changed = True
        for node in mind_map["nodes"]:
            if not node.get("id"):
                node["id"] = _new_id("node")
                changed = True
            if "parent_id" not in node:
                node["parent_id"] = None
                changed = True
    if changed:
        user_profile.save_mind_maps(maps)
    return maps


def _save_notes(notes):
    user_profile.save_notes(notes)


def _save_mind_maps(maps):
    user_profile.save_mind_maps(maps)


def _new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _note_matches_node(note, node_text):
    node = _normalise(node_text)
    return (
        _normalise(note.get("title")) == node
        or _normalise(note.get("subtopic")) == node
    )


def _all_map_node_names(mind_map):
    return {
        _normalise(node.get("text"))
        for node in mind_map.get("nodes", [])
        if node.get("text")
    }


def _connected_notes_for_map(mind_map):
    map_name = _normalise(mind_map.get("name"))
    node_names = _all_map_node_names(mind_map)
    connected = []
    for note in _get_notes():
        title = _normalise(note.get("title"))
        subtopic = _normalise(note.get("subtopic"))
        if title == map_name or title in node_names or subtopic in node_names:
            connected.append(note)
    return connected


def _connected_maps_for_note(note):
    title = _normalise(note.get("title"))
    subtopic = _normalise(note.get("subtopic"))
    connected = []
    for mind_map in _get_mind_maps():
        if title == _normalise(mind_map.get("name")):
            connected.append(mind_map)
            continue
        node_names = _all_map_node_names(mind_map)
        if title in node_names or subtopic in node_names:
            connected.append(mind_map)
    return connected


def _children(items, parent_id):
    return [item for item in items if item.get("parent_id") == parent_id]


def _note_depth(notes, note):
    depth = 0
    seen = set()
    parent_id = note.get("parent_id")
    while parent_id and parent_id not in seen:
        seen.add(parent_id)
        parent = next((n for n in notes if n.get("id") == parent_id), None)
        if not parent:
            break
        depth += 1
        parent_id = parent.get("parent_id")
    return depth


def open_notes_mindmaps(parent_window):
    parent_window.withdraw()

    window = tk.Toplevel(parent_window)
    window.title("ORANGE WAVES - Notes & Mind Maps")
    window.geometry("1250x780+25+20")
    window.minsize(1050, 680)
    window.config(bg=BG)

    def on_close():
        window.destroy()
        parent_window.deiconify()

    window.protocol("WM_DELETE_WINDOW", on_close)

    header = tk.Frame(window, bg="#660101", height=70)
    header.pack(fill="x")
    header.pack_propagate(False)
    tk.Label(
        header, text="📚 NOTES & MIND MAPS", font=("Arial", 22, "bold"),
        fg="white", bg="#660101"
    ).pack(side="left", padx=25, pady=16)
    tk.Label(
        header, text="Create • Connect • Explore", font=("Arial", 11, "italic"),
        fg="#ffdede", bg="#660101"
    ).pack(side="left", padx=5)

    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True, padx=12, pady=12)

    notes_tab = tk.Frame(notebook, bg=BG)
    maps_tab = tk.Frame(notebook, bg=BG)
    notebook.add(notes_tab, text="  📝 Notes  ")
    notebook.add(maps_tab, text="  🧠 Mind Maps  ")

    # ================================================================
    # NOTES
    # ================================================================
    notes_list_frame = tk.Frame(notes_tab, bg=BG)
    notes_list_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)

    tk.Label(notes_list_frame, text="Your Notes", font=("Arial", 13, "bold"), bg=BG).pack(anchor="w")
    search_var = tk.StringVar()
    ttk.Entry(notes_list_frame, textvariable=search_var, width=30).pack(fill="x", pady=7)

    notes_list = tk.Listbox(notes_list_frame, width=36, height=30, font=("Arial", 10))
    notes_list.pack(fill="y", expand=True)

    notes_editor = tk.Frame(notes_tab, bg=BG)
    notes_editor.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

    tk.Label(notes_editor, text="Note Editor", font=("Arial", 13, "bold"), bg=BG).pack(anchor="w")
    note_parent_info = tk.Label(notes_editor, text="Parent: None (top-level note)", bg=BG, fg="#444")
    note_parent_info.pack(anchor="w", pady=(2, 3))

    title_var = tk.StringVar()
    subtopic_var = tk.StringVar()

    tk.Label(notes_editor, text="Note Name / Title", bg=BG).pack(anchor="w", pady=(5, 2))
    ttk.Entry(notes_editor, textvariable=title_var).pack(fill="x")

    tk.Label(notes_editor, text="Subtopic", bg=BG).pack(anchor="w", pady=(7, 2))
    ttk.Entry(notes_editor, textvariable=subtopic_var).pack(fill="x")

    tk.Label(notes_editor, text="Content", bg=BG).pack(anchor="w", pady=(7, 2))
    content = tk.Text(notes_editor, height=10, wrap="word", font=("Arial", 11))
    content.pack(fill="both", expand=False)

    selected_note_id = {"value": None}
    selected_note_parent_id = {"value": None}

    button_row = tk.Frame(notes_editor, bg=BG)
    button_row.pack(fill="x", pady=(7, 4))

    connection_frame = tk.LabelFrame(notes_editor, text=" 🔗 Connections ", bg=BG, padx=8, pady=5)
    connection_frame.pack(fill="x", pady=(3, 5))
    connection_list = tk.Listbox(connection_frame, height=4, font=("Arial", 9))
    connection_list.pack(fill="x")

    def clear_note_editor():
        selected_note_id["value"] = None
        selected_note_parent_id["value"] = None
        title_var.set("")
        subtopic_var.set("")
        content.delete("1.0", tk.END)
        note_parent_info.config(text="Parent: None (top-level note)")
        connection_list.delete(0, tk.END)
        notes_list.selection_clear(0, tk.END)

    def visible_notes():
        query = _normalise(search_var.get())
        notes = _get_notes()
        if not query:
            return notes
        return [
            note for note in notes
            if query in _normalise(
                f"{note.get('title', '')} {note.get('subtopic', '')} {note.get('content', '')}"
            )
        ]

    def refresh_notes_list(*_):
        notes_list.delete(0, tk.END)
        notes = _get_notes()
        visible = visible_notes()
        for note in visible:
            depth = _note_depth(notes, note)
            prefix = "    " * depth + ("└─ " if depth else "")
            notes_list.insert(
                tk.END,
                f"{prefix}{note.get('title', 'Untitled')}  •  {note.get('subtopic', '')}"
            )

    def show_note_connections(note):
        connection_list.delete(0, tk.END)
        maps = _connected_maps_for_note(note)
        if not maps:
            connection_list.insert(tk.END, "No connected mind maps yet.")
            return
        for mind_map in maps:
            connection_list.insert(tk.END, f"🧠 {mind_map.get('name', 'Untitled Mind Map')}")

    def load_selected_note(_event=None):
        selection = notes_list.curselection()
        if not selection:
            return
        visible = visible_notes()
        if selection[0] >= len(visible):
            return
        note = visible[selection[0]]
        selected_note_id["value"] = note.get("id")
        selected_note_parent_id["value"] = note.get("parent_id")
        title_var.set(note.get("title", ""))
        subtopic_var.set(note.get("subtopic", ""))
        content.delete("1.0", tk.END)
        content.insert("1.0", note.get("content", ""))
        parent = next((n for n in _get_notes() if n.get("id") == note.get("parent_id")), None)
        if parent:
            note_parent_info.config(text=f"Parent: {parent.get('title', 'Untitled')}")
        else:
            note_parent_info.config(text="Parent: None (top-level note)")
        show_note_connections(note)

    def save_note():
        title = title_var.get().strip()
        subtopic = subtopic_var.get().strip()
        body = content.get("1.0", "end-1c").strip()
        if not title:
            messagebox.showwarning("Missing Title", "Give your note a name/title first.")
            return

        notes = _get_notes()
        note_id = selected_note_id["value"]
        existing = next((n for n in notes if n.get("id") == note_id), None)
        if existing:
            existing.update({"title": title, "subtopic": subtopic})
            existing["content"] = body
            existing["parent_id"] = selected_note_parent_id["value"]
        else:
            new_note = {
                "id": _new_id("note"),
                "title": title,
                "subtopic": subtopic,
                "content": body,
                "parent_id": selected_note_parent_id["value"],
            }
            notes.append(new_note)
            selected_note_id["value"] = new_note["id"]

        _save_notes(notes)
        refresh_notes_list()
        saved = next((n for n in _get_notes() if n.get("id") == selected_note_id["value"]), None)
        if saved:
            show_note_connections(saved)
        messagebox.showinfo("Note Saved", "Note saved successfully. Matching mind-map names and nodes connect automatically.")

    def add_subnote():
        parent_id = selected_note_id["value"]
        if not parent_id:
            messagebox.showwarning("Select a Parent Note", "Select the note that should become the parent first.")
            return
        parent = next((n for n in _get_notes() if n.get("id") == parent_id), None)
        if not parent:
            return
        clear_note_editor()
        selected_note_parent_id["value"] = parent_id
        note_parent_info.config(text=f"Parent: {parent.get('title', 'Untitled')}")
        title_var.set(f"{parent.get('title', '')} - ")
        messagebox.showinfo("New Subnote", "The new note will be a child of the selected note. Give it its own title and save it.")

    def delete_note():
        note_id = selected_note_id["value"]
        if not note_id:
            messagebox.showwarning("No Note Selected", "Select a note first.")
            return
        notes = _get_notes()
        descendants = {note_id}
        changed = True
        while changed:
            changed = False
            for note in notes:
                if note.get("parent_id") in descendants and note.get("id") not in descendants:
                    descendants.add(note.get("id"))
                    changed = True
        if not messagebox.askyesno(
            "Delete Note",
            "Delete this note and all of its subnotes?"
        ):
            return
        _save_notes([n for n in notes if n.get("id") not in descendants])
        clear_note_editor()
        refresh_notes_list()

    ttk.Button(button_row, text="💾 Save Note", command=save_note).pack(side="left", padx=(0, 5))
    ttk.Button(button_row, text="➕ New Note", command=clear_note_editor).pack(side="left", padx=5)
    ttk.Button(button_row, text="↳ Add Subnote", command=add_subnote).pack(side="left", padx=5)
    ttk.Button(button_row, text="🗑 Delete", command=delete_note).pack(side="left", padx=5)

    notes_list.bind("<<ListboxSelect>>", load_selected_note)
    search_var.trace_add("write", refresh_notes_list)
    window.bind("<Control-s>", lambda _event: save_note())

    # ================================================================
    # MIND MAPS
    # ================================================================
    map_left = tk.Frame(maps_tab, bg=BG)
    map_left.pack(side="left", fill="y", padx=(10, 5), pady=10)
    tk.Label(map_left, text="Your Mind Maps", font=("Arial", 13, "bold"), bg=BG).pack(anchor="w")
    maps_list = tk.Listbox(map_left, width=28, height=30, font=("Arial", 10))
    maps_list.pack(fill="y", expand=True)

    map_right = tk.Frame(maps_tab, bg=BG)
    map_right.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)

    map_name_var = tk.StringVar()
    node_var = tk.StringVar()
    selected_node_info = tk.StringVar(value="Selected parent: Root")
    selected_map_id = {"value": None}
    selected_node_id = {"value": None}
    current_nodes = {}
    drag_state = {"node_id": None, "dx": 0, "dy": 0}

    top_map_bar = tk.Frame(map_right, bg=BG)
    top_map_bar.pack(fill="x")
    tk.Label(top_map_bar, text="Mind Map Name", bg=BG).pack(side="left")
    ttk.Entry(top_map_bar, textvariable=map_name_var, width=25).pack(side="left", padx=6)
    tk.Label(top_map_bar, text="New Child", bg=BG).pack(side="left", padx=(10, 0))
    ttk.Entry(top_map_bar, textvariable=node_var, width=23).pack(side="left", padx=6)
    ttk.Button(top_map_bar, text="➕ Add Child", command=lambda: add_node()).pack(side="left", padx=4)
    ttk.Button(top_map_bar, text="💾 Save Map", command=lambda: save_map()).pack(side="left", padx=4)
    ttk.Button(top_map_bar, text="🆕 New Map", command=lambda: clear_map_editor()).pack(side="left", padx=4)
    ttk.Button(top_map_bar, text="🗑 Delete", command=lambda: delete_map()).pack(side="left", padx=4)

    tk.Label(map_right, textvariable=selected_node_info, bg=BG, fg="#444", anchor="w").pack(fill="x", pady=(4, 0))

    map_canvas_frame = tk.Frame(map_right, bg="white", bd=1, relief="sunken")
    map_canvas_frame.pack(fill="both", expand=True, pady=6)
    map_canvas = tk.Canvas(map_canvas_frame, bg="#fffafa", highlightthickness=0)
    map_canvas.pack(fill="both", expand=True)
    map_canvas.bind("<B1-Motion>", lambda event: drag_node(drag_state.get("node_id"), event) if drag_state.get("node_id") else None)
    map_canvas.bind("<ButtonRelease-1>", lambda event: finish_drag(drag_state.get("node_id"), event) if drag_state.get("node_id") else None)

    map_info = tk.Label(map_right, text="Drag nodes to move them. Click a node to select it as the parent.", bg=BG, fg="#333", anchor="w")
    map_info.pack(fill="x")
    map_connections = tk.Listbox(map_right, height=4, font=("Arial", 9))
    map_connections.pack(fill="x", pady=(4, 5))

    def refresh_maps_list():
        maps_list.delete(0, tk.END)
        for mind_map in _get_mind_maps():
            maps_list.insert(tk.END, mind_map.get("name", "Untitled Mind Map"))

    def get_selected_map():
        map_id = selected_map_id["value"]
        return next((m for m in _get_mind_maps() if m.get("id") == map_id), None)

    def node_by_id(mind_map, node_id):
        return next((n for n in mind_map.get("nodes", []) if n.get("id") == node_id), None)

    def node_depth(nodes, node):
        depth = 0
        seen = set()
        parent_id = node.get("parent_id")
        while parent_id and parent_id not in seen:
            seen.add(parent_id)
            parent = next((n for n in nodes if n.get("id") == parent_id), None)
            if not parent:
                break
            depth += 1
            parent_id = parent.get("parent_id")
        return depth

    def node_descendants(nodes, node_id):
        result = {node_id}
        changed = True
        while changed:
            changed = False
            for node in nodes:
                if node.get("parent_id") in result and node.get("id") not in result:
                    result.add(node.get("id"))
                    changed = True
        return result

    def choose_initial_position(mind_map, node, index):
        existing = [n for n in mind_map.get("nodes", []) if n is not node and n.get("x") is not None and n.get("y") is not None]
        if node.get("x") is not None and node.get("y") is not None:
            return float(node["x"]), float(node["y"])
        parent_id = node.get("parent_id")
        parent = node_by_id(mind_map, parent_id) if parent_id else None
        if parent and parent.get("x") is not None and parent.get("y") is not None:
            siblings = [n for n in mind_map.get("nodes", []) if n.get("parent_id") == parent_id]
            sibling_index = max(0, siblings.index(node))
            count = max(1, len(siblings))
            angle = (2 * math.pi * sibling_index / count) - math.pi / 2
            distance = 170 + node_depth(mind_map.get("nodes", []), node) * 25
            return float(parent["x"]) + distance * math.cos(angle), float(parent["y"]) + distance * math.sin(angle)
        width = max(map_canvas.winfo_width(), 750)
        height = max(map_canvas.winfo_height(), 480)
        root_x, root_y = width / 2, height / 2
        count = max(1, len(existing) + 1)
        angle = (2 * math.pi * index / count) - math.pi / 2
        return root_x + min(280, width * 0.33) * math.cos(angle), root_y + min(180, height * 0.32) * math.sin(angle)

    def draw_map(mind_map):
        current_nodes.clear()
        map_canvas.delete("all")
        width = max(map_canvas.winfo_width(), 750)
        height = max(map_canvas.winfo_height(), 480)
        root_x, root_y = width / 2, height / 2

        # Keep the root visually movable too. Its coordinates live on the map.
        if mind_map.get("root_x") is None or mind_map.get("root_y") is None:
            mind_map["root_x"] = root_x
            mind_map["root_y"] = root_y
        root_x = float(mind_map.get("root_x", root_x))
        root_y = float(mind_map.get("root_y", root_y))

        # Draw edges first.
        nodes = mind_map.get("nodes", [])
        positions = {}
        for index, node in enumerate(nodes):
            x, y = choose_initial_position(mind_map, node, index)
            node["x"], node["y"] = x, y
            positions[node.get("id")] = (x, y)

        for node in nodes:
            x, y = positions[node.get("id")]
            parent_id = node.get("parent_id")
            if parent_id and parent_id in positions:
                px, py = positions[parent_id]
            else:
                px, py = root_x, root_y
            map_canvas.create_line(px, py, x, y, fill="#777", width=2, tags=("edge",))

        root_w, root_h = 190, 65
        root_rect = map_canvas.create_rectangle(
            root_x - root_w / 2, root_y - root_h / 2,
            root_x + root_w / 2, root_y + root_h / 2,
            fill=ACCENT, outline="#4d0000", width=2, tags=("root_node",)
        )
        root_text_item = map_canvas.create_text(root_x, root_y, text=mind_map.get("name", "Untitled Mind Map"), fill="white", font=("Arial", 12, "bold"), width=175, tags=("root_text",))
        current_nodes["__root__"] = {"id": "__root__", "text": mind_map.get("name", ""), "item_id": root_rect, "x": root_x, "y": root_y}
        map_canvas.tag_bind(root_rect, "<Button-1>", lambda e: begin_node_drag("__root__", e))
        map_canvas.tag_bind(root_text_item, "<Button-1>", lambda e: begin_node_drag("__root__", e))

        for node in nodes:
            x, y = positions[node.get("id")]
            node_w, node_h = 165, 55
            rect = map_canvas.create_rectangle(
                x - node_w / 2, y - node_h / 2,
                x + node_w / 2, y + node_h / 2,
                fill="#ffe1e1", outline=ACCENT, width=2, tags=("node",)
            )
            node_text_item = map_canvas.create_text(x, y, text=node.get("text", ""), fill="#222", font=("Arial", 10, "bold"), width=145, tags=("node_text",))
            current_nodes[node.get("id")] = {"id": node.get("id"), "text": node.get("text", ""), "item_id": rect, "x": x, "y": y}
            map_canvas.tag_bind(rect, "<Button-1>", lambda e, nid=node.get("id"): begin_node_drag(nid, e))
            map_canvas.tag_bind(node_text_item, "<Button-1>", lambda e, nid=node.get("id"): begin_node_drag(nid, e))

        if selected_node_id["value"] not in current_nodes:
            selected_node_id["value"] = "__root__"
        update_selected_label(mind_map)

    def update_selected_label(mind_map):
        nid = selected_node_id["value"]
        if nid == "__root__" or not nid:
            selected_node_info.set("Selected parent: Root (new children will be attached to the mind-map root)")
        else:
            node = node_by_id(mind_map, nid)
            selected_node_info.set(f"Selected parent: {node.get('text', 'Untitled') if node else 'Root'}")

    def begin_node_drag(node_id, event):
        mind_map = get_selected_map()
        if not mind_map or node_id not in current_nodes:
            return
        current = current_nodes[node_id]
        x, y = map_canvas.canvasx(event.x), map_canvas.canvasy(event.y)
        selected_node_id["value"] = node_id
        drag_state["node_id"] = node_id
        drag_state["dx"] = current["x"] - x
        drag_state["dy"] = current["y"] - y
        update_selected_label(mind_map)
        show_node_connections(node_id)

    def drag_node(node_id, event):
        mind_map = get_selected_map()
        if not mind_map or drag_state.get("node_id") != node_id:
            return
        current = current_nodes.get(node_id)
        if not current:
            return
        x = map_canvas.canvasx(event.x) + drag_state["dx"]
        y = map_canvas.canvasy(event.y) + drag_state["dy"]
        if node_id == "__root__":
            mind_map["root_x"], mind_map["root_y"] = x, y
        else:
            node = node_by_id(mind_map, node_id)
            if node:
                node["x"], node["y"] = x, y
        # Redraw keeps every connector attached to the moving node.
        draw_map(mind_map)
        selected_node_id["value"] = node_id

    def finish_drag(node_id, _event=None):
        if drag_state.get("node_id") != node_id:
            return
        drag_state["node_id"] = None
        mind_map = get_selected_map()
        if mind_map:
            _save_mind_maps(_get_mind_maps())
            selected_node_id["value"] = node_id
            update_selected_label(mind_map)

    def show_node_connections(node_id):
        mind_map = get_selected_map()
        if not mind_map:
            return
        map_connections.delete(0, tk.END)
        if node_id == "__root__":
            node_text = mind_map.get("name", "")
            connected = [n for n in _get_notes() if _normalise(n.get("title")) == _normalise(node_text) or _normalise(n.get("subtopic")) == _normalise(node_text)]
        else:
            node = node_by_id(mind_map, node_id)
            node_text = node.get("text", "") if node else ""
            connected = [n for n in _get_notes() if _note_matches_node(n, node_text)]
        if not connected:
            map_info.config(text=f'No notes connected to "{node_text}".')
            map_connections.insert(tk.END, "Create a note with this title/subtopic to connect it automatically.")
            return
        map_info.config(text=f'🔗 {len(connected)} note(s) connected to "{node_text}"')
        for note in connected:
            map_connections.insert(tk.END, f"📄 {note.get('title', 'Untitled')}  •  {note.get('subtopic', '')}")

    def clear_map_editor():
        selected_map_id["value"] = None
        selected_node_id["value"] = None
        map_name_var.set("")
        node_var.set("")
        selected_node_info.set("Selected parent: Root")
        map_canvas.delete("all")
        map_connections.delete(0, tk.END)
        map_info.config(text="Create a map, then click a node and add children under it.")
        maps_list.selection_clear(0, tk.END)

    def add_node():
        text = node_var.get().strip()
        if not text:
            messagebox.showwarning("Missing Child Name", "Type the name of the new subtopic/child first.")
            return
        mind_map = get_selected_map()
        if not mind_map:
            messagebox.showwarning("Create/Select a Mind Map", "Save a mind map first, then add children.")
            return
        parent_id = selected_node_id["value"] or "__root__"
        parent_real_id = None if parent_id == "__root__" else parent_id
        nodes = mind_map.setdefault("nodes", [])
        if any(_normalise(n.get("text")) == _normalise(text) and n.get("parent_id") == parent_real_id for n in nodes):
            messagebox.showwarning("Duplicate Child", "That child already exists under this parent.")
            return
        new_node = {
            "id": _new_id("node"),
            "text": text,
            "parent_id": parent_real_id,
            "x": None,
            "y": None,
        }
        nodes.append(new_node)
        _save_mind_maps(_get_mind_maps())
        node_var.set("")
        selected_node_id["value"] = new_node["id"]
        draw_map(mind_map)
        show_node_connections(new_node["id"])

    def save_map():
        name = map_name_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Give your mind map a name first.")
            return
        maps = _get_mind_maps()
        map_id = selected_map_id["value"]
        existing = next((m for m in maps if m.get("id") == map_id), None)
        if existing:
            existing["name"] = name
        else:
            new_map = {
                "id": _new_id("map"),
                "name": name,
                "nodes": [],
                "root_x": None,
                "root_y": None,
            }
            maps.append(new_map)
            selected_map_id["value"] = new_map["id"]
            existing = new_map
        _save_mind_maps(maps)
        refresh_maps_list()
        selected = next((m for m in _get_mind_maps() if m.get("id") == selected_map_id["value"]), None)
        if selected:
            map_name_var.set(selected.get("name", ""))
            selected_node_id["value"] = "__root__"
            draw_map(selected)
            show_node_connections("__root__")
        messagebox.showinfo("Mind Map Saved", "Mind map saved successfully.")

    def load_selected_map(_event=None):
        selection = maps_list.curselection()
        if not selection:
            return
        maps = _get_mind_maps()
        if selection[0] >= len(maps):
            return
        mind_map = maps[selection[0]]
        selected_map_id["value"] = mind_map.get("id")
        selected_node_id["value"] = "__root__"
        map_name_var.set(mind_map.get("name", ""))
        node_var.set("")
        draw_map(mind_map)
        show_node_connections("__root__")

    def delete_map():
        map_id = selected_map_id["value"]
        if not map_id:
            messagebox.showwarning("No Mind Map Selected", "Select a mind map first.")
            return
        if not messagebox.askyesno("Delete Mind Map", "Delete this mind map permanently?"):
            return
        _save_mind_maps([m for m in _get_mind_maps() if m.get("id") != map_id])
        clear_map_editor()
        refresh_maps_list()

    def delete_selected_node():
        mind_map = get_selected_map()
        node_id = selected_node_id["value"]
        if not mind_map or not node_id or node_id == "__root__":
            messagebox.showwarning("Select a Child", "Select a subtopic node first. The root cannot be deleted.")
            return
        node = node_by_id(mind_map, node_id)
        if not node:
            return
        descendants = node_descendants(mind_map.get("nodes", []), node_id)
        if not messagebox.askyesno("Delete Branch", f"Delete '{node.get('text', '')}' and all of its child nodes?"):
            return
        mind_map["nodes"] = [n for n in mind_map.get("nodes", []) if n.get("id") not in descendants]
        selected_node_id["value"] = "__root__"
        _save_mind_maps(_get_mind_maps())
        draw_map(mind_map)
        show_node_connections("__root__")

    # Extra map controls below canvas, so the top bar stays compact.
    map_button_row = tk.Frame(map_right, bg=BG)
    map_button_row.pack(fill="x", pady=(0, 3))
    ttk.Button(map_button_row, text="🗑 Delete Selected Branch", command=delete_selected_node).pack(side="left")
    ttk.Label(map_button_row, text="  Tip: click a node to make it the parent; drag any node to reposition it.", background=BG).pack(side="left", padx=8)

    maps_list.bind("<<ListboxSelect>>", load_selected_map)

    def open_note_from_connection(_event=None):
        selection = map_connections.curselection()
        if not selection:
            return
        value = map_connections.get(selection[0])
        if not value.startswith("📄"):
            return
        title = value[2:].split("  •  ")[0].strip()
        note = next((n for n in _get_notes() if n.get("title", "") == title), None)
        if note:
            notebook.select(notes_tab)
            selected_note_id["value"] = note.get("id")
            selected_note_parent_id["value"] = note.get("parent_id")
            title_var.set(note.get("title", ""))
            subtopic_var.set(note.get("subtopic", ""))
            content.delete("1.0", tk.END)
            content.insert("1.0", note.get("content", ""))
            parent = next((n for n in _get_notes() if n.get("id") == note.get("parent_id")), None)
            note_parent_info.config(text=f"Parent: {parent.get('title', 'Untitled')}" if parent else "Parent: None (top-level note)")
            show_note_connections(note)

    map_connections.bind("<Double-Button-1>", open_note_from_connection)

    # Redraw after resizing so newly opened windows use their actual canvas size.
    map_canvas.bind("<Configure>", lambda _event: (get_selected_map() and draw_map(get_selected_map())))

    refresh_notes_list()
    refresh_maps_list()


__all__ = ["open_notes_mindmaps"]
