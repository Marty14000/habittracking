import sqlite3
from datetime import datetime


def get_db(name='habit_prod.db'):
    """
    Connects to an SQLite database file and ensures that the necessary tables exist.

    This function establishes a connection to the specified SQLite database file.
    If the database file or tables do not exist, it creates them.

    :param name: The name of the SQLite database file to connect to
                 (default is 'habit_prod.db').
    :type name: str
    :return: A connection object to the SQLite database.
    :rtype: sqlite3.Connection
    """
    db = sqlite3.connect(name)
    create_tables(db)
    return db


def create_tables(db):
    """
    Create the necessary database tables if they do not exist, and populate
    them with sample data if not already present. The function ensures the
    establishment of two tables `habit` and `event`. It also populates these
    tables with preset habits and corresponding events, initializing them
    if they do not already exist in the database.

    :param db: SQLite database connection object.
    :type db: sqlite3.Connection
    :return: None
    """
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

    # Insert sample data if not already present
    sample_habits_data = [
        ('Exercise', 'Weekly physical activity', 'Weekly', '2025-03-01 00:00:00'),
        ('Reading', 'Read a book', 'Daily', '2025-03-01 00:00:00')
    ]
    for habit in sample_habits_data:
        c.execute("SELECT COUNT(*) FROM habit WHERE name = ?", (habit[0],))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO habit (name, description, periodicity,creationTimestamp) VALUES (?,?,?,?)", habit)

    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sample_events_data = [
        ('Exercise', 2, 3, '2025-04-01 00:00:00', '2025-03-23 00:00:00'),
        ('Reading', 20, 8, '2025-04-20 00:00:00', '2025-04-10 00:00:00')
    ]
    for event in sample_events_data:
        c.execute("SELECT COUNT(*) FROM event WHERE habitName = ?", (event[0],))
        if c.fetchone()[0] == 0:
            c.execute(
                "INSERT INTO event (habitName, currentStreak, longestStreak, timestamp, timestampLongestStreak) "
                "VALUES (?,?,?,?,?)",
                event)

    db.commit()


def add_habit(db, name, description, periodicity, creation_date=None):
    """
    Adds a new habit to the database. This includes both creating an entry in the
    habit table with the provided name, description, and periodicity, and initializing
    the related event table for tracking the habit's progress.

    This function commits the changes to the database immediately after insertion.
    If a habit with the same name already exists, this function will print an error
    message and return without making changes. Exception never occurs currently as
    habits have to be chosen from predefined list.

    :param db: A SQLite database connection object
    :param name: Name of the habit to be added
    :param description: A short description of the habit
    :param periodicity: The periodicity of the habit (e.g., daily, weekly)
    :return: None
    """
    c = db.cursor()
    while True:
        try:
            creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO habit (name, description, periodicity, creationTimestamp) VALUES (?,?,?,?)",
                      (name, description, periodicity,creation_date))
            timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            c.execute("INSERT INTO event (habitName, currentStreak, timestamp, longestStreak, timestampLongestStreak) "
                      "VALUES (?,?,?,?,?)", (name, 0, timestamp, 0, timestamp))
            db.commit()
        except sqlite3.IntegrityError:
            print("Habit already exists, please choose another name")

        break


def checkoff_habit(db, name):
    """
    Updates the habit entry in the event table.
    In case of streak is ok: currentStreak is increased by 1 and timestamp is updated.
    Additionally, longestStreak is updated if currentStreak is greater than longestStreak.
    In case streak is not ok, only timestamp is updated.

    :param db: A database connection object used to execute queries and commit
        changes.
    :param name: The name of the habit to check off in the database.
    :return: None
    """
    c = db.cursor()
    timestamp = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Timestamp: {timestamp}")
    if check_streak(db, name):
        """
        Increase current streak, update current timestamp and
        additionally in case current streak exceeds former longest streak: 
        copy current streak to longest streak
        """
        c.execute("""
            UPDATE event SET currentStreak = currentStreak + 1, timestamp = ? WHERE habitName = ?
            AND timestamp = (SELECT MAX(timestamp) FROM event WHERE habitName = ?)""", (timestamp, name, name))
        c.execute("""UPDATE event SET longestStreak = currentStreak, timestampLongestStreak = timestamp WHERE 
        habitName = ? AND longestStreak < currentStreak""",
                  (name,))

    else:
        # set current streak (back) to 1 and update current timestamp
        c.execute("""UPDATE event SET timestamp = ?, currentStreak = 1 WHERE habitName = ?
            AND timestamp = (SELECT MAX(timestamp) FROM event WHERE habitName = ?)""", (timestamp, name, name))
    db.commit()


