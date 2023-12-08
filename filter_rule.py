class filter_rule:
    def __init__(self, rule):
        self.from_addresses = rule.get('From', [])
        self.subject_keywords = rule.get('Subject', [])
        self.content_keywords = rule.get('Content', [])
        self.spam_keywords = rule.get('Spam', [])
        self.to_folder = rule.get('ToFolder', 'Inbox')