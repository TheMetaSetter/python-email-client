# import socket
# import base64

# # Create a socket object
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # Connect to the SMTP server
# s.connect(('127.0.0.1', 2225))

# # Receive the server's response
# print(s.recv(1024).decode())

# # Send HELO command to the server
# s.sendall(b'HELO \r\n')
# print(s.recv(1024).decode())

# # Send MAIL FROM command
# s.sendall(b'MAIL FROM:<hailong552004@gmail.com>\r\n')
# print(s.recv(1024).decode())

# # Send RCPT TO command
# s.sendall(b'RCPT TO:<hailong552004@gmail.com>\r\n')
# print(s.recv(1024).decode())

# # Send DATA command
# s.sendall(b'DATA\r\n')
# print(s.recv(1024).decode())

# # Send email headers and body
# email_body = 'From: hailong552004@gmail.com\r\nTo: hailong552004@gmail.com\r\nSubject: Test email\r\n\r\nThis is a test email.\r\n.\r\n'
# s.sendall(email_body.encode())
# print(s.recv(1024).decode())

# # Send QUIT command
# s.sendall(b'QUIT\r\n')
# print(s.recv(1024).decode())

# # Close the socket
# s.close()


import socket
import base64   
import os

def check_file_size(file_path, size):
    max_size_in_bytes = size * 1024 * 1024
    file_size = os.path.getsize(file_path)
    if file_size > max_size_in_bytes:
        return False
    return True

def sendList_emails(client,list):
    if list:
        for item in list:
            client.sendall(f'RCPT TO:<{item}>\r\n'.encode("utf8"))
            client.recv(1024)


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
def send_file(client, path, boundary):
    attachment_filename = os.path.basename(path)

    # Attach the file
    with open(path, 'rb') as file:
        attachment_data = base64.b64encode(file.read()).decode()
        attachment_headers = f'Content-Disposition: attachment; filename={attachment_filename}\r\nContent-Transfer-Encoding: base64\r\n\r\n'
        client.sendall(f'--{boundary}\r\n{attachment_headers}{attachment_data}\r\n'.encode())

def send_email(to_email, cc_email, bcc_email, subject, content, file_choice):
    mail_server = "127.0.0.1"
    mail_port = 2225

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.connect((mail_server, mail_port))
        c.sendall(b'HELO \r\n')
        c.recv(1024)

        mail_from = "MAIL FROM: <hailong552004@gmail.com>\r\n"
        c.send(mail_from.encode("utf8"))
        c.recv(1024)

        if to_email:
            sendList_emails(c, to_email)
            if cc_email:
                sendList_emails(c, cc_email)
                if bcc_email:
                    sendList_emails(c, bcc_email)

        # Begin sending data
        data_command = "DATA\r\n"
        c.send(data_command.encode("utf8"))
        c.recv(1024)

        # Generate a random boundary
        boundary = "boundary1"

        # Send email structure
        email_content = f"Subject: {subject}\r\n"
        email_content += f"To: {to_email}\r\n"

        if cc_email:
            email_content += f"CC: {cc_email}\r\n"

        if bcc_email:
            email_content += f"BCC: {bcc_email}\r\n"

        mime_headers = f'MIME-Version: 1.0\r\nContent-Type: multipart/mixed; boundary={boundary}\r\n\r\n'
        c.sendall((email_content + mime_headers).encode())

        # Send file attachments
        if file_choice == 1:
            file_amount = int(input("Số lượng file muốn gửi: "))
            for i in range(1, file_amount + 1):
                path = input(f"Cho biết đường dẫn file thứ {i}: ")
                if check_file_size(path, 3):
                    send_file(c, path, boundary)

        # End mail
        end = f'\r\n--{boundary}--\r\n.\r\n'
        c.send(end.encode())
        c.recv(1024)

        # Close connect
        quit_command = "QUIT\r\n"
        c.send(quit_command.encode())
        c.recv(1024)

    print("\nĐã gửi email thành công\n\n")
        
        
        
#------------------------------------------------main-------------------------------------------------


print("Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)")
temp_to = input("To: ")
to_receivers = email_list(temp_to)

temp_cc = input("CC: ")
cc_receivers = email_list(temp_cc)

temp_bcc = input("BCC: ")
bcc_receivers = email_list(temp_bcc)

subject = input("Subject: ")

content = input("Content: ")

have_file = int(input("Có gửi kèm file (1. có, 2. không): "))


send_email(to_receivers,cc_receivers, bcc_receivers, subject, content, have_file )


