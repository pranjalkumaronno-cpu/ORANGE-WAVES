import os
import json

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_profile.json")

# Database structural memory mapping all users and tracking current session state
_database = {
    "users": {},
    "current_user": None
}


def load_database():
    global _database
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            # Keep compatibility with older user_profile.json files.
            if isinstance(loaded, dict):
                _database["users"] = loaded.get("users", {})
            else:
                _database["users"] = {}
        else:
            _database["users"] = {}
    except (OSError, json.JSONDecodeError):
        _database["users"] = {}

    _database["current_user"] = None


def save_database():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"users": _database["users"]},
                f,
                indent=4,
                ensure_ascii=False
            )
    except OSError:
        pass


def _get_active_profile():
    username = _database.get("current_user")
    if not username:
        return None
    return _database["users"].get(username)


def register_user(username, gmail, password):
    username = username.strip()
    gmail = gmail.strip()

    if not username or not gmail or not password:
        return False, "All fields are required."

    if username in _database["users"]:
        return False, "Username already exists."

    _database["users"][username] = {
        "gmail": gmail,
        "password": password,
        "xp": 0,
        "saved_marks": {},
        "notes": [],
        "mind_maps": []
    }
    save_database()
    return True, "Account created successfully."


def login_user(username, password):
    username = username.strip()
    profile = _database["users"].get(username)

    if profile and profile.get("password") == password:
        _database["current_user"] = username
        return True, "Login successful."

    return False, "Invalid username or password."


def logout_user():
    _database["current_user"] = None


def get_logged_in_user():
    return _database.get("current_user")


def add_xp(amount=5):
    profile = _get_active_profile()
    if profile is None:
        return 0

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        amount = 0

    profile["xp"] = max(0, int(profile.get("xp", 0)) + amount)
    save_database()
    return profile["xp"]


def get_xp():
    profile = _get_active_profile()
    return int(profile.get("xp", 0)) if profile else 0


def save_calculated_marks(marks_dict):
    profile = _get_active_profile()
    if profile is None:
        return False

    profile["saved_marks"] = dict(marks_dict or {})
    save_database()
    return True


def get_saved_marks():
    profile = _get_active_profile()
    if profile is None:
        return {}
    return dict(profile.get("saved_marks", {}))


# ---------------- NOTES & MIND MAPS ----------------

def _ensure_learning_storage(profile):
    """Adds the new fields to old accounts without breaking them."""
    if profile is None:
        return
    if not isinstance(profile.get("notes"), list):
        profile["notes"] = []
    if not isinstance(profile.get("mind_maps"), list):
        profile["mind_maps"] = []


def get_notes():
    profile = _get_active_profile()
    if profile is None:
        return []
    _ensure_learning_storage(profile)
    return profile["notes"]


def save_notes(notes):
    profile = _get_active_profile()
    if profile is None:
        return False
    _ensure_learning_storage(profile)
    profile["notes"] = list(notes or [])
    save_database()
    return True


def get_mind_maps():
    profile = _get_active_profile()
    if profile is None:
        return []
    _ensure_learning_storage(profile)
    return profile["mind_maps"]


def save_mind_maps(mind_maps):
    profile = _get_active_profile()
    if profile is None:
        return False
    _ensure_learning_storage(profile)
    profile["mind_maps"] = list(mind_maps or [])
    save_database()
    return True


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
        level = 4 + (extra_xp // 150)
        current = extra_xp % 150
        return level, current, 150, "Grandmaster Scholar"


load_database()
