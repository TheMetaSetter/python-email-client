# Standard library imports
import base64
import os
import random
import string

# Third party imports
import socket

from utilities import *

class smtp_client:
    def __init__(self, smtp_server: str, port: int, username: str, password: str = "12345678"):
        self.__socket = None
        self.__smtp_server = smtp_server
        self.__port = port

        self.__username = username
        self.__password = password

    def __exit__(self, exc_type, exc_value, traceback):
        self.__socket.close()

    def send_list_emails(self, email_list):
        if email_list:
            for item in email_list:
                self.__socket.sendall(f'RCPT TO:<{item}>\r\n'.encode("utf8"))
                self.__socket.recv(1024)

    @staticmethod
    def check_list_file_size(list_file_path, size):
        max_size_in_bytes = size * 1024 * 1024
        list_file_size = 0
        for file_path in list_file_path:
            list_file_size += os.path.getsize(file_path)
        if list_file_size > max_size_in_bytes:
            return False
        return True
    
    @staticmethod   
    def email_list(str_info, type):
        mails = str_info.split(',')
        mails = [email.strip() for email in mails]
        mails = [email for email in mails if email]
        valid = []
        invalid = []
        for email in mails:
            if is_valid_email(email):
                valid.append(email)
            else:
                invalid.append(email)
        if invalid:
            flag = 1
            print(f"Invalid email addresses in {type}: ")
            for email in invalid:
                print(email)
        else:
            flag = 0        
        return valid, flag
    
    @staticmethod
    def get_type_content_file(path):
        name, extension = os.path.splitext(os.path.basename(path))
        if extension == ".pdf":
            return "application/pdf"
        elif extension == ".txt":
            return "text/plain"
        elif extension == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif extension == ".jpg":
            return "image/jpeg"
        elif extension == ".zip":
            return "application/zip"
        else:
            return "application/octet-stream"

    def send_file(self, path, boundary):
        attachment_filename = os.path.basename(path)

        self.__socket.send(f'--{boundary}\r\n'.encode())
        self.__socket.send(
            f'Content-Type:{self.get_type_content_file(path)}; charset={"UTF-8"}; name="{attachment_filename}"\r\n'.encode())
        self.__socket.send(
            f'Content-Disposition: attachment; filename="{attachment_filename}"\r\n'.encode())

        # Attach the file
        try:
            with open(path, 'rb') as file:
                attachment_data = base64.b64encode(file.read()).decode()
                self.__socket.send(f'Content-Transfer-Encoding: base64\r\n\r\n'.encode())
                for data in range(0, len(attachment_data), 72):
                    line = attachment_data[data:data+72]
                    self.__socket.send(f'{line}\r\n'.encode())
        except Exception as e:
            print("Error: ",e)

    @staticmethod
    def generate_boundary():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def send_email(self, to, cc, bcc, subject, content, path_list):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__socket:
            try:
                self.__socket.connect((self.__smtp_server, self.__port))
                self.__socket.sendall(b'EHLO \r\n')
                self.__socket.recv(1024)

                # Send MAIL FROM
                mail_from = "MAIL FROM: <{}>\r\n".format(self.__username)

                self.__socket.send(mail_from.encode())
                self.__socket.recv(1024)

                # Send MAIL TO
                if to:
                    self.send_list_emails(to)
                if cc:
                    self.send_list_emails(cc)
                if bcc:
                    self.send_list_emails(bcc)

                # Begin sending data
                self.__socket.send(b'DATA\r\n')
                self.__socket.recv(1024)

                # Generate a random boundary
                boundary = self.generate_boundary()

                # Send email structure
                self.__socket.send(f'Subject: {subject}\r\n'.encode())
                self.__socket.send(f'From: {self.__username}\r\n'.encode())
                self.__socket.send(f'To: {", ".join(to)}\r\n'.encode())
                if cc:
                    self.__socket.send(f'Cc: {", ".join(cc)}\r\n'.encode())
                self.__socket.send(
                    f'Content-Type: multipart/mixed; boundary={boundary}\r\n'.encode())
                self.__socket.send('\r\n'.encode())  # End header

                # Send body email
                self.__socket.send(f'--{boundary}\r\n'.encode())
                self.__socket.send(f'Content-Type: text/plain\r\n\r\n{content}\r\n'.encode())

                # Send file attachments
                if path_list:
                    for items_file in path_list:
                        self.send_file(items_file, boundary)
                    
                # End mail
                self.__socket.send(f'\r\n--{boundary}--\r\n'.encode())
                end = f'.\r\n'
                self.__socket.send(end.encode())
                self.__socket.recv(1024)

                # Close connect
                quit_cmd = "QUIT\r\n"
                self.__socket.send(quit_cmd.encode())
                self.__socket.recv(1024)
                self.__socket.close()

                print("Email sent successfully.")
            except Exception as error:
                print("Error: ", error)
                