<<<<<<< HEAD

from modules.auth import hash_password, verify_password


password = "Test@123"

hashed = hash_password(password)

print("Hashed Password:", hashed)

if verify_password(password, hashed):
    print("Login Successful!")

else:
=======

from modules.auth import hash_password, verify_password


password = "Test@123"

hashed = hash_password(password)

print("Hashed Password:", hashed)

if verify_password(password, hashed):
    print("Login Successful!")

else:
>>>>>>> e472b73cc18c70656c4c8f2aeed2fdf84f75f25b
    print("Invalid Password!")