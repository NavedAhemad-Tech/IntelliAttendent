
from database import get_connection
from modules.auth import hash_password

username = "hr"
password = "HR@123"

connection = get_connection()
cursor = connection.cursor()

try:
    cursor.execute(
        "SELECT user_id FROM users WHERE username = %s",
        (username,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        print("HR account already exists.")

    else:
        cursor.execute(
            "SELECT role_id FROM roles WHERE role_name = %s",
            ("HR",)
        )

        role = cursor.fetchone()

        if role is None:
            print("HR role not found.")

        else:
            password_hash = hash_password(password)

            cursor.execute("""
                INSERT INTO users
                (role_id, username, password_hash)
                VALUES (%s, %s, %s)
            """, (role[0], username, password_hash))

            connection.commit()
            print("HR account created successfully!")

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