def get_habit_events(db, name):
    """
    Retrieve all events associated with a specific habit from the database.

    This function queries the database to fetch all rows from the `event` table
    where the habit name matches the provided name. The retrieved data represents
    all events related to the habit in question.
    As of current DB specification only one row is expected

    :param db: The database connection object used to execute the query.
    :type db: sqlite3.Connection
    :param name: The name of the habit for which events are to be retrieved.
    :type name: str
    :return: A list of rows from the `event` table corresponding to the specified habit.
    :rtype: list
    """
    c = db.cursor()
    c.execute("SELECT * FROM event WHERE habitName = ?", (name,))
    return c.fetchall()


def check_streak(db, name):
    """
    Check the streak status of a habit based on its periodicity and last checkoff timestamp.

    Streak is considered TRUE for cases where habit not been checked off up to now
    or date difference matches defined periodicity.

    :param db: Database connection object used to query habit and event data.
    :type db: sqlite3.Connection
    :param name: Name of the habit to be checked for streak compliance.
    :type name: str
    :return: A boolean indicating whether the streak is ok.
    :rtype: bool
    """
    streak_ok = False
    now = datetime.now()

    c = db.cursor()
    c.execute("SELECT periodicity FROM habit WHERE name = ?", (name,))
    periodicity = c.fetchone()[0]
    c.execute("SELECT MAX(timestamp) FROM event WHERE habitName = ?", (name,))
    max_timestamp = c.fetchone()[0]
    c.execute("SELECT currentStreak FROM event WHERE habitName = ?", (name,))
    current_streak = c.fetchone()[0]
    last_timestamp = datetime.strptime(max_timestamp, "%Y-%m-%d %H:%M:%S")
    last_day = last_timestamp.day
    time_difference = now.day - last_day

    if current_streak == 0:
        streak_ok = True

    elif periodicity == "Daily":
        if time_difference == 1:
            streak_ok = True

    elif periodicity == "Weekly":
        if time_difference == 7:
            streak_ok = True
    return streak_ok


"""def get_habits(db):
    c = db.cursor()
    c.execute("SELECT distinct(name) FROM habit order by name")
    return c.fetchall()"""

def get_habits(db):
    c = db.cursor()
    c.execute("SELECT name, description, periodicity, creationTimestamp FROM habit order by name")
    return c.fetchall()

def get_longest_streaks(db: sqlite3.Connection) -> list:
    c = db.cursor()
    c.execute(
        "SELECT habitName, longestStreak, periodicity FROM event INNER JOIN habit ON event.habitName = habit.name "
        "ORDER BY longestStreak DESC, habitName ASC")
    return c.fetchall()


def get_longest_streak(db, name):
    c = db.cursor()
    c.execute("SELECT longestStreak, timestampLongestStreak FROM event WHERE habitName = ?", (name,))
    return c.fetchall()


def get_periodicity(db, name):
    """
    Retrieves the periodicity of a habit based on its name from the database.

    This function queries the provided database connection for the periodicity
    of a habit that matches the given name. If the habit is found, the function
    returns its periodicity value.

    :param db: Database connection object
    :type db: Any
    :param name: The name of the habit whose periodicity is to be retrieved
    :type name: str
    :return: The periodicity of the habit
    :rtype: str
    """
    c = db.cursor()
    c.execute("SELECT periodicity FROM habit WHERE name = ?", (name,))
    return c.fetchone()[0]
