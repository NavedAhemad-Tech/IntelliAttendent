<<<<<<< HEAD

from modules.auth import authenticate_user

username = input("Enter Username: ")
password = input("Enter Password: ")

user = authenticate_user(username, password)

if user:
    print("\nLogin Successful!")
    print("Welcome:", user["username"])
    print("Employee Name:", user["employee_name"])
    print("Role:", user["role"])

else:
    print("\nInvalid Username or Password!")
=======

from modules.auth import authenticate_user

username = input("Enter Username: ")
password = input("Enter Password: ")

user = authenticate_user(username, password)

if user:
    print("\nLogin Successful!")
    print("Welcome:", user["username"])
    print("Employee Name:", user["employee_name"])
    print("Role:", user["role"])

else:
    print("\nInvalid Username or Password!")
>>>>>>> e472b73cc18c70656c4c8f2aeed2fdf84f75f25b
