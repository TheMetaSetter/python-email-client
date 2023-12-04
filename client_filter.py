import json
import mailbox

class email_filter:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return config

    def extract_email_info_from_mbox_file(self, mbox_file_path):
        email_info = {'From': '', 'To': '', 'Subject': '', 'Content': ''}

        mbox = mailbox.mbox(mbox_file_path)

        for message in mbox:
            # Extract 'From' address
            if 'From' in message:
                email_info['From'] = message['From']

            # Extract 'To' addresses
            if 'To' in message:
                email_info['To'] = message['To']

            # Extract 'Subject'
            if 'Subject' in message:
                email_info['Subject'] = message['Subject']

            # Extract 'Content'
            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        email_info['Content'] += part.get_payload(decode=True).decode('utf-8', errors='ignore') + ' '

        return email_info

    def classify_email(self, email):
        sender = email['From']
        subject = email['Subject']
        content = email['Content']

        for filter_rule in self.config['Filter']:
            if 'From' in filter_rule and any(addr in sender for addr in filter_rule['From']):
                return filter_rule['ToFolder']
            if 'Subject' in filter_rule and any(keyword in subject for keyword in filter_rule['Subject']):
                return filter_rule['ToFolder']
            if 'Content' in filter_rule and any(keyword in content for keyword in filter_rule['Content']):
                return filter_rule['ToFolder']
            if 'Spam' in filter_rule and any(keyword in subject or keyword in content for keyword in filter_rule['Spam']):
                return filter_rule['ToFolder']

        return "Inbox"

