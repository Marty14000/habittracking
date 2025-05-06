import os
import time
import pytest
from habit import Habit
from db import get_db, checkoff_habit, get_habit_events, get_longest_streak, check_streak


@pytest.fixture(scope='function', autouse=True)
def delete_sqlite_file():
    """
    Fixture to remove used SQLite DB test file for clean tests.
    Removal (or check for file) is done before and after each test.
    """
    db_path = 'habit_test.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    yield
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
    except PermissionError:
        # Delay due to Windows file lock
        time.sleep(0.1)
        if os.path.exists(db_path):
            os.remove(db_path)


def test_store_habit():
    """
    Tests the functionality of storing a habit into the database and verifying its
    existence.
    """
    db = get_db('habit_test.db')
    habit = Habit("New_habit", "New_description", "Daily", "2025-01-01 00:00:00")
    habit.store(db)
    stored_habits = [habit[0] for habit in db.execute("SELECT name FROM habit").fetchall()]
    assert "New_habit" in stored_habits
    db.close()


def test_checkoff_habit():
    """
    Tests the functionality of habit check-off and event recording.
    """
    db = get_db('habit_test.db')
    habit = Habit("Checkoff_habit", "Checkoff ", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    habit.check_off(db)
    events = get_habit_events(db, "Checkoff_habit")
    checked_off_events = [("Checkoff_habit", 1, 1)]
    fetched_events = [(event[0], event[1], event[2]) for event in events]
    assert checked_off_events == fetched_events
    db.close()


def test_check_streak():
    """
    Tests the check_streak function.
    """
    db = get_db('habit_test.db')
    habit = Habit("Streakcheck_habit", "Streak_description", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    assert check_streak(db, "Streakcheck_habit")
    db.close()


def test_get_longest_streak():
    """
    Tests the functionality of the `get_longest_streak` function to ensure it correctly retrieves
    the longest streak of a habit.
    """
    db = get_db('habit_test.db')
    habit = Habit("Streak_habit", "Streak_description", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    checkoff_habit(db, "Streak_habit")
    longest_streak = get_longest_streak(db, "Streak_habit")
    assert longest_streak[0][0] == 1
    db.close()
