
from database import get_connection
from modules.auth import hash_password

employee_code = input("Enter Employee Code: ")
username = input("Enter Login Username: ")
password = input("Enter Login Password: ")

connection = get_connection()
cursor = connection.cursor()

try:
    # Find employee
    cursor.execute("""
        SELECT employee_id
        FROM employees
        WHERE employee_code = %s
    """, (employee_code,))

    employee = cursor.fetchone()

    if employee is None:
        print("Employee not found!")

    else:
        employee_id = employee[0]

        # Get Employee role
        cursor.execute("""
            SELECT role_id
            FROM roles
            WHERE role_name = %s
        """, ("Employee",))

        role = cursor.fetchone()

        if role is None:
            print("Employee role not found!")

        else:
            password_hash = hash_password(password)

            cursor.execute("""
                INSERT INTO users
                (employee_id, role_id, username, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (
                employee_id,
                role[0],
                username,
                password_hash
            ))

            connection.commit()
            print("Employee login created successfully!")

except Exception as error:
    connection.rollback()
    print("Error:", error)

finally:
    cursor.close()
    connection.close()
