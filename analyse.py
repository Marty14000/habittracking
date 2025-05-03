from db import get_longest_streaks, get_longest_streak, get_periodicity
from datetime import datetime


def calculate_longest_streaks(db):
    """
    Return the longest streaks for habits stored in the database.

    Retrieves the longest streaks of habits
    and returns the streak data.

    :param db: Database connection.
    :return: Streak data
    :rtype list"""
    habits_longest_streaks = get_longest_streaks(db)
    return habits_longest_streaks


def longest_streak_per_habit(db, name):
    """
    Display the longest streak for a habit defined by its name.

    Retrieves data about the longest streak for a habit stored in the database
    and prints this date formatted depending on the periodicity of the habit (Daily or Weekly).

    :param db: Database connection.
    :param name: Name of the habit for which the longest streak is calculated.
    :return: None
    """
    longest_streak_data = get_longest_streak(db, name)
    longest_streak, timestamp_longest_streak = longest_streak_data[0]
    timestamp_longest_streak = datetime.strptime(timestamp_longest_streak, "%Y-%m-%d %H:%M:%S").date()
    periodicity = get_periodicity(db, name)
    print()
    if periodicity == 'Daily':
        print(f"\033[96mLongest run streak for '{name}' is {longest_streak} day(s) and was reached on"
              f" {timestamp_longest_streak}\033[0m")
    elif periodicity == 'Weekly':
        print(f"\033[96mLongest run streak for '{name}' is {longest_streak} week(s) and was reached on"
              f" {timestamp_longest_streak}\033[0m")
