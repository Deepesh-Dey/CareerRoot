#auth utilities for password validation and helpers

import re
from werkzeug.security import generate_password_hash, check_password_hash

def validate_password_strength(password):
    #Validate password strength (min 8 chars, at least 1 uppercase, 1 number, 1 special char.)
    #Returns: (is_valid, error_message)
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Password must contain at least one special character (!@#$%^&*...)"
    
    return True, None

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
