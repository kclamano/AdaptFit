import os
import random
from datetime import datetime
from data import (
    load_users, save_users,
    load_sessions, add_session,
    load_exercises, load_nutrition,
    filter_by_level, get_substitute,
    hash_password,
    ALL_EQUIPMENT, EXPERIENCE_LEVELS, FREQUENCY_OPTIONS
)

# ── UI Helpers ────────────────────────────────────────────────
def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("=" * 62)
    print("  AdaptFit: Smart Workout Planning System")
    print("  Based on Available Equipment and Lifestyle")
    print("=" * 62)

def pause():
    input("\n  Press Enter to continue...")

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ── Auth ──────────────────────────────────────────────────────
def register():
    clear(); banner()
    print("\n  [ REGISTER ]\n")
    users = load_users()

    username = input("  Enter username: ").strip()
    if not username:
        print("  Username cannot be empty."); pause(); return
    if username in users:
        print("  Username already exists."); pause(); return

    password = input("  Enter password: ").strip()
    if len(password) < 4:
        print("  Password must be at least 4 characters."); pause(); return
    confirm = input("  Confirm password: ").strip()
    if password != confirm:
        print("  Passwords do not match."); pause(); return

    # Fitness goal
    nutrition = load_nutrition()
    goals = list(nutrition.keys())
    print("\n  Select your fitness goal:")
    for i, g in enumerate(goals, 1):
        print(f"    {i}. {g.title()}")
    try:
        goal = goals[int(input("  Choice: ")) - 1]
    except:
        goal = "general fitness"

    # Experience level
    print("\n  Select your experience level:")
    for i, lvl in enumerate(EXPERIENCE_LEVELS, 1):
        print(f"    {i}. {lvl.title()}")
    try:
        level = EXPERIENCE_LEVELS[int(input("  Choice: ")) - 1]
    except:
        level = "beginner"

    # Workout frequency
    print("\n  How many days per week do you plan to work out?")
    for i, f in enumerate(FREQUENCY_OPTIONS, 1):
        print(f"    {i}. {f} days/week")
    try:
        frequency = FREQUENCY_OPTIONS[int(input("  Choice: ")) - 1]
    except:
        frequency = 3

    users[username] = {
        "password":  hash_password(password),
        "goal":      goal,
        "level":     level,
        "frequency": frequency,
        "equipment": [],
        "joined":    datetime.now().strftime("%Y-%m-%d")
    }
    save_users(users)
    print(f"\n  Account created! Welcome, {username}!")
    pause()

def login():
    clear(); banner()
    print("\n  [ LOGIN ]\n")
    users = load_users()
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()
    if username in users and users[username]["password"] == hash_password(password):
        print(f"\n  Welcome back, {username}!")
        pause()
        return username
    print("\n  Invalid username or password.")
    pause()
    return None

# ── Equipment ─────────────────────────────────────────────────
def manage_equipment(username):
    users = load_users()
    user  = users[username]
    while True:
        clear(); banner()
        print(f"\n  [ EQUIPMENT MANAGER ] - {username}\n")
        current   = user.get("equipment", [])
        available = [e for e in ALL_EQUIPMENT if e not in current]

        print("  Your current equipment:")
        if current:
            for e in current:
                print(f"    {e.title()}")
        else:
            print("    (none - bodyweight workouts only)")

        print("\n  Available equipment to add:")
        if not available:
            print("    You have all equipment listed!")
        else:
            for i, e in enumerate(available, 1):
                print(f"    {i}. {e.title()}")

        print("\n  Options:  A - Add   R - Remove   B - Back")
        choice = input("\n  Choice: ").strip().upper()

        if choice == "A" and available:
            try:
                eq = available[int(input("  Enter number to add: ")) - 1]
                user["equipment"].append(eq)
                users[username] = user
                save_users(users)
                print(f"  {eq.title()} added!")
                pause()
            except:
                print("  Invalid input."); pause()

        elif choice == "R" and current:
            for i, e in enumerate(current, 1):
                print(f"    {i}. {e.title()}")
            try:
                eq = current[int(input("  Enter number to remove: ")) - 1]
                user["equipment"].remove(eq)
                users[username] = user
                save_users(users)
                print(f"  {eq.title()} removed.")
                pause()
            except:
                print("  Invalid input."); pause()

        elif choice == "B":
            break

