import json

def load_config(config_file_path):
    with open(config_file_path, 'r') as config_file:
        config = json.load(config_file)
    return config

def classify_email(email, config):
    sender = email['sender']
    subject = email['subject']
    content = email['content']

    for filter_rule in config['Filter']:
        if 'From' in filter_rule and any(addr in sender for addr in filter_rule['From']):
            return filter_rule['ToFolder']
        if 'Subject' in filter_rule and any(keyword in subject for keyword in filter_rule['Subject']):
            return filter_rule['ToFolder']
        if 'Content' in filter_rule and any(keyword in content for keyword in filter_rule['Content']):
            return filter_rule['ToFolder']
        if 'Spam' in filter_rule and any(keyword in subject or keyword in content for keyword in filter_rule['Spam']):
            return filter_rule['ToFolder']

    # Default folder: Inbox
    return 'Inbox'


def save_to_folder(email, folder):
    print(f"Saving email to folder: {folder}")

config_file_path = 'config.json'

# Have to make a layer comparision i guess
email_info = {
    'sender' : 'example@testing.com',
    'subject' : 'nah',
    'content' : 'This is an virus news'
}

config = load_config(config_file_path)
category = classify_email(email_info, config)
save_to_folder(email_info, category)





# configResult = load_config("config.json")

# name = configResult["General"]["Username"]
# passWord = configResult["General"]["Password"]

# print(f"User name: {name}")
# print(f"Password: {passWord}")

