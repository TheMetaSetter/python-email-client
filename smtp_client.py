# Standard library imports
import base64
import os
import random
import string

# Third party imports
import socket


class SMTPClient:
    def __init__(self, mail_from, to, cc, bcc, subject, content, path_list):
        self.__socket = None
        self.__smtp_server = "127.0.0.1"
        self.__port = 2225

        self._username = mail_from
        self._to = to
        self._cc = cc
        self._bcc = bcc
        self._subject = subject
        self._content = content
        self._path = path_list
        
    def __enter__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((self.__smtp_server, self.__port))
        self.__socket.sendall(b'EHLO \r\n')
        self.__socket.recv(1024)
        return self

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
    def email_list(str_info):
        mails = str_info.split(',')
        mails = [email.strip() for email in mails]
        mails = [email for email in mails if email]
        valid = []
        invalid = []
        for email in mails:
            if "@" in email and "." in email:
                valid.append(email)
            else:
                invalid.append(email)
        if invalid:
            print("Invalid email address: ")
            for email in invalid:
                print(email)
        return valid
    
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
        with open(path, 'rb') as file:
            attachment_data = base64.b64encode(file.read()).decode()
            self.__socket.send(f'Content-Transfer-Encoding: base64\r\n\r\n'.encode())
            for data in range(0, len(attachment_data), 72):
                line = attachment_data[data:data+72]
                self.__socket.send(f'{line}\r\n'.encode())

    @staticmethod
    def generate_boundary():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def send_email(self):
        mail_server = "127.0.0.1"
        mail_port = 2225

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__socket:
            try:
                self.__socket.connect((mail_server, mail_port))
                self.__socket.sendall(b'EHLO \r\n')
                self.__socket.recv(1024)

                # Send MAIL FROM
                mail_from = "MAIL FROM: <{}>\r\n".format(self._username)

                self.__socket.send(mail_from.encode())
                self.__socket.recv(1024)

                # Send MAIL TO
                if self._to:
                    self.send_list_emails(self._to)
                if self._cc:
                    self.send_list_emails(self._cc)
                if self._bcc:
                    self.send_list_emails(self._bcc)

                # Begin sending data
                self.__socket.send(b'DATA\r\n')
                self.__socket.recv(1024)

                # Generate a random boundary
                boundary = self.generate_boundary()

                # Send email structure
                self.__socket.send(f'Subject: {self._subject}\r\n'.encode())
                self.__socket.send(f'From: {self._username}\r\n'.encode())
                self.__socket.send(f'To: {", ".join(self._to)}\r\n'.encode())
                if self._cc:
                    self.__socket.send(f'Cc: {", ".join(self._cc)}\r\n'.encode())
                self.__socket.send(
                    f'Content-Type: multipart/mixed; boundary={boundary}\r\n'.encode())
                self.__socket.send('\r\n'.encode())  # End header

                # Send body email
                self.__socket.send(f'--{boundary}\r\n'.encode())
                self.__socket.send(f'Content-Type: text/plain\r\n\r\n{self._content}\r\n'.encode())

                # Send file attachments
                
                if self._path:
                    if self.check_list_file_size(self._path, 3):
                            for items_file in self._path:
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

                print("\nĐã gửi email thành công\n\n")
            except Exception as error:
                print("Error: ", error)
                