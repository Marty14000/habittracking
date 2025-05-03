import questionary
from habit import Habit
from db import get_db, get_habits, get_periodicity
from analyse import calculate_longest_streaks, longest_streak_per_habit
from datetime import datetime

# List of habits to chose from. To be extended in case of additional habits needed.
PREDEFINED_HABITS = ["Cleaning", "Exercise", "Meditating", "Reading", "Yoga"]


# all prints in cyan color for better visualization
def cyan_print(message: str):
    """Prints the given message in CYAN color."""
    print(f"\033[96m{message}\033[0m")


def cli():
    db = get_db()
    stop = False
    while not stop:
        choice = questionary.select("Choose an option",
                                    choices=["Add Habit", "Check Off Habit", "Analyse Habit", "Exit"]).ask()
        if choice == "Add Habit":
            predefined_habits = PREDEFINED_HABITS
            stored_habits = get_habits(db)
            stored_habit_names = [habit[0] for habit in stored_habits]
            habit_ok = False
            while not habit_ok:
                # only make habits available for selection that are not already tracked
                choices = [
                    {"name": habit_name, "disabled": "already tracked, not available for adding"
                        if habit_name in stored_habit_names else None}
                    for habit_name in predefined_habits
                ]
                # noinspection PyTypeChecker
                choices.append("EXIT this menu")
                name = questionary.select("Choose a habit or EXIT this  menu", choices=choices).ask()

                if name == "EXIT this menu":
                    habit_ok = True

                else:
                    desc = questionary.text("Whats the description of the habit?").ask()
                    periodicity = questionary.select("Chose a periodicity:", choices=["Daily", "Weekly"]).ask()
                    habit = Habit(name, desc, periodicity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    habit.store(db)
                    cyan_print(f"Habit {habit} has been added")
                    habit_ok = True

        elif choice == "Check Off Habit":
            stored_habits = get_habits(db)
            stored_habit_names = [habit[0] for habit in stored_habits]
            while True:

                name = questionary.select(
                    "Chose habit for checkoff or EXIT this menu",
                    choices=stored_habit_names + ["EXIT this menu"]).ask()

                if name == "EXIT this menu":
                    break
                habit = Habit(name)
                habit.check_off(db)
                cyan_print(f"Habit '{name}' has been checked off")
                continue

        elif choice == "Analyse Habit":
            stored_habits = get_habits(db)
            # Check on available habits, no need to proceed if there are none
            if len(stored_habits) == 0:
                cyan_print("No habits tracked yet, please first add a habit")
                continue
            stored_habit_names = [habit[0] for habit in stored_habits]
            while True:
                choice = questionary.select("Choose an option or EXIT this menu",
                                            choices=["List of all currently tracked habits",
                                                     "List of all habits grouped by periodicity",
                                                     "List of all habits and their longest run streak",
                                                     "Longest run streak for a given habit", "EXIT this menu"]).ask()

                if choice == "EXIT this menu":
                    break

                elif choice == "List of all currently tracked habits":
                    print()
                    cyan_print(f"{'Habit Name':<20} {'Creation Date and Time':<40}")
                    cyan_print("-" * 60)

                    for habit in stored_habits:
                        cyan_print(f"{habit[0]:<20} created on {habit[3]}")

                    print()

                elif choice == "List of all habits grouped by periodicity":
                    print()
                    cyan_print(f"{'DAILY habits':<20} {'WEEKLY habits':<20}")
                    cyan_print("-" * 40)

                    daily_habits = [habit for habit in stored_habit_names if get_periodicity(db, habit) == "Daily"]
                    weekly_habits = [habit for habit in stored_habit_names if get_periodicity(db, habit) == "Weekly"]

                    max_length = max(len(daily_habits), len(weekly_habits))

                    for i in range(max_length):
                        daily = daily_habits[i] if i < len(daily_habits) else ""
                        weekly = weekly_habits[i] if i < len(weekly_habits) else ""
                        cyan_print(f"{daily:<20} {weekly:<20}")
                    print()

                elif choice == "List of all habits and their longest run streak":
                    habits_longest_streaks = calculate_longest_streaks(db)
                    print()
                    cyan_print(f"{'Habit Name':<20} {'Longest Streak':<15}")
                    cyan_print("-" * 35)

                    # Iterate and print each habit and its longest streak
                    for habit, streak, periodicity in habits_longest_streaks:
                        if periodicity == 'Daily':
                            cyan_print(f"{habit:<20} {streak} day(s)")
                        else:
                            cyan_print(f"{habit:<20} {streak} week(s)")

                    print()

                elif choice == "Longest run streak for a given habit":
                    end = False
                    while not end:
                        name = questionary.select(
                            "Chose habit for calculation of longest run streak or EXIT this menu",
                            choices=stored_habit_names + ["EXIT this menu"]).ask()
                        if name == "EXIT this menu":
                            end = True
                        else:
                            longest_streak_per_habit(db, name)
                            print()

        else:
            stop = True

    db.close()


if __name__ == "__main__":
    cli()
