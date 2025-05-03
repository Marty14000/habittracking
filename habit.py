from db import add_habit, checkoff_habit


class Habit:
    """
    Represents a habit that can be stored, tracked, and checked off.

    This class models a habit with a name, description, and
    periodicity. It provides methods to store the habit in a database
    and mark it as completed for the current period.

    :ivar name: The name of the habit.
    :ivar description: A brief description of the habit.
    :ivar periodicity: The periodicity of the habit (Daily, Weekly).
    """
    def __init__(self, name: str, description=None, periodicity=None, creation_date=None):
        self.name = name
        self.description = description
        self.periodicity = periodicity
        self.creation_date = creation_date

    def __str__(self):
        return f"{self.name} - {self.description} - {self.periodicity} - {self.creation_date}"

    def store(self, db):
        """
        Stores the current habit information into the database.

        This method takes the habit attributes and calls the `add_habit` function
        to store the habit details, such as name, description, periodicity, and
        creation date, into the provided database.

        :param db: DB instance where the habit details are stored.
        :type db: Any
        :return: None
        """
        add_habit(db, self.name, self.description, self.periodicity, self.creation_date)

    def check_off(self, db):
        """
        Mark a habit as checked off. This function calls the `checkoff_habit` function
        to update the event table in the database.

        :param db: DB instance where the habit details are stored.
        :type db: object
        """
        checkoff_habit(db, self.name)
