import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta

class AuthManager:
    def __init__(self, auth_file='auth.json'):
        self.auth_file = auth_file
        self.users = {}
        self.load_users()

    def load_users(self):
        """Load users from JSON file. Create default admin if missing."""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r') as f:
                    self.users = json.load(f)
            except Exception:
                self.users = {}
        
        # Ensure Admin exists (Default)
        if 'admin' not in self.users:
            # Use Env Var or Default Placeholder (User changed)
            def_admin_pass = os.environ.get('API650_ADMIN_PASS', 'ChangeMeAdmin!')
            self.create_user('admin', def_admin_pass, role='admin')
        
        # Ensure Default User exists
        if 'user' not in self.users:
            # Expires in 30 days
            def_user_pass = os.environ.get('API650_USER_PASS', 'ChangeMeUser!')
            self.create_user('user', def_user_pass, role='user', days_valid=30)

    def save_users(self):
        """Save users to JSON file."""
        with open(self.auth_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def hash_password(self, password, salt=None):
        """Hash password using SHA256 and salt."""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Combine salt and password
        salted_pass = salt + password
        hashed = hashlib.sha256(salted_pass.encode()).hexdigest()
        return hashed, salt

    def create_user(self, username, password, role='user', days_valid=30):
        """Create or Reset a user."""
        hashed, salt = self.hash_password(password)
        
        expiry_date = None
        if days_valid:
            expiry_date = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
            
        self.users[username] = {
            'password_hash': hashed,
            'salt': salt,
            'role': role,
            'full_name': 'Administrator' if role == 'admin' else 'Standard User',
            'created_at': datetime.now().strftime("%Y-%m-%d"),
            'expires_at': expiry_date
        }
        self.save_users()
        return True

    def check_login(self, username, password):
        """
        Verify credentials.
        Returns: (success: bool, message: str, role: str)
        """
        if username not in self.users:
            return False, "User not found", None
            
        user_data = self.users[username]
        
        # Check Password
        hashed_input, _ = self.hash_password(password, salt=user_data['salt'])
        if hashed_input != user_data['password_hash']:
            return False, "Details incorrect (Password)", None
            
        # Check Expiration (Skip for Admin)
        if user_data['role'] != 'admin':
            expiry_str = user_data.get('expires_at')
            if expiry_str:
                expiry_dt = datetime.strptime(expiry_str, "%Y-%m-%d")
                if datetime.now() > expiry_dt + timedelta(days=1): # Allow until end of day
                    return False, f"Account expired on {expiry_str}. Contact Admin.", None
        
        return True, "Login Successful", user_data['role']

    def update_password(self, username, new_password):
        """Update password for a user."""
        if username in self.users:
            hashed, salt = self.hash_password(new_password)
            self.users[username]['password_hash'] = hashed
            self.users[username]['salt'] = salt
            self.save_users()
            return True
        return False

    def renew_user(self, username, days=30):
        """Extend user validity."""
        if username in self.users:
            expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            self.users[username]['expires_at'] = expiry_date
            self.save_users()
            return True
        return False

    def get_all_users(self):
        """Return dict of users (excluding sensitive hash for display logic)."""
        # Return deep copy or filtered list
        safe_list = {}
        for u, v in self.users.items():
            safe_list[u] = {
                'role': v['role'],
                'expires_at': v.get('expires_at', 'Never'),
                'full_name': v.get('full_name', '')
            }
        return safe_list

if __name__ == "__main__":
    # Initialize
    am = AuthManager()
    print("Auth Initialized. Users:", am.users.keys())
