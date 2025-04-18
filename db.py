import sqlite3
from datetime import datetime, timedelta



def get_db(name='habit_prod.db'):
    db = sqlite3.connect(name)
    create_tables(db)
    return db


def create_tables(db):
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS habit (
        name text UNIQUE PRIMARY KEY,
        description text,
        periodicity text)""")
    c.execute("""CREATE TABLE IF NOT EXISTS event (
        habitName text,
        currentStreak integer DEFAULT 0,
        longestStreak integer DEFAULT 0,
        timestamp text,
        timestampLongestStreak text,
        FOREIGN KEY(habitName) REFERENCES habit(name))""")
    db.commit()


def add_habit(db, name, description, periodicity):
    c = db.cursor()
    while True:
        try:
            c.execute("INSERT INTO habit (name, description, periodicity) VALUES (?,?,?)", (name, description, periodicity))
            timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            c.execute("INSERT INTO event (habitName, currentStreak, timestamp, longestStreak, timestampLongestStreak) VALUES (?,?,?,?,?)", (name, 0, timestamp,0,timestamp))
            db.commit()
        except sqlite3.IntegrityError:
            print("Habit already exists, please choose another name")

        break



def checkoff_habit(db, name):
    c = db.cursor()
    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if check_streak(db, name):
        c.execute("""
            UPDATE event SET currentStreak = currentStreak + 1, timestamp = ? WHERE habitName = ?
            AND timestamp = (SELECT MAX(timestamp) FROM event WHERE habitName = ?)""", (timestamp, name, name))
        c.execute("""
            UPDATE event SET longestStreak = currentStreak, timestampLongestStreak = timestamp WHERE habitName = ? AND longestStreak < currentStreak""", (name,))
    #c.execute("UPDATE event SET currentStreak = currentStreak + 1, timestamp = ? WHERE habitName = ? and "
              #"timestamp = (SELECT MAX(timestamp) from event)", (timestamp, name))

    else:
        c.execute("""UPDATE event SET timestamp = ? WHERE habitName = ?
            AND timestamp = (SELECT MAX(timestamp) FROM event WHERE habitName = ?)""", (timestamp, name, name))
    db.commit()


def get_habit_events(db, name):
    c = db.cursor()
    c.execute("SELECT * FROM event WHERE habitName = ?", (name,))
    return c.fetchall()

def check_streak(db, name):
    streak_ok = False
    now = datetime.now()

    c = db.cursor()
    c.execute("SELECT periodicity FROM habit WHERE name = ?", (name,))
    periodicity = c.fetchone()[0]
    c.execute("SELECT MAX(timestamp) FROM event WHERE habitName = ?", (name,))
    max_timestamp = c.fetchone()[0]
    c.execute("SELECT currentStreak FROM event WHERE habitName = ?", (name,))
    currentStreak = c.fetchone()[0]
    last_timestamp = datetime.strptime(max_timestamp, "%Y-%m-%d %H:%M:%S")
    last_day = last_timestamp.day
    time_difference = now.day - last_day

    if periodicity == "Daily":
        if time_difference == 1 or (time_difference == 0 and currentStreak == 0):
            streak_ok = True

    elif periodicity == "Weekly":
        if time_difference == 7 or (time_difference < 7 and currentStreak == 0):
            streak_ok = True
    return streak_ok

def get_habits(db):
    c = db.cursor()
    c.execute("SELECT distinct(name) FROM habit order by name")
    return c.fetchall()

def get_longest_streaks(db):
    c = db.cursor()
    c.execute("SELECT habitName, longestStreak, periodicity FROM event INNER JOIN habit ON event.habitName = habit.name ORDER BY longestStreak DESC, habitName ASC")
    return c.fetchall()

def get_longest_streak(db,name):
    c = db.cursor()
    c.execute("SELECT longestStreak, timestampLongestStreak FROM event WHERE habitName = ?", (name,))
    return c.fetchall()

def get_periodicity(db,name):
    c = db.cursor()
    c.execute("SELECT periodicity FROM habit WHERE name = ?", (name,))
    return c.fetchone()[0]


