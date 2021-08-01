
class user:
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password



class users:
    #constructor
    def __init__(self, conn):
        self._conn = conn

    def add(self, user):
        self._conn.execute("""INSERT INTO users (first_name, last_name, email, password) VALUES (?,?,?,?)""",
                           [user.first_name, user.last_name, user.email, user.password])


    def usersFirst_Name(self, name):
        this = self._conn.cursor()
        output1 = this.execute("SELECT * FROM users WHERE users.first_name=?", [name])
        output = this.fetchone()

        return output

    def usersLast_Name(self, name):
        this = self._conn.cursor()
        this.execute("SELECT * FROM users WHERE users.last_name=?", [name])
        output = this.fetchone()[0]

        return output

    def usersPassword(self, password):
        this = self._conn.cursor()
        this.execute("SELECT * FROM users WHERE users.country=?", [password])
        output = this.fetchone()[0]

        return output

    def users_email(self, email):
        this = self._conn.cursor()
        this.execute("SELECT * FROM users WHERE users.email=?", [email])
        output = this.fetchone()[0]

        return output

import sqlite3





