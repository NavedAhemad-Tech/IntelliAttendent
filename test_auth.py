
from modules.auth import hash_password, verify_password


password = "Test@123"

hashed = hash_password(password)

print("Hashed Password:", hashed)

if verify_password(password, hashed):
    print("Login Successful!")

else:
    print("Invalid Password!")