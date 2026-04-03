# Form validation utilities for all endpoints
import re

def validate_email(email):
    # Check if email format is valid using regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    # Username must be 3-20 characters, alphanumeric and underscore only
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters long"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscore"
    return True, None

def validate_password_length(password):
    # Check if password meets minimum length requirement
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, None

def validate_phone(phone):
    # Phone must be 10 digits
    if not phone:
        return True, None  # Phone is optional
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) != 10:
        return False, "Phone number must contain 10 digits"
    return True, None

def validate_cgpa(cgpa):
    # CGPA must be between 0 and 10
    try:
        cgpa_float = float(cgpa)
        if cgpa_float < 0 or cgpa_float > 10:
            return False, "CGPA must be between 0 and 10"
        return True, None
    except:
        return False, "CGPA must be a valid number"

def validate_company_name(name):
    # Company name must be 2-100 characters
    if len(name) < 2 or len(name) > 100:
        return False, "Company name must be 2-100 characters"
    return True, None

def validate_job_title(title):
    # Job title must be 3-50 characters
    if len(title) < 3 or len(title) > 100:
        return False, "Job title must be 3-100 characters"
    return True, None

def validate_salary(salary):
    # Salary must be a positive number
    try:
        sal = float(salary)
        if sal <= 0:
            return False, "Salary must be greater than 0"
        return True, None
    except:
        return False, "Salary must be a valid number"

def sanitize_input(text):
    # Remove potentially dangerous characters from user input
    if not text:
        return text
    # Remove HTML tags and script tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def validate_url(url):
    # Check if URL is in valid format
    if not url:
        return True, None  # URL is optional
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        return False, "Please enter a valid URL starting with http:// or https://"
    return True, None

def validate_name(name):
    # Name should contain only letters and spaces
    if len(name) < 2 or len(name) > 50:
        return False, "Name must be 2-50 characters"
    if not re.match(r'^[a-zA-Z\s]+$', name):
        return False, "Name should contain only letters and spaces"
    return True, None

def validate_required_field(field, field_name):
    # Check if required field is not empty
    if not field or not str(field).strip():
        return False, f"{field_name} is required"
    return True, None

def validate_hr_contact(hr_contact):
    # HR contact name - just check length, allow any printable characters
    if len(hr_contact) < 2 or len(hr_contact) > 50:
        return False, "HR contact must be 2-50 characters"
    return True, None
