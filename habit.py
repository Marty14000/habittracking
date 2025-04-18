from db import add_habit, checkoff_habit


class Habit:
    def __init__(self, name: str, description = None ,periodicity = None):
        self.name = name
        self.description = description
        self.periodicity = periodicity

    def __str__(self):
        return f"{self.name} - {self.description} - {self.periodicity}"

    def store(self, db):
        add_habit(db, self.name, self.description, self.periodicity) # add_habit(db, name, description, periodicity)
        #add_habit(db, self.name, self.description, self.periodicity) # add_habit(db, name, description, periodicity)

    def check_off(self, db):
        checkoff_habit(db, self.name)

    def streak_ok(self,db):
        pass
