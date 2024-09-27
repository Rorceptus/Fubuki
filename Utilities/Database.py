#LIBRARIES--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
import mysql.connector as mc

#MAIN-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
class Database:
    def __init__(self, host, user, password, database_name):
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self.connection =  None
        self.cursor = None
        self.connect()

    # Connecting or creating databse.
    def connect(self):
        try:
            self.connection = mc.connect(
                host = self.host,
                user = self.user,
                password = self.password
            )
            self.cursor = self.connection.cursor()

            # Creating the database if it doesn't exists.
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
            self.connection.database = self.database_name
            print(f" ✅ Successfully connected to the database '{self.database_name}'.")

            # Creating the tables if it doesn't exists.
            self.create_table()

        except mc.Error as e:
            print(f" ❌ Failed to connect to the database. Error: {e}")

    # Creating required tables.
    def create_table(self):
        try:
            query = """
            CREATE TABLE IF NOT EXISTS members (
                `S.No.` INT AUTO_INCREMENT PRIMARY KEY,
                Name VARCHAR(255) NOT NULL,
                User_Id VARCHAR(255) NOT NULL,
                Join_Time TIME NOT NULL,
                Join_Date DATE NOT NULL
            )
            """

            # Creating the table if it doesn't exist.
            self.cursor.execute(query)
            self.connection.commit()

        except mc.Error as e:
            print(f" ❌ Failed to load the tables. Error: {e}")

    # Inserting new member data into the appropriate table.
    def insert_member(self, name, user_id, join_time, join_date):
        try:
            query = "INSERT INTO members (Name, User_Id, Join_Time, Join_Date) VALUES (%s, %s, %s, %s)"
            values = (name, user_id, join_time, join_date)
            self.cursor.execute(query, values)

            # Inserting member data for new members.
            self.connection.commit()
            print(f" ✅ '{name}' with User ID '{user_id}' joined our server.")

        except mc.Error as e:
            print(f" ❌ Failed to update member data. Error: {e}")
