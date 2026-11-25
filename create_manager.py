<<<<<<< HEAD

from database import get_connection
from modules.auth import hash_password

username = "manager"
password = "Manager@123"

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "SELECT user_id FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print("Manager account already exists.")

    else:
        cursor.execute(
            "SELECT role_id FROM roles WHERE role_name = %s",
            ("Manager",)
        )

        role = cursor.fetchone()

        if role is None:
            print("Manager role not found.")

        else:
            password_hash = hash_password(password)

            cursor.execute("""
                INSERT INTO users
                (role_id, username, password_hash)
                VALUES (%s, %s, %s)
            """, (role[0], username, password_hash))

            connection.commit()
            print("Manager account created successfully!")

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
=======

from database import get_connection
from modules.auth import hash_password

username = "manager"
password = "Manager@123"

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "SELECT user_id FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print("Manager account already exists.")

    else:
        cursor.execute(
            "SELECT role_id FROM roles WHERE role_name = %s",
            ("Manager",)
        )

        role = cursor.fetchone()

        if role is None:
            print("Manager role not found.")

        else:
            password_hash = hash_password(password)

            cursor.execute("""
                INSERT INTO users
                (role_id, username, password_hash)
                VALUES (%s, %s, %s)
            """, (role[0], username, password_hash))

            connection.commit()
            print("Manager account created successfully!")

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
>>>>>>> e472b73cc18c70656c4c8f2aeed2fdf84f75f25b
