import pytest

from habit import Habit
from db import get_db, add_habit, checkoff_habit, get_habit_events, get_longest_streak, check_streak
from datetime import datetime, timedelta
from unittest.mock import patch



# def test_habit():
#     habit = Habit("Test_habit", "Test_description", "Test_periodicity", "2025-01-01 00:00:00")
#     assert str(habit) == "Test_habit - Test_description - Test_periodicity - 2025-01-01 00:00:00"
# 
# 
# def test_db():
#     db = get_db()
#     # add_habit(db, "habit1", "description1", "periodicity1")
#     checkoff_habit(db, "habit1")
# 
# 
# def test_allevents():
#     db = get_db()
#     events = get_habit_events(db, "habit1")
#     assert len(events) > 0
#     print(events)

# def test_habit_str_representation():
#     habit = Habit("Test_habit", "Test_description", "Test_periodicity", "2025-01-01 00:00:00")
#     assert str(habit) == "Test_habit - Test_description - Test_periodicity - 2025-01-01 00:00:00"
#
#
def test_store_habit():
    db = get_db()
    habit = Habit("New_habit", "New_description", "Daily", "2025-01-01 00:00:00")
    habit.store(db)
    stored_habits = [habit[0] for habit in db.execute("SELECT name FROM habit").fetchall()]
    assert "New_habit" in stored_habits

def test_checkoff_habit():
    db = get_db()
    habit = Habit("Checkoff_habit", "Checkoff ", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    habit.check_off(db)
    events = get_habit_events(db, "Checkoff_habit")
    checked_off_events = [("Checkoff_habit", 1, 1)]
    fetched_events = [(event[0], event[1], event[3]) for event in events]
    assert checked_off_events == fetched_events

def test_check_streak():
    db = get_db()
    habit = Habit("Streakcheck_habit", "Streak_description", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    assert check_streak(db, "Streakcheck_habit")

def test_get_longest_streak():
    db = get_db()
    habit = Habit("Streak_habit", "Streak_description", "Weekly", "2025-01-01 00:00:00")
    habit.store(db)
    checkoff_habit(db, "Streak_habit")
    '''print(datetime.now())

    simulated_date = datetime.now() + timedelta(days=7)
    print(simulated_date)
    with patch("db.datetime") as mock_datetime:
        mock_datetime.now.return_value = simulated_date
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        checkoff_habit(db, "Streak_habit")'''
    longest_streak = get_longest_streak(db, "Streak_habit")
    assert longest_streak[0][0] == 1

def test_streak():
    test_habit_data = [
        ('Test_habit', 'Test_description', 'Weekly', '2025-03-01 00:00:00'),
    ]

    db = get_db()
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM habit WHERE name = ?", (test_habit_data[0],))
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO habit (name, description, periodicity,creationTimestamp) VALUES (?,?,?,?)", test_habit_data)

    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    test_event_data = [
        ('Test_habit', 2, 3, '2025-04-01 00:00:00', '2025-03-23 00:00:00'),
        ]
    c.execute("SELECT COUNT(*) FROM event WHERE habitName = ?", (test_event_data[0],))
    if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO event (habitName, currentStreak, longestStreak, timestamp, timestampLongestStreak) "
                "VALUES (?,?,?,?,?)",
                test_event_data)

    db.commit()




@pytest.fixture
def habit_data():
    return [
        {"name": "habit1", "description": "description1", "periodicity": "daily"},
        {"name": "habit2", "description": "description2", "periodicity": "weekly"},
        {"name": "habit3", "description": "description3", "periodicity": "monthly"}
    ]
