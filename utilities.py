# Standard library imports
import re
import json

# Local application imports
from filter_rule import filter_rule

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

def load_config(self, config_file_path: str):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return [filter_rule(rule) for rule in config.get('Filter', [])]