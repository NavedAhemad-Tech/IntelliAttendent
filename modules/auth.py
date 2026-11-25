import bcrypt
from database import get_connection

# step 1 : Hash password before storing it in mysql
def hash_password(password):

    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")

# Step 2 : Verify entered passwor during login
def verify_password(password,stored_hash):

    password_bytes = password.encode("utf-8")
    stored_hash_bytes = stored_hash.encode("utf-8")

    return bcrypt.checkpw(
        password_bytes,
        stored_hash_bytes
    )


def authenticate_user(username, password):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                SELECT
                    u.user_id,
                    u.employee_id,
                    u.username,
                    u.password_hash,
                    u.is_active,
                    r.role_name,
                    e.employee_name
                    FROM users u
                    LEFT JOIN roles r
                    ON u.role_id = r.role_id
                    LEFT JOIN employees e
                    ON u.employee_id = e.employee_id
                    WHERE u.username = %s
                    """, (username,))

        user = cursor.fetchone()

        if user is None:
            return None

        if not user["is_active"]:
            return None

        if verify_password(password, user["password_hash"]):
            return {
                 "user_id": user["user_id"],
                "employee_id": user["employee_id"],
                "username": user["username"],
                "role": user["role_name"],
                "employee_name": user["employee_name"]
}
        return None

    except Exception as error:
        print("Authentication Error:", error)
        return None

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
