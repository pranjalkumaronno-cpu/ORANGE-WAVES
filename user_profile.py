import os
import json

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_profile.json")

# Database structural memory mapping all users and tracking current session state
_database = {
    "users": {},          # Maps username -> {"gmail": str, "password": str, "xp": int, "saved_marks": dict}
    "current_user": None  # Tracks who is currently authenticated
}


def load_database():
    """Loads database structural state variables from permanent JSON file blocks."""
    global _database
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "users" in loaded:
                    _database["users"] = loaded["users"]
                    # Reset active runtime session variables on cold startup for security
                    _database["current_user"] = None
        except Exception:
            pass


def save_database():
    """Commits user registers and scores into absolute local file tracks."""
    global _database
    try:
        with open(DB_FILE, "w") as f:
            json.dump({"users": _database["users"]}, f, indent=4)
    except Exception:
        pass


def register_user(username, gmail, password):
    """Registers a unique profile structure inside the ledger system."""
    global _database
    username = username.strip()
    if not username or not gmail or not password:
        return False, "All registration input parameters are mandatory."
    if username in _database["users"]:
        return False, "Username matches an existing profile record."
    _database["users"][username] = {
        "gmail": gmail.strip(),
        "password": password,
        "xp": 0,
        "saved_marks": {}
    }
    save_database()
    return True, "Registration completed successfully!"


def login_user(username, password):
    """Verifies access keys to initialize an active workspace layer."""
    global _database
    username = username.strip()
    if username in _database["users"] and _database["users"][username]["password"] == password:
        _database["current_user"] = username
        return True, "Access granted."
    return False, "Invalid authentication matching attributes."


def logout_user():
    """Closes down session tokens immediately."""
    global _database
    _database["current_user"] = None


def get_logged_in_user():
    global _database
    return _database["current_user"]


def _get_active_profile():
    global _database
    user = _database["current_user"]
    if user and user in _database["users"]:
        return _database["users"][user]
    return None


def add_xp(amount=5):
    prof = _get_active_profile()
    if prof:
        prof["xp"] = prof.get("xp", 0) + amount
        save_database()
        return prof["xp"]
    return 0


def get_xp():
    prof = _get_active_profile()
    return prof.get("xp", 0) if prof else 0


def save_calculated_marks(marks_dict):
    prof = _get_active_profile()
    if prof:
        prof["saved_marks"] = marks_dict
        save_database()


def get_saved_marks():
    prof = _get_active_profile()
    return prof.get("saved_marks", {}) if prof else {}


def calculate_level_info():
    xp = get_xp()
    if xp < 50:
        return 1, xp, 50, "Novice Learner"
    elif xp < 120:
        return 2, xp - 50, 70, "Study Tracker"
    elif xp < 220:
        return 3, xp - 120, 100, "Focus Master"
    else:
        extra_xp = xp - 220
        lvl_offset = extra_xp // 150
        rem_xp = extra_xp % 150
        return 4 + lvl_offset, rem_xp, 150, "Grandmaster Scholar"


# Run cold structural check configuration on boot sequence
load_database()


