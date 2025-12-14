
from AuthManager import AuthManager
import os

def test_auth():
    print("Testing AuthManager...")
    if os.path.exists("auth.json"):
        os.remove("auth.json") # Start fresh
        
    am = AuthManager("auth.json")
    print("Initialized. Users:", am.users.keys())
    
    # Check Admin
    success, msg, role = am.check_login("admin", "ChangeMeAdmin!")
    print(f"Login Admin (Default): {success} - {msg} - {role}")
    
    # Create User
    ret = am.create_user("newuser", "user123", role="user")
    print(f"Create User 'newuser': {ret}")
    
    # Login User
    success, msg, role = am.check_login("newuser", "user123")
    print(f"Login New User: {success} - {msg} - {role}")
    
    # Verify File
    import json
    with open("auth.json") as f:
        data = json.load(f)
        print("Auth File Content Keys:", data.keys())

if __name__ == "__main__":
    test_auth()
