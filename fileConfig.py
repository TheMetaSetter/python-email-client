import configparser

def read_config():
    config = configparser.ConfigParser()
    config.read("file_config.ini")

    username = config.get('General', 'Username')
    password = config.get('General', 'Password')
    mail_server = config.get('General', 'MailServer')
    smtp_port = config.get('General', 'SMTP')
    pop3_port = config.get('General', 'POP3')
    autoload_interval = config.get('General', 'Autoload')

    return {
        'Username': username,
        'Password': password,
        'MailServer': mail_server,
        'SMTP': smtp_port,
        'POP3': pop3_port,
        'Autoload': autoload_interval
    }

config_info = read_config()
