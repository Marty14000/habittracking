from operator import truediv

import questionary
from habit import Habit
from db import get_db, get_habits, add_habit, checkoff_habit, get_habit_events, get_longest_streak, get_periodicity
from analyse import calculate_longest_streaks
from datetime import datetime


def cli():
    db = get_db()
    stop = False
    while not stop:
        choice = questionary.select("Choose an option", choices=["Add Habit", "Check Off Habit", "Analyse Habit", "Exit"]).ask()
        if choice == "Add Habit":
                predefined_habits = ["Cleaning","Exercise","Meditating","Reading","Yoga"]
                stored_habits = get_habits(db)
                stored_habit_names = list(sum(stored_habits, ()))
                habit_ok = False
                while not habit_ok:
                    choices = [
                        {"name": habit_name, "disabled": "already tracked" if habit_name in stored_habit_names else None}
                        for habit_name in predefined_habits
                    ]
                    choices.append("RETURN")
                    name = questionary.select("Choose a habit or RETURN to exit to main menu", choices=choices).ask()
                    #name = questionary.text("Whats the name of the habit?").ask().strip().upper()
                    '''if name in stored_habit_names:
                        habit_ok = False
                        print("Habit already exists, please choose another habit")
                    elif name == "":
                        habit_ok = False
                        print("Habit name cannot be empty")'''

                    if name == "RETURN":
                        habit_ok = True

                    else:
                        habit_ok = True
                        desc = questionary.text("Whats the description of the habit?").ask()
                        periodicity = questionary.select("Chose a periodicity:", choices=["Daily", "Weekly"]).ask()
                        habit = Habit(name, desc, periodicity)
                        habit.store(db)
                        print(f"Habit {habit} has been added")



        elif choice == "Check Off Habit":
            stored_habits = get_habits(db)
            stored_habit_names = list(sum(stored_habits, ()))
            while True:
                name = questionary.rawselect(
                    "Chose habit for checkoff or RETURN to exit to main menu",
                    choices=stored_habit_names + ["RETURN"]).ask()

                if name == "RETURN":
                    break
                habit = Habit(name)
                habit.check_off(db)
                print(f"Habit '{name}' has been checked off")
                break

        elif choice == "Analyse Habit":
            stored_habits = get_habits(db)
            stored_habit_names = list(sum(stored_habits, ()))
            while True:
                choice = questionary.select("Choose an option or RETURN to exit to main menu",
                choices = ["List of all currently tracked habits", "List of all habits grouped by periodicity",
                         "List of all habits and their longest run streak", "Longest run streak for a given habit", "RETURN"]).ask()


                if choice == "RETURN":
                    break

                elif choice == "List of all currently tracked habits":
                    print()
                    print(f"{'Habit Name':<20}")
                    print("-" * 20)

                    # Iterate and print each habit and its longest streak
                    for habit in stored_habit_names:
                        print(f"{habit:<20}")
                    #print(stored_habit_names)

                    print()  # Add empty space after the table for better readability

                elif choice == "List of all habits and their longest run streak":
                    habits_longest_streaks = calculate_longest_streaks(db)
                    print()
                    print(f"{'Habit Name':<20} {'Longest Streak':<15}")
                    print("-" * 35)

                    # Iterate and print each habit and its longest streak
                    for habit, streak, periodicity in habits_longest_streaks:
                        if periodicity == 'Daily':
                            print(f"{habit:<20} {streak} day(s)")
                        else:
                              print(f"{habit:<20} {streak} week(s)")

                    print()  # Add empty space after the table for better readability


                elif choice == "Longest run streak for a given habit":
                    name = questionary.rawselect(
                        "Chose habit for calculation of longest run streak or RETURN to exit to main menu",
                        choices=stored_habit_names + ["RETURN"]).ask()
                    longest_streak_data = get_longest_streak(db,name)
                    longest_streak, timestamp_longest_streak = longest_streak_data[0]
                    timestamp_longest_streak = datetime.strptime(timestamp_longest_streak, "%Y-%m-%d %H:%M:%S").date()

                    periodicity = get_periodicity(db,name)
                    print()
                    if periodicity == 'Daily':
                        print(f"Longest run streak for '{name}' is {longest_streak} day(s) and ended on {timestamp_longest_streak}")
                    elif periodicity == 'Weekly':
                        print(f"Longest run streak for '{name}' is {longest_streak} week(s) and ended on {timestamp_longest_streak}")
                    print()  # Add empty space after the table for better readability




                #break



        else:
            stop = True

    db.close()


if __name__ == "__main__":
    cli()

