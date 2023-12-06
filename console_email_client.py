import pop3_client
import smtp_client
from utilities import *

class console_email_client:
    def __init__(self, mail_server_address: str, smtp_port: int = 2225, pop3_port: int = 3335):
        self.__smtp_server_address = mail_server_address
        self.__pop3_server_address = mail_server_address

        self.__smtp_port = smtp_port
        self.__pop3_port = pop3_port

        self.__pop3_client: pop3_client.pop3_client = None
        self.__smtp_client: smtp_client.smtp_client = None

        self.__current_user: str = None

        self.__current_mode: int = None

        self.__mailboxes_dict: dict = dict()

    def __console_login(self):
        try:
            username = input("Username: ")
            
            while not is_valid_email(username):
                print("Invalid email.")
                username = input("Username: ")
            
            password = input("Password: ")

            self.__smtp_client = smtp_client.smtp_client(
                self.__smtp_server_address, self.__smtp_port, username, password)
            self.__pop3_client = pop3_client.pop3_client(
                self.__pop3_server_address, self.__pop3_port, username, password)
            self.__pop3_client.quit()
        except Exception as e:
            print(e)
            exit(1)
        else:
            self.__current_user = username
            return True

    def __console_logout(self):
        self.__current_user = str()

        if self.__pop3_client is not None:
            self.__pop3_client.close()

        if self.__smtp_client is not None:
            self.__smtp_client.__exit__

        print("Logout completed.")

        exit(0)

    def __send_email(self):
        print("This is the information to compose an email: (If not filled in, please press enter to skip)")
        temp_to = input("To: ")
        to_receivers = self.__smtp_client.email_list(temp_to)

        temp_cc = input("Cc: ")
        cc_receivers = self.__smtp_client.email_list(temp_cc)

        temp_bcc = input("BCC: ")
        bcc_receivers = self.__smtp_client.email_list(temp_bcc)

        subject = input("Subject: ")

        content = input("Content: ")

        have_file = int(input("Are files attached? (1. yes, 2. no): "))
        path_list = []
        if have_file == 1:
            file_amount = int(input("Number of files you want to send: "))
            for i in range(1, file_amount + 1):
                path = input(f"Indicates the file path {i}: ")
                path_list.append(path)

        self.__smtp_client.send_email(to_receivers, cc_receivers, bcc_receivers, subject, content,path_list)

    def __display_retrieved_email(self):
        print("List of your mailboxes:")

        list_mailboxes = self.__pop3_client.get_list_mailboxes()

        for i, mailbox in enumerate(list_mailboxes, start=1):
            print(f"{i}. {mailbox}")
            self.__mailboxes_dict[i] = mailbox

        choice = int(input("You want to check email in folder number: "))

        self.__pop3_client.check_mailbox(self.__mailboxes_dict[choice])

    def __display_menu(self):
        print("Select from the options below:")
        print("1. Send email")
        print("2. Check email")
        print("3. Logout")

    def __change_mode(self):
        self.__display_menu()

        mode = input("Your choose mode number: ")
        
        while mode not in ["1", "2", "3"]:
            print("Invalid mode number.")
            mode = input("Your choose mode number: ")

        self.__current_mode = int(mode)

    def __run_current_mode(self):
        if self.__current_mode == 1:
            self.__send_email()
        elif self.__current_mode == 2:
            self.__display_retrieved_email()
        elif self.__current_mode == 3:
            self.__console_logout()

    def run(self):
        self.__console_login()
        while True:
            self.__change_mode()
            self.__run_current_mode()
