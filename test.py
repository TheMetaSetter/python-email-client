from console_email_client import console_email_client

mail_server_address = "127.0.0.1"
mail_server_port = 3335
client = console_email_client(mail_server_address)
client.run()