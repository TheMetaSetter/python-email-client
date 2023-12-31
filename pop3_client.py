# Standard library imports
import os
import sys

# Third party imports
import mailbox

# Local application imports
import client_socket
from utilities import *
from client_filter import email_filter

# NOTES:
# All id in this file starts from 0, only except for the id in the LIST command, which starts from 1.
# All count in this file starts from 1.


class pop3_client:
    def __init__(self, pop3_server: str, port: int, username: str, password: str = "12345678", config_file_path: str = None):
        """Initialize a pop3 client object and login to the server.

        Args:
            address (str): adress of the server.
            port (int): port of the server.
            username (str): username of the client.
            password (str, optional): password of the client. Defaults to "12345678".
        """

        self.__socket: client_socket.client_socket = None
        self.__pop3_server = pop3_server
        self.__port = port

        self.__username = username
        self.__password = password
        
        self.__filter: email_filter = None
        
        self.__path_to_config_file: str = config_file_path
        
        self.__slash: str = None

        # Check if the os is Windows or MacOS
        # https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
        if sys.platform == "win32":
            self.__slash = "\\"
        elif sys.platform == "darwin":
            self.__slash = "/"
        elif sys.platform == "linux" or sys.platform == "linux2":
            self.__slash = "/"
        
        self.__path_to_local_mailboxes: str = f"Profiles{self.__slash}{self.__username}{self.__slash}Local Mailboxes"
        
        # Check if the local mailboxes folder exists
        if not os.path.exists(self.__path_to_local_mailboxes):
            # If not, create it
            os.makedirs(self.__path_to_local_mailboxes)

        # We don't create the Downloads folder here because it may not be used.
        self.__path_to_save_attachments: str = f"Profiles{self.__slash}{self.__username}{self.__slash}Downloads"

        # After the client object is created, it will automatically connect to the server and login.
        self.__connect()
        self.login()

    def __connect(self):
        """Connect to the server.
        """

        # Create a socket object
        self.__socket = client_socket.client_socket(
            self.__pop3_server, self.__port)

        # Connect to the server
        self.__socket.connect()
    
    def reconnect(self):
        """Reconnect to the pop3 server after using close().
        """

        if self.__socket is None:
            self.__connect()
        else:
            self.__socket.connect()
        
        self.login()

    def __quit(self):
        """Quit session
        """

        self.__socket.send("QUIT")
        
        server_response = self.__socket.recieve_bytes()
        
        if b"+OK" not in server_response:
            print("Quit session unsuccessful.")
            self.close()

    def close(self):
        """Quit session and close the connection to the server and the socket.
        """

        self.__quit()
        
        if self.__socket is not None:
            # Close the connection to the server
            self.__socket.close()
            
            # Close the socket
            self.__socket = None

    def login(self):
        """Login to the server.
        """

        self.__socket.send("USER " + self.__username)
        server_response = self.__socket.recieve_bytes()

        if b"+OK" not in server_response:
            self.__socket.close()
            raise Exception("The username is invalid.")

        self.__socket.send("PASS " + self.__password)
        server_response = self.__socket.recieve_bytes()

        if b"+OK" not in server_response:
            self.__socket.close()
            raise Exception("The password is invalid.")

    def get_message_count(self) -> int:
        """Get the number of messages in the mailbox.

        Returns:
            int: the number of messages in the mailbox.
        """

        self.__socket.send("STAT")

        server_response = self.__socket.recieve_bytes()

        if b"+OK" not in server_response:
            print(server_response)
            self.__socket.close()
            sys.exit(1)

        message_count = int(server_response.split()[1])

        return message_count

    def __retrieve_message_bytes(self, id: int) -> bytes:
        """Retrieve a message from the server in string format.

        Args:
            id (int): The id of the message in the LIST command.

        Returns:
            str: The message in string format.
        """

        self.__socket.send(f"RETR {id}")

        # Keep recieving the message until the end of the message
        message_bytes = b''

        # If the message_bytes ends with b"\r\n.\r\n", then the message is complete.
        while True:
            # Recieve the message
            message_bytes += self.__socket.recieve_bytes()

            # If the message ends with b"\r\n.\r\n"
            if message_bytes.endswith(b"\r\n.\r\n"):
                break
            
        # Keep the content right after the first "\r\n" till the end
        message_bytes = message_bytes.split(b"\r\n", 1)[1]

        return message_bytes

    def __convert_message_bytes_to_message_object(self, message_bytes: bytes) -> mailbox.mboxMessage:
        """Convert a message in bytes to an message object.

        Args:
            message_bytes (bytes): The message in bytes.

        Returns:
            mailbox.mboxMessage: The message object.
        """

        # Parse the message bytes to an message object
        message_object = mailbox.mboxMessage(message_bytes)
        
        return message_object

    def __delete_message_on_server(self, id: int):
        """Delete a message on the server.

        Args:
            id (int): The id of the message in the LIST command.
        """

        self.__socket.send(f"DELE {id}")

        server_response = self.__socket.recieve_bytes()

        if b"+OK" not in server_response:
            print("Delete unsuccessful.")

    def __add_message_object_to_local_mailboxes(self, message: mailbox.mboxMessage, local_mailbox_name: str):
        """Add an message object to the local mailbox.

        Args:
            message (mailbox.mboxMessage): The message object.
        """

        path = self.__path_to_local_mailboxes

        # Create a file path
        file_path = f"{path}{self.__slash}{local_mailbox_name}.mbox"
        
        # Create a mailbox object
        mbox = mailbox.mbox(file_path, create=True)

        # Add the message object to the mailbox
        mbox.add(message)

        # Save the mailbox
        mbox.flush()

    def move_all_messages_to_local_mailboxes_and_close(self):
        """Move all of the messages in the mailbox to the local mailbox and quit the session.
        """

        # Get the number of messages in the mailbox
        message_count = self.get_message_count()

        # For each message on the server
        for id in range(1, message_count + 1):
            # Retrieve the message in bytes
            message_bytes = self.__retrieve_message_bytes(id)

            # Convert the message in bytes to an message object
            message = self.__convert_message_bytes_to_message_object(
                message_bytes)
            
            # Create a filter object
            if self.__filter is None:
                self.__filter = email_filter(self.__path_to_config_file)
            
            # Get the local mailbox name of the message
            local_mailbox_name = self.__filter.classify_email(message)
            
            # Add message object to Inbox
            self.__add_message_object_to_local_mailboxes(message, local_mailbox_name)

            # Delete the message on the server
            self.__delete_message_on_server(id)

        # Quit the session
        self.close()

    def get_list_mailboxes(self) -> list[str]:
        """Get the list of mailboxes of the user.

        Returns:
            list: The list of mailboxes of the user.
        """

        # Get the list of mailbox files of the user
        list_mailboxes = os.listdir(self.__path_to_local_mailboxes)

        # Remove the extension of the mailbox files
        for i in range(len(list_mailboxes)):
            list_mailboxes[i] = list_mailboxes[i].split(".")[0]

        return list_mailboxes

    def __mark_message_as_read(self, mbox: mailbox.mbox, id: int) -> mailbox.mboxMessage:
        """Mark message having id = id as read.

        Args:
            mailbox (mailbox.mbox): The mailbox object.
            id (int): The id of the message
        """

        # Get the message
        message = mbox[id]

        # Get the flags
        flags = message.get_flags()

        # If the message is unread
        if "R" not in flags:
            # Mark the message as read
            message.set_flags("R")
        
        mbox[id] = message
        
        mbox.flush()

    def __count_attachments(self, message: mailbox.mboxMessage) -> int:
        count = 0
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                count += 1

        return count
    
    def __save_an_attachment(self, part: mailbox.mboxMessage, path: str):
        # Get the name of the file
        file_name = part.get_filename()
        
        # Split the name and the extension
        file_name, file_extension = os.path.splitext(file_name)

        # Create the full path to file
        full_path_to_file = f"{path}{self.__slash}{file_name}.{file_extension}"
        
        # Check if the file exists
        if os.path.exists(full_path_to_file):
            # Count the number of the file have the same name
            count_same_name = 1
            while True:
                # Create a new full path to file
                full_path_to_file = f"{path}{self.__slash}{file_name}({count_same_name}).{file_extension}"
                
                # Check if the file exists
                if os.path.exists(full_path_to_file):
                    count_same_name += 1
                    continue
                else:
                    # Save the file to the path
                    fb = open(full_path_to_file, 'wb')
                    fb.write(part.get_payload(decode=True))
                    fb.close()
                    break
        else:
            # Save the file to the path
            fb = open(full_path_to_file, 'wb')
            fb.write(part.get_payload(decode=True))
            fb.close()
    
    def __save_all_attachments(self, message: mailbox.mboxMessage):
        # Ask user for the path to save all these attachments at once
        path = None
        if self.__path_to_save_attachments is not None:
            print("Last-used path: ", self.__path_to_save_attachments)
            
            choice = input_integer("Do you want to use this path? (Type 1 for Yes, 0 for No): ")
            
            if choice == 1:
                path = self.__path_to_save_attachments
            else:
                path = str(input("Enter path to save all the files: "))
        else:
            path = str(input("Enter path to save all the files: "))
        
        # Check if the path exists
        if not os.path.exists(path):
            # If not, create it
            os.makedirs(path)
        
        # Update the last-used path
        self.__path_to_save_attachments = path
        
        # Save attachments
        count = 1
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                self.__save_an_attachment(part, self.__path_to_save_attachments)
                print(f"File {count} saved.")
                count += 1

    def __save_attachments_consecutively(self, message: mailbox.mboxMessage):
        count = 1
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                file_name = part.get_filename()

                print(f"{count}.{file_name}")
                
                choice = input_integer("Do you want to save this file? (Type 1 for Yes, 0 for No): ")
                
                if choice == 1:
                    path = None
                    if self.__path_to_save_attachments is not None:
                        print("Last-used path: ", self.__path_to_save_attachments)
                        
                        choice = input_integer("Do you want to use this path? (Type 1 for Yes, 0 for No): ")
                        
                        if choice == 1:
                            path = self.__path_to_save_attachments
                        else:
                            path = str(input("Enter path to save the file: "))
                    else:
                        path = str(input("Enter path to save the file: "))

                    self.__save_an_attachment(part, path)
                    
                    print("File saved.")

    def __ask_to_save_attachments(self, message: mailbox.mboxMessage):
        attachments_count = self.__count_attachments(message)

        choice = 0
        if attachments_count > 0:
            choice = input_integer("Do you want to save the attachments? (Type 1 for Yes, 0 for No): ")

        if choice == 1:
            # Ask user whether to save all attachments at once or save each attachment
            choice = input_integer("Do you want to save all attachments at once? (Type 1 for Yes, 0 for No): ")
            
            if choice == 1:
                self.__save_all_attachments(message)
            else:
                self.__save_attachments_consecutively(message)

    def __dipslay_message_summary(self, message: mailbox.mboxMessage):
        # Components of an message summary
        read_status_str: str() = ""
        subject_str: str() = ""
        sender_str: str() = ""
        recipient_str: str() = ""
        have_attachment_str: str() = ""

        # Get the read status string
        flags = message.get_flags()
        if "R" not in flags:
            read_status_str = add_angle_brackets("Unread")
        else:
            read_status_str = ""

        # Get the subject string
        subject_str = add_angle_brackets(str(message['Subject']))

        # Get the sender string
        sender_str = add_angle_brackets(str(message['From']))

        # Get the recipient string
        recipient_str = add_angle_brackets(str(message['To']))

        # Check if the message have attachment
        if self.__count_attachments(message) > 0:
            have_attachment_str = add_angle_brackets("Have attachment")

        summary_str = read_status_str + subject_str + sender_str + recipient_str + have_attachment_str

        print(summary_str)

    def __display_message(self, message: mailbox.mboxMessage):
        count = 1
        
        not_headers = ["Status", "X-Status","Content-Type"]
        for key, value in message.items():
            if key not in not_headers:
                print(f"{key}: {value}")

        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            
            # If the part is content
            if part.get_content_type() == 'text/plain' and part.get_content_disposition() is None:
                # https://stackoverflow.com/questions/38970760/how-to-decode-a-mime-part-of-a-message-and-get-a-unicode-string-in-python-2
                bytes = part.get_payload(decode=True)
                charset = part.get_content_charset('iso-8859-1')
                chars = bytes.decode(charset, 'replace')
                print("\nContent: ")
                print(chars)
                print("\n")
                continue

            # If the part is an attachment
            if part.get_content_disposition() == "attachment":
                file_name = part.get_filename()
                print(f"Attachment: {count}. {file_name}")
                count += 1

        self.__ask_to_save_attachments(message)

    def check_mailbox(self, mailbox_name: str):
        mailbox_file_path = f"{self.__path_to_local_mailboxes}/{mailbox_name}.mbox"

        mbox = mailbox.mbox(mailbox_file_path)

        # Display all of the summary of messages in the mailbox
        for id, message in enumerate(mbox):
            # Print the count of the message without the endline character
            print(f"{id + 1}. ", end="")
            # Display the message summary
            self.__dipslay_message_summary(message)

        while True:
            # Ask the user to choose which message to display
            choice = input("Enter the number of the message you want to display. (Enter 0 to display all messages or press Enter to exit): ")
            # NOTES: Message number starts from 1 but the index of the message in the mailbox starts from 0.
            # Therefore, we need to subtract 1 from the choice to get the index of the message in the mailbox.
            
            if choice == "":
                break
            
            while not choice.isdigit():
                choice = input("Invalid character. Please re-enter: ")
                
            choice = int(choice)

            # If user choose to display message number count
            if choice != 0:
                id = choice - 1
                
                # Get the message
                message = mbox[id]

                # Diplay the message
                self.__display_message(message)

                # Mark the message as read
                self.__mark_message_as_read(mbox, id)
            elif choice == 0:
                # Display all the messages in the mailbox
                for id, message in enumerate(mbox):
                    # Print the count of the message without the endline character
                    print(f"{id + 1}. ", end="")
                    # Display the message summary
                    self.__dipslay_message_summary(message)
            else:
                break
            
            mbox.flush()
    
    def set_path_to_config_file(self, path: str):
        self.__path_to_config_file = path