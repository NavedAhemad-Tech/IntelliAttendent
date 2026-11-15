from database import get_connection
from pages import employees

try:
    connection = get_connection()

    if connection.is_connected():
        print("MySQL Connected Successfully!")

        cursor = connection.cursor()

        cursor.execute("SHOW TABLES")

        tables = cursor.fetchall()

        print("Available Tables:")

        for table in tables:
            print(table[0])

        cursor.close()
        connection.close()

except Exception as error:
    print("Database Connection Failed:", error)


