import json

config_data = {
    "General": {
        "Username": "Quan Nguyen <ntquan@testing.com>",
        "Password": "ahihi",
        "MailServer": "192.168.1.10",
        "SMTP": 3333,
        "POP3": 4444,
        "Autoload": 10
    },
    "Filter": [
        {
            "From": ["ahihi@testing.com", "ahuu@testing.com"],
            "ToFolder": "Project"
        },
        {
            "Subject": ["urgent", "ASAP"],
            "ToFolder": "Important"
        },
        {
            "Content": ["report", "meeting"],
            "ToFolder": "Work"
        },
        {
            "Spam": ["virus", "hack", "crack"],
            "ToFolder": "Spam"
        }
    ]
}

# Lưu vào file JSON
with open('config.json', 'w') as config_file:
    json.dump(config_data, config_file, indent=2)

print("Đã lưu cấu hình vào config.json")
