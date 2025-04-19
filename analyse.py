from db import get_longest_streaks

def calculate_longest_streaks(db)   :
    habits_longest_streaks = get_longest_streaks(db)
    return habits_longest_streaks
