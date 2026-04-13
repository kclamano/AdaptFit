import json
import os
import hashlib

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
USERS_FILE     = os.path.join(BASE_DIR, "users.json")
SESSIONS_FILE  = os.path.join(BASE_DIR, "sessions.json")
EXERCISES_FILE = os.path.join(BASE_DIR, "exercises.json")
NUTRITION_FILE = os.path.join(BASE_DIR, "nutrition.json")

MAX_SESSIONS = 10

ALL_EQUIPMENT = sorted([
    "dumbbells", "barbell", "resistance bands", "pull-up bar",
    "bench", "kettlebell", "treadmill", "jump rope"
])

EXPERIENCE_LEVELS = ["beginner", "intermediate", "advanced"]
FREQUENCY_OPTIONS = [2, 3, 4, 5, 6]   # days per week

DIFFICULTY_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2}

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_users():
    return load_json(USERS_FILE)

def save_users(data):
    save_json(USERS_FILE, data)

def load_sessions():
    return load_json(SESSIONS_FILE)

def save_sessions(data):
    save_json(SESSIONS_FILE, data)

def add_session(username, entry):
    """Add session and keep only last MAX_SESSIONS."""
    sessions = load_sessions()
    if username not in sessions:
        sessions[username] = []
    sessions[username].append(entry)
    sessions[username] = sessions[username][-MAX_SESSIONS:]
    save_sessions(sessions)

def load_exercises():
    return load_json(EXERCISES_FILE)

def load_nutrition():
    return load_json(NUTRITION_FILE)

def filter_by_level(exercises, level):
    """Return exercises at or below user's experience level."""
    max_rank = DIFFICULTY_RANK.get(level, 2)
    return [ex for ex in exercises if DIFFICULTY_RANK.get(ex.get("difficulty", "beginner"), 0) <= max_rank]

def get_substitute(exercise, all_exercises_flat):
    """Find the substitute exercise by name from the full pool."""
    sub_name = exercise.get("substitute", "")
    for ex in all_exercises_flat:
        if ex["name"] == sub_name:
            return ex
    return None

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()