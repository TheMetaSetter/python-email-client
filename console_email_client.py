import json
import threading
import time
import os

import pop3_client
import smtp_client
from utilities import *

class console_email_client:
    def __init__(self, mail_server_address: str, smtp_port: int = 2225, pop3_port: int = 3335):
        self.__mail_server_address = mail_server_address

        self.__smtp_port = smtp_port
        self.__pop3_port = pop3_port

        self.__pop3_client: pop3_client.pop3_client = None
        self.__smtp_client: smtp_client.smtp_client = None

        self.__current_username: str = None
        self.__current_password: str = None

        self.__current_mode: int = None

        self.__mailboxes_dict: dict = dict()
        
        self.__user_config_file_path: str = None

    def generate_config(self):
        config = {
            "General": {
                "Username": self.__current_username,
                "Password": self.__current_password,
                "MailServer": self.__mail_server_address,
                "SMTP": self.__smtp_port,
                "POP3": self.__pop3_port,
                "Autoload": 10
            },
            "Filter": [
                {"From": [], "ToFolder": "Project"},
                {"Subject": [], "ToFolder": "Important"},
                {"Content": [], "ToFolder": "Work"},
                {"Spam": [], "ToFolder": "Spam"}
            ]
        }

        with open(f'Profiles/{self.__current_username}/config.json', 'w') as config_file:
            json.dump(config, config_file, indent = 2)
    
    def __console_login(self):
        try:
            username = input("Username: ")
            
            while not is_valid_email(username):
                print("Invalid email.")
                username = input("Username: ")
            
            password = input("Password: ")

            # Try to login to the smtp server
            self.__smtp_client = smtp_client.smtp_client(
                self.__mail_server_address, self.__smtp_port, username, password)
            
            # Try to login to the pop3 server
            self.__pop3_client = pop3_client.pop3_client(
                self.__mail_server_address, self.__pop3_port, username, password)
            
        except Exception as e:
            print(e)
            exit(1)
            
        else:
            # After login successfully, set current user
            self.__current_username = username
            
            # Initialize path to config file
            self.__user_config_file_path = f"Profiles/{self.__current_username}/config.json"
            
            # Create config file if not exist
            if not os.path.exists(self.__user_config_file_path):
                self.generate_config()
            
            # Set config file path for pop3 client
            self.__pop3_client.set_path_to_config_file(self.__user_config_file_path)
            
            # Move all messages to local mailboxes
            self.__pop3_client.move_all_messages_to_local_mailboxes_and_close()

    def __console_logout(self):
        flag = input_integer("Do you want to quit? (Type 1 for Yes, order keys for No): ")
        
        if flag == 1:
            self.__current_username = str()
            self.__current_password = str()

            if self.__smtp_client is not None:
                self.__smtp_client.__exit__

            print("Logout completed.")

            exit(0)
        else:
            print("Canceled logout!!!\n")
            return 

    def __send_email(self):
        print("This is the information to compose an email: ")
        print("(If not filled in, please press 'enter' to skip)")
        print("(If you want to cancel sending mail, enter '***')")
        while True:
            temp_to = input("To: ")
            if temp_to =="***":
                print("Canceled sending email!!!\n")
                return
            to_receivers,flag = self.__smtp_client.email_list(temp_to, "'To'")
            if flag == 1:
                buf = input("Select 1 to re-enter all valid emails you want to send or Select any other key to continue to other sections: ")
                if buf == "1":
                    continue
                else:
                    break
            else:
                break
                
        while True:    
            temp_cc = input("CC: ")
            if temp_cc=="***" :
                print("Canceled sending email!!!\n")
                return
            cc_receivers,flag = self.__smtp_client.email_list(temp_cc, "'CC'")
            if flag == 1:
                buf = input("Select 1 to re-enter all valid emails you want to send or Select any other key to continue to other sections: ")
                if buf == "1":
                    continue
                else:
                    break
            else:
                break
                
        while True:    
            temp_bcc = input("BCC: ")
            if temp_bcc =="***":
                print("Canceled sending email!!!\n")
                return
            bcc_receivers,flag = self.__smtp_client.email_list(temp_bcc, "'BCC'")
            if flag == 1:
                buf = input("Select 1 to re-enter all valid emails you want to send or Select any other key to continue to other sections: ")
                if buf == "1":
                    continue
                else:
                    break
            else:
                break
                
        if not to_receivers and not cc_receivers and not bcc_receivers:
            print("There are no valid emails. Sending email failed!!!\n\n")
            return
        
        subject = input("Subject: ")
        if subject=="***" :
            print("Canceled sending email!!!\n")
            return
        
        content = ""
        while True:
            temp = "-"
            print("Content(Press 'enter' twice to end the content): ")
            while temp != "":
                temp = input("  ")
                if temp == "***":
                    print("Canceled sending email!!!\n")
                    return
                content = content + temp + "\n"
            if content == "\n":
                print("The content cannot be empty. Please re-enter or enter '***' to cancel sending the email!!!") 
            else:
                break
                
        have_file =""
        while True:
            have_file = input("Are files attached? (1. yes, 2. no): ")
            if have_file =="1"or have_file=="2"or have_file=="***":
                break
            else:
                print("Invalid character, only 1 or 2 or '***' can be entered here. Please re-enter!!!")
        
        if have_file=="***":
            print("Canceled sending email!!!\n")
            return
        
        else:
            path_list = []
            if have_file == "1" :
                file_amount = int(input("Number of files you want to send: "))
                while True:
                    path_list = []
                    for i in range(1, file_amount + 1):
                        while True:
                            path = input(f"Indicates the file path {i}: ")
                            if path == "***":
                                print("Canceled sending email!!!\n")
                                return
                            
                            if os.path.exists(path):
                                path_list.append(path)
                                break
                            else:
                                print(f"The file {path} does not exist. Please re-enter or enter '***' to cancel sending the email!!!")
                        
                    if self.__smtp_client.check_list_file_size(path_list, 3) == False:
                        print("The size of the attached files is larger than 3MB so it cannot be sent. Please re-enter or enter '***' to cancel sending the email!!!") 
                    else:
                        break  
                    
            self.__smtp_client.send_email(to_receivers, cc_receivers, bcc_receivers, subject, content,path_list)
                

    def __display_retrieved_email(self):
        print("List of your mailboxes:")

        list_mailboxes = self.__pop3_client.get_list_mailboxes()

        for i, mailbox in enumerate(list_mailboxes, start=1):
            print(f"{i}. {mailbox}")
            self.__mailboxes_dict[i] = mailbox

        choice = input_integer("You want to check mailbox number: ")

        try:
            self.__pop3_client.check_mailbox(self.__mailboxes_dict[choice])
        except KeyError:
            print("Invalid mailbox number.\n")
            

    def __display_menu(self):
        print("Select from the options below:")
        print("1. Send email")
        print("2. Check email")
        print("3. Logout")

    def __change_mode(self):
        self.__display_menu()

        mode = input("\nYour choose mode number: ")
        
        while mode not in ["1", "2", "3"]:
            print("Invalid mode number. Please select again!!!")
            mode = input("Your choose mode number: ")

        self.__current_mode = int(mode)

    def __run_current_mode(self):
        if self.__current_mode == 1:
            self.__send_email()
        elif self.__current_mode == 2:
            self.__display_retrieved_email()
        elif self.__current_mode == 3:
            self.__console_logout()
            
    def start_autoload(self):
        # Read auto load config
        with open(self.__user_config_file_path, 'r') as config_file:
            config = json.load(config_file)
        autoload_interval: int = config['General']['Autoload']
        
        while True:
            time.sleep(autoload_interval)
            self.__pop3_client.reconnect()
            self.__pop3_client.login()
            self.__pop3_client.move_all_messages_to_local_mailboxes_and_close()
            

    def run(self):
        self.__console_login()

        autoload_thread = threading.Thread(target=self.start_autoload, daemon=True)
        autoload_thread.start()
        
        while True:
            self.__change_mode()
            self.__run_current_mode()