# ── Profile Settings ──────────────────────────────────────────
def edit_profile(username):
    users = load_users()
    user  = users[username]
    while True:
        clear(); banner()
        print(f"\n  [ PROFILE SETTINGS ] - {username}\n")
        print(f"  Goal      : {user.get('goal','').title()}")
        print(f"  Level     : {user.get('level','beginner').title()}")
        print(f"  Frequency : {user.get('frequency', 3)} days/week")
        print("\n  1. Change Fitness Goal")
        print("  2. Change Experience Level")
        print("  3. Change Workout Frequency")
        print("  4. Back")
        choice = input("\n  Choice: ").strip()

        if choice == "1":
            nutrition = load_nutrition()
            goals = list(nutrition.keys())
            for i, g in enumerate(goals, 1):
                print(f"    {i}. {g.title()}")
            try:
                user["goal"] = goals[int(input("  Choice: ")) - 1]
                save_users(users); print("  Goal updated!")
            except:
                pass
            pause()

        elif choice == "2":
            for i, lvl in enumerate(EXPERIENCE_LEVELS, 1):
                print(f"    {i}. {lvl.title()}")
            try:
                user["level"] = EXPERIENCE_LEVELS[int(input("  Choice: ")) - 1]
                save_users(users); print("  Level updated!")
            except:
                pass
            pause()

        elif choice == "3":
            for i, f in enumerate(FREQUENCY_OPTIONS, 1):
                print(f"    {i}. {f} days/week")
            try:
                user["frequency"] = FREQUENCY_OPTIONS[int(input("  Choice: ")) - 1]
                save_users(users); print("  Frequency updated!")
            except:
                pass
            pause()

        elif choice == "4":
            break

