from habit import Habit
from db import get_db, add_habit, checkoff_habit, get_habit_events


def test_habit():
    habit = Habit("habit", "description", "periodicity")
    assert str(habit) == "habit - description - periodicity"


def test_db():
    db = get_db()
    # add_habit(db, "habit1", "description1", "periodicity1")
    checkoff_habit(db, "habit1")


def test_allevents():
    db = get_db()
    events = get_habit_events(db, "habit1")
    assert len(events) > 0
    print(events)
