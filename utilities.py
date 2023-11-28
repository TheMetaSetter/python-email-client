import re

def add_angle_brackets(string: str) -> str:
    return "<" + string + ">"

def is_valid_email(email):
    # Define the pattern for an email
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    
    # Use the match method to check if the email matches the pattern
    if re.match(pattern, email):
        return True
    else:
        return False
