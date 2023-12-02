# Standard library imports
import os
import sys

# Third party imports
import mailbox

# Local application imports
import client_socket
from utilities import *

# NOTES:
# All id in this file starts from 0, only except for the id in the LIST command, which starts from 1.
# All count in this file starts from 1.


class pop3_client:
    def __init__(self, pop3_server: str, port: int, username: str, password: str = "12345678"):
        """Initialize a pop3 client object and login to the server.

        Args:
            address (str): adress of the server.
            port (int): port of the server.
            username (str): username of the client.
            password (str, optional): password of the client. Defaults to "12345678".
        """

        self.__socket = None
        self.__pop3_server = pop3_server
        self.__port = port

        self.__username = username
        self.__password = password

        self.__path_to_local_mailboxes: str = f"Profiles/{self.__username}/Local Mailboxes"
        # Check if the local mailboxes folder exists
        if not os.path.exists(self.__path_to_local_mailboxes):
            # If not, create it
            os.makedirs(self.__path_to_local_mailboxes)

        # We don't create the Downloads folder here because it may not be used.
        self.__path_to_save_attachments: str = f"Profiles/{self.__username}/Downloads"

        # After the client object is created, it will automatically connect to the server and login.
        self.__connect()
        self.__login()

        # Then, it will move all of the messages in the mailbox to the local mailbox and quit the session (close the connection).
        self.__move_all_messages_to_local_mailboxes_and_quit()

    def __connect(self):
        """Connect to the server.
        """

        print("Connect to the POP3 server...")
        # Create a socket object
        self.__socket = client_socket.client_socket(
            self.__pop3_server, self.__port)

        # Connect to the server
        self.__socket.connect()

        print("Connect successful.")

    def reconnect(self):
        """Reconnect to the pop3 server.
        """

        print("Reconnect to the POP3 server...")

        if self.__socket is None:
            self.__connect()
            self.__login()

        print("Reconnect successful.")

    def quit(self):
        """Quit session
        """

        self.__socket.send("QUIT")

    def close(self):
        """Close the connection to the server and the socket.
        """

        # Close the connection to the server
        self.__socket.close()

        # Close the socket
        self.__socket = None

    def __login(self):
        """Login to the server.
        """

        print("Logging in...")
        self.__socket.send("USER " + self.__username)
        server_response = self.__socket.recieve_string()

        if server_response[:3] != "+OK":
            self.__socket.close()
            raise Exception("The username is invalid.")

        self.__socket.send("PASS " + self.__password)
        server_response = self.__socket.recieve_string()

        if server_response[:3] != "+OK":
            self.__socket.close()
            raise Exception("The password is invalid.")

        print("Login successful.")

    def get_message_count(self) -> int:
        """Get the number of messages in the mailbox.

        Returns:
            int: the number of messages in the mailbox.
        """

        self.__socket.send("STAT")

        server_response = self.__socket.recieve_string()

        if server_response[:3] != "+OK":
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
        message_bytes = self.__socket.recieve_bytes()
        while message_bytes[-5:] != b"\r\n.\r\n":
            message_bytes += self.__socket.recieve_bytes()

        # Keep the message content from the "Subject" to the end of the mail
        message_bytes = message_bytes[message_bytes.find(
            b"Subject"):message_bytes.find(b"\r\n.\r\n")]

        return message_bytes

    def __convert_message_bytes_to_message_object(self, message_bytes: bytes) -> mailbox.mboxMessage:
        """Convert a message in bytes to an message object.

        Args:
            message_bytes (bytes): The message in bytes.

        Returns:
            mailbox.mboxMessage: The message object.
        """

        # Parse the message bytes to an message object
        mbox_object = mailbox.mboxMessage(message_bytes)

        return mbox_object

    def __delete_message_on_server(self, id: int):
        """Delete a message on the server.

        Args:
            id (int): The id of the message in the LIST command.
        """

        self.__socket.send(f"DELE {id}")

        server_response = self.__socket.recieve_string()

        if server_response[:3] != "+OK":
            print("Delete unsuccessful.")

    def __add_message_object_to_inbox(self, message: mailbox.mboxMessage):
        """Add an message object to the local mailbox.

        Args:
            message (mailbox.mboxMessage): The message object.
        """

        path = self.__path_to_local_mailboxes

        # Create a file path
        file_path = f"{path}/Inbox.mbox"
        
        # Create a mailbox object
        mbox = mailbox.mbox(file_path, create=True)

        mbox.lock()
        try:
            # Add the message object to the mailbox
            mbox.add(message)

            # Save the mailbox
            mbox.flush()
        finally:
            mbox.unlock()

    def __move_all_messages_to_local_mailboxes_and_quit(self):
        """Move all of the messages in the mailbox to the local mailbox and quit the session.
        """

        print("Collecting new messages from server...")

        # Get the number of messages in the mailbox
        message_count = self.get_message_count()

        # For each message on the server
        for id in range(1, message_count + 1):
            # Retrieve the message in bytes
            message_bytes = self.__retrieve_message_bytes(id)

            # Convert the message in bytes to an message object
            message = self.__convert_message_bytes_to_message_object(
                message_bytes)

            # Add index and read status to message object

            # Add message object to Inbox
            self.__add_message_object_to_inbox(message)

            # Delete the message on the server
            self.__delete_message_on_server(id)

        # Quit the session
        self.quit()

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
        mbox.lock()
        try:
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
        finally:
            mbox.unlock()

    def __count_attachments(self, message: mailbox.mboxMessage) -> int:
        count = 0
        if message.get_content_maintype() == 'multipart':
            for part in message.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get('Content-Disposition') is None:
                    continue
                count += 1

        return count

    def __save_attachments(self, message: mailbox.mboxMessage):
        count = 1
        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            file_name = part.get_filename()

            print(f"{count}.{file_name}")
            print("Do you want to save this file? Type 1 for Yes, 0 for No.")
            choice = int(input())
            if choice == 1:
                path = None
                if self.__path_to_save_attachments is not None:
                    print("Last-used path: ", self.__path_to_save_attachments)
                    print(
                        "Do you want to use this path to save the file? Type 1 for Yes, 0 for No.")
                    path = self.__path_to_save_attachments
                else:
                    path = str(input("Enter path to save the file: "))

                # Check if the path exists
                if not os.path.exists(path):
                    # If not, create it
                    os.makedirs(path)

                # Update the last-used path
                self.__path_to_save_attachments = path

                # Create a file path
                file_name = f"{path}/{file_name}"

                # Save the file to the path
                fb = open(file_name, 'wb')
                fb.write(part.get_payload(decode=True))
                fb.close()
                print("File saved.")

    def __ask_to_save_attachments(self, message: mailbox.mboxMessage):
        attachments_count = self.__count_attachments(message)

        if attachments_count > 0:
            print(
                "This message have attached file. Do you want to save? Type 1 for Yes, 0 for No.")
            choice = int(input())

        if choice == 1:
            self.__save_attachments(message)

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

        for part in message.walk():
            # Check if the part is multipart
            if part.get_content_maintype() == 'multipart':
                continue

            # If the part is text
            if part.get_content_type() == 'text/plain':
                # https://stackoverflow.com/questions/38970760/how-to-decode-a-mime-part-of-a-message-and-get-a-unicode-string-in-python-2
                bytes = part.get_payload(decode=True)
                charset = part.get_content_charset('iso-8859-1')
                chars = bytes.decode(charset, 'replace')
                print(chars)
                continue

            # If the part is an attachment
            if part.get('Content-Disposition') is not None:
                file_name = part.get_filename()
                print(f"{count}. {file_name}")
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
            choice = input(
                "Display message number (or press Enter to stop checking or type 0 to display all messages in the mailbox): ")
            # NOTES: Message number starts from 1 but the index of the message in the mailbox starts from 0.
            # Therefore, we need to subtract 1 from the choice to get the index of the message in the mailbox.
            
            try:
                choice = int(choice)
            except ValueError:
                break

            # If user choose to display message number count
            if choice != 0:
                # Get the message
                message = mbox[choice]

                # Diplay the message
                self.__display_message(message)

                # Mark the message as read
                self.__mark_message_as_read(mbox, choice - 1)
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