# ── Workout Generator ─────────────────────────────────────────
def generate_workout(username):
    clear(); banner()
    users     = load_users()
    user      = users[username]
    equipment = user.get("equipment", [])
    level     = user.get("level", "beginner")
    exercises = load_exercises()

    print(f"\n  [ WORKOUT ROUTINE ] - {username}\n")
    print("  Generating personalized workout...\n")

    # Build pool filtered by difficulty
    all_flat = []
    for exlist in exercises.values():
        all_flat.extend(exlist)

    pool = filter_by_level(exercises.get("none", []), level)
    for eq in equipment:
        if eq in exercises:
            pool.extend(filter_by_level(exercises[eq], level))

    random.shuffle(pool)
    selected = pool[:8]

    eq_label = ', '.join([e.title() for e in equipment]) if equipment else 'Bodyweight only'
    print(f"  Today's Workout  -  {datetime.now().strftime('%B %d, %Y')}")
    print(f"  Level     : {level.title()}")
    print(f"  Equipment : {eq_label}")
    print("  " + "-" * 58)
    print(f"  {'#':<4} {'Exercise':<26} {'Muscle':<20} {'Sets x Reps':<14} {'Level'}")
    print("  " + "-" * 58)
    for i, ex in enumerate(selected, 1):
        print(f"  {i:<4} {ex['name']:<26} {ex['muscle']:<20} {ex['sets']}x{ex['reps']:<12} {ex.get('difficulty','').title()}")
    print("  " + "-" * 58)

    # Substitution mechanism
    print("\n  Need to substitute an exercise? (e.g. equipment unavailable)")
    sub_choice = input("  Replace an exercise? (y/n): ").strip().lower()
    if sub_choice == "y":
        for i, ex in enumerate(selected, 1):
            print(f"    {i}. {ex['name']}  ->  Alt: {ex.get('substitute', 'N/A')}")
        try:
            idx = int(input("  Which number to substitute? ")) - 1
            orig = selected[idx]
            alt  = get_substitute(orig, all_flat)
            if alt:
                selected[idx] = alt
                print(f"  Replaced with: {alt['name']}")
            else:
                print(f"  No substitute found for {orig['name']}.")
        except:
            print("  Invalid input, keeping original.")
        pause()
        clear(); banner()
        print(f"\n  Updated Workout - {datetime.now().strftime('%B %d, %Y')}")
        print("  " + "-" * 58)
        print(f"  {'#':<4} {'Exercise':<26} {'Muscle':<20} {'Sets x Reps'}")
        print("  " + "-" * 58)
        for i, ex in enumerate(selected, 1):
            print(f"  {i:<4} {ex['name']:<26} {ex['muscle']:<20} {ex['sets']}x{ex['reps']}")
        print("  " + "-" * 58)

    # Log workout with weights & reps
    log = input("\n  Log this workout as completed? (y/n): ").strip().lower()
    if log == "y":
        logged_exercises = []
        print("\n  Enter the actual weight (kg) and reps you performed.")
        print("  (Press Enter to skip for bodyweight/timed exercises)\n")
        for ex in selected:
            print(f"  {ex['name']} - Prescribed: {ex['sets']}x{ex['reps']}")
            weight_in = input(f"    Weight used (kg, or Enter to skip): ").strip()
            reps_in   = input(f"    Actual reps completed (or Enter to skip): ").strip()
            logged_exercises.append({
                "name":   ex["name"],
                "muscle": ex["muscle"],
                "sets":   ex["sets"],
                "prescribed_reps": ex["reps"],
                "weight_kg": weight_in if weight_in else "bodyweight",
                "actual_reps": reps_in if reps_in else ex["reps"],
            })

        add_session(username, {
            "date":           now_str(),
            "level":          level,
            "equipment_used": equipment if equipment else ["bodyweight"],
            "exercises":      logged_exercises
        })
        print("\n  Workout logged successfully!")
    pause()

# ── Progress ──────────────────────────────────────────────────
def track_progress(username):
    while True:
        clear(); banner()
        print(f"\n  [ PROGRESS TRACKER ] - {username}\n")
        sessions = load_sessions()
        logs     = sessions.get(username, [])

        if not logs:
            print("  No workouts logged yet. Complete a workout first!")
            pause(); return

        print(f"  Total sessions logged : {len(logs)}")
        print(f"  Last workout          : {logs[-1]['date']}\n")
        print("  1. View recent sessions (last 5)")
        print("  2. View session details")
        print("  3. Back")
        choice = input("\n  Choice: ").strip()

        if choice == "1":
            clear(); banner()
            print(f"\n  [ RECENT SESSIONS ] - {username}\n")
            for entry in reversed(logs[-5:]):
                exs = entry.get("exercises", [])
                names = [e["name"] if isinstance(e, dict) else e for e in exs]
                print(f"  {entry['date']}  |  Level: {entry.get('level','').title()}")
                print(f"     {', '.join(names[:4])}{'...' if len(names)>4 else ''}")
                print()
            pause()

        elif choice == "2":
            clear(); banner()
            print(f"\n  [ SESSION DETAILS ] - {username}\n")
            for i, entry in enumerate(reversed(logs[-5:]), 1):
                print(f"  {i}. {entry['date']}")
            try:
                idx  = int(input("\n  Select session: ")) - 1
                sess = list(reversed(logs[-5:]))[idx]
                clear(); banner()
                print(f"\n  {sess['date']}  |  Level: {sess.get('level','').title()}")
                print(f"  Equipment: {', '.join(sess.get('equipment_used', []))}\n")
                print(f"  {'Exercise':<26} {'Weight':<14} {'Reps':<12} {'Sets'}")
                print("  " + "-" * 56)
                for ex in sess.get("exercises", []):
                    if isinstance(ex, dict):
                        print(f"  {ex['name']:<26} {ex.get('weight_kg','—'):<14} {ex.get('actual_reps','—'):<12} {ex.get('sets','—')}")
                    else:
                        print(f"  {ex}")
                print("  " + "-" * 56)
            except:
                print("  Invalid selection.")
            pause()

        elif choice == "3":
            break

