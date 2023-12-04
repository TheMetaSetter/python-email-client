import json

class email_filter:
    def __init__(self, config_file_path):
        self.config = self.load_config(config_file_path)

    def load_config(self, config_file_path):
        with open(config_file_path, 'r') as config_file:
            config = json.load(config_file)
        return config

    def extract_email_info_from_msg_file(self, msg_file_path):
        email_info = {'From': '', 'To': '', 'Subject': '', 'Content': ''}

        with open(msg_file_path, 'r', encoding='utf-8', errors='ignore') as msg_file:
            lines = msg_file.readlines()

            in_plain_text_content = False

            for line in lines:
                if line.startswith("From:"):
                    email_info['From'] = line[len("From:"):].strip()
                elif line.startswith("To:"):
                    email_info['To'] = line[len("To:"):].strip()
                elif line.startswith("Subject:"):
                    email_info['Subject'] = line[len("Subject:"):].strip()
                elif line.startswith("Content-Type: text/plain"):
                    in_plain_text_content = True
                    continue
                elif line.startswith("--") and in_plain_text_content:
                    break
                elif in_plain_text_content:
                    email_info['Content'] += line.strip() + ' '

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
    
# Example usage:
email_processor = email_filter("config.json")
email_info = email_processor.extract_email_info_from_msg_file("my_mailbox.mbox")
folder = email_processor.classify_email(email_info)
print(folder)
 