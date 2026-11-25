
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