# ── History ───────────────────────────────────────────────────
def view_history(username):
    clear(); banner()
    print(f"\n  [ WORKOUT HISTORY ] - {username}\n")
    sessions = load_sessions()
    logs     = sessions.get(username, [])

    if not logs:
        print("  No workout history found.")
        pause(); return

    print(f"  {'#':<4} {'Date':<20} {'Level':<14} {'Exercises':<10} {'Equipment'}")
    print("  " + "-" * 62)
    for i, entry in enumerate(logs, 1):
        exs = entry.get("exercises", [])
        eq  = ', '.join(entry.get("equipment_used", []))[:18]
        print(f"  {i:<4} {entry['date']:<20} {entry.get('level','').title():<14} {len(exs):<10} {eq}")
    print("  " + "-" * 62)
    pause()

# ── Nutrition ─────────────────────────────────────────────────
def nutrition_tips(username):
    clear(); banner()
    users     = load_users()
    nutrition = load_nutrition()
    goal      = users[username].get("goal", "general fitness")
    tips      = nutrition.get(goal, list(nutrition.values())[0])

    print(f"\n  [ NUTRITION TIPS ] - Goal: {goal.title()}\n")
    print("  " + "-" * 54)
    for tip in tips:
        print(f"  {tip}")
    print("  " + "-" * 54)

    goals = list(nutrition.keys())
    print("\n  Change goal?")
    for i, g in enumerate(goals, 1):
        print(f"    {i}. {g.title()}")
    print("    0. Keep current")
    try:
        c = int(input("\n  Choice: "))
        if 1 <= c <= len(goals):
            users[username]["goal"] = goals[c - 1]
            save_users(users)
            print(f"  Goal updated to: {goals[c-1].title()}")
    except:
        pass
    pause()

# ── Dashboard ─────────────────────────────────────────────────
def dashboard(username):
    while True:
        clear(); banner()
        users    = load_users()
        sessions = load_sessions()
        user     = users.get(username, {})
        logs     = sessions.get(username, [])

        print(f"\n  User       : {username}")
        print(f"  Goal       : {user.get('goal', '').title()}")
        print(f"  Level      : {user.get('level', 'beginner').title()}")
        print(f"  Frequency  : {user.get('frequency', 3)} days/week")
        print(f"  Equipment  : {len(user.get('equipment', []))} item(s)")
        print(f"  Sessions   : {len(logs)} logged (last 10 saved)")
        print("\n  " + "-" * 48)
        print("  MAIN MENU")
        print("  " + "-" * 48)
        print("    1. Manage Equipment")
        print("    2. Generate Workout Routine")
        print("    3. Track Progress")
        print("    4. View Workout History")
        print("    5. Nutrition Tips")
        print("    6. Profile Settings")
        print("    7. Logout")
        print("  " + "-" * 48)
        choice = input("\n  Enter choice: ").strip()

        if   choice == "1": manage_equipment(username)
        elif choice == "2": generate_workout(username)
        elif choice == "3": track_progress(username)
        elif choice == "4": view_history(username)
        elif choice == "5": nutrition_tips(username)
        elif choice == "6": edit_profile(username)
        elif choice == "7":
            print(f"\n  Goodbye, {username}! Keep grinding!")
            pause(); break

# ── Entry Point ───────────────────────────────────────────────
def main():
    while True:
        clear(); banner()
        print("\n  1. Login")
        print("  2. Register")
        print("  3. Exit")
        choice = input("\n  Enter choice: ").strip()
        if choice == "1":
            user = login()
            if user:
                dashboard(user)
        elif choice == "2":
            register()
        elif choice == "3":
            clear()
            print("\n  Thank you for using AdaptFit!")
            print("  Stay fit, stay healthy.\n")
            break

if __name__ == "__main__":
    main()