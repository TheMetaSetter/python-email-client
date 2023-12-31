# Standard library imports
import json
import mailbox

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

    def classify_email(self, email: mailbox.mboxMessage):
        sender = email.get('From', '').lower()
        subject = email.get('Subject', '').lower()
        payload = email.get_payload()

        if isinstance(payload, list) and payload:
            # If there are multiple parts, assume the first part is the text/plain part
            text_part = payload[0]
            content = text_part.get_payload().lower()
        elif isinstance(payload, str):
            # If there is only one part, treat it as the text/plain part
            content = payload.lower()
        else:
            content = ""
            
        for filter_rule in self.config:
            if filter_rule.from_addresses and any(addr in sender for addr in filter_rule.from_addresses):
                return filter_rule.to_folder
            if filter_rule.subject_keywords and any(keyword in subject for keyword in filter_rule.subject_keywords):
                return filter_rule.to_folder
            if filter_rule.content_keywords and any(keyword in content for keyword in filter_rule.content_keywords):
                return filter_rule.to_folder
            if filter_rule.spam_keywords and any(keyword in subject or keyword in content for keyword in filter_rule.spam_keywords):
                return filter_rule.to_folder
            
        return 'Inbox'