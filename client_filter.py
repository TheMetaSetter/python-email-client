# Standard library imports
import json
import mailbox

# Local application imports
from utilities import load_config

class filter_rule:
    def __init__(self, rule):
        self.from_addresses = rule.get('From', [])
        self.subject_keywords = rule.get('Subject', [])
        self.content_keywords = rule.get('Content', [])
        self.spam_keywords = rule.get('Spam', [])
        self.to_folder = rule.get('ToFolder', 'Inbox')

class email_filter:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return [filter_rule(rule) for rule in config.get('Filter', [])]
        self.config = load_config(config_file_path)

    def extract_email_info_from_mbox_file(self, mbox_file_path):
        email_info = {'From': '', 'To': '', 'Subject': '', 'Content': ''}

        mbox = mailbox.mbox(mbox_file_path)

        for message in mbox:
            try:
                email_info['From'] = message.get('From', '')
                email_info['To'] = message.get('To', '')
                email_info['Subject'] = message.get('Subject', '')

                if message.is_multipart():
                    for part in message.walk():
                        content_type = part.get_content_type()
                        if content_type == 'text/plain':
                            email_info['Content'] += part.get_payload(decode=True).decode('utf-8', errors='ignore') + ' '
            except Exception as e:
                print(f"Error extracting email info: {e}")

        return email_info

    def classify_email(self, mbox_file_path):
        # Gọi hàm extract_email_info_from_mbox_file để lấy thông tin email
        email = self.extract_email_info_from_mbox_file(mbox_file_path)

        sender = email['From']
        subject = email['Subject']
        content = email['Content']

        for filter_rule in self.config:
            if filter_rule.from_addresses and any(addr in sender for addr in filter_rule.from_addresses):
                return filter_rule.to_folder
            if filter_rule.subject_keywords and any(keyword in subject for keyword in filter_rule.subject_keywords):
                return filter_rule.to_folder
            if filter_rule.content_keywords and any(keyword in content for keyword in filter_rule.content_keywords):
                return filter_rule.to_folder
            if filter_rule.spam_keywords and any(keyword in subject or keyword in content for keyword in filter_rule.spam_keywords):
                return filter_rule.to_folder

        return "Inbox"