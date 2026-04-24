def generate_workout(username):
    clear(); banner()
    users = load_users()
    user = users[username]
    equipment = user.get("equipment", [])
    level = user.get("level", "beginner")
    frequency = user.get("frequency", 3)
    exercises = load_exercises()

    print(f"\n [ WORKOUT ROUTINE ] - {username}\n")

    print(" How much time do you have today?")
    print(" 1. 20 minutes  (3 exercises)")
    print(" 2. 30 minutes  (5 exercises)")
    print(" 3. 45 minutes  (6 exercises)")
    print(" 4. 60 minutes  (8 exercises)")
    time_choice = safe_int(" Choice: ", 1, 4)
    time_map = {1: (20, 3), 2: (30, 5), 3: (45, 6), 4: (60, 8)}
    time_available, exercise_count = time_map.get(time_choice, (60, 8))

    print("\n Generating personalized workout...\n")

    all_flat = []
    for exlist in exercises.values():
        all_flat.extend(exlist)

    GYM_THRESHOLD = 2
    if len(equipment) >= GYM_THRESHOLD:
        workout_type = "Gym Workout"
        pool = []
        for eq in equipment:
            if eq in exercises:
                pool.extend(filter_by_level(exercises[eq], level))
        pool.extend(filter_by_level(exercises.get("none", []), level))
    else:
        workout_type = "Home Workout"
        pool = filter_by_level(exercises.get("none", []), level)
        for eq in equipment:
            if eq in exercises:
                pool.extend(filter_by_level(exercises[eq], level))

    random.shuffle(pool)
    selected = pool[:exercise_count]

    eq_label = ', '.join([e.title() for e in equipment]) if equipment else 'Bodyweight only'

    print(f" Today's Workout - {datetime.now().strftime('%B %d, %Y')}")
    print(f" Type      : {workout_type}")
    print(f" Level     : {level.title()}")
    print(f" Equipment : {eq_label}")
    print(f" Duration  : ~{time_available} minutes")
    print(f" Frequency : {frequency} days/week schedule")
    print(" " + "-" * 58)
    print(f" {'#':<4} {'Exercise':<26} {'Muscle':<20} {'Sets x Reps':<14} {'Level'}")
    print(" " + "-" * 58)
    for i, ex in enumerate(selected, 1):
        print(f" {i:<4} {ex['name']:<26} {ex['muscle']:<20} {ex['sets']}x{ex['reps']:<12} {ex.get('difficulty','').title()}")
    print(" " + "-" * 58)

    print("\n Need to substitute an exercise? (e.g. equipment unavailable)")
    sub_choice = input(" Replace an exercise? (y/n): ").strip().lower()
    if sub_choice == "y":
        for i, ex in enumerate(selected, 1):
            print(f" {i}. {ex['name']} -> Alt: {ex.get('substitute', 'N/A')}")
        try:
            c = safe_int(" Which number to substitute? ", 1, len(selected))
            if not c:
                print(" Invalid selection, keeping original.")
                pause()
                return
            idx = c - 1
            orig = selected[idx]
            alt = get_substitute(orig, all_flat)
            if alt:
                selected[idx] = alt
                print(f" Replaced with: {alt['name']}")
            else:
                print(f" No substitute found for {orig['name']}.")
        except:
            print(" Invalid input, keeping original.")
        pause()
        clear(); banner()
        print(f"\n Updated Workout - {datetime.now().strftime('%B %d, %Y')}")
        print(" " + "-" * 58)
        print(f" {'#':<4} {'Exercise':<26} {'Muscle':<20} {'Sets x Reps'}")
        print(" " + "-" * 58)
        for i, ex in enumerate(selected, 1):
            print(f" {i:<4} {ex['name']:<26} {ex['muscle']:<20} {ex['sets']}x{ex['reps']}")
        print(" " + "-" * 58)

    log = input("\n Log this workout as completed? (y/n): ").strip().lower()
    if log == "y":
        logged_exercises = []
        print("\n Enter the actual weight (kg) and reps you performed.")
        print(" (Press Enter to skip for bodyweight/timed exercises)\n")
        for ex in selected:
            print(f" {ex['name']} - Prescribed: {ex['sets']}x{ex['reps']}")
            weight_in = input(f" Weight used (kg, or Enter to skip): ").strip()
            reps_in = input(f" Actual reps completed (or Enter to skip): ").strip()
            logged_exercises.append({
                "name": ex["name"],
                "muscle": ex["muscle"],
                "sets": ex["sets"],
                "prescribed_reps": ex["reps"],
                "weight_kg": weight_in if weight_in else "bodyweight",
                "actual_reps": reps_in if reps_in else ex["reps"],
            })

        add_session(username, {
            "date": now_str(),
            "workout_type": workout_type,
            "time_available": time_available,
            "level": level,
            "equipment_used": equipment if equipment else ["bodyweight"],
            "exercises": logged_exercises
        })
        print("\n Workout logged successfully!")
    pause()