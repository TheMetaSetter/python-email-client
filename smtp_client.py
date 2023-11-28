# Standard library imports
import base64
import os
import random
import string

# Third party imports
import socket


def sendList_emails(client, list):
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


def check_list_file_size(list_file_path, size):
    max_size_in_bytes = size * 1024 * 1024
    list_file_size = 0
    for file_path in list_file_path:
        list_file_size += os.path.getsize(file_path)
    if list_file_size > max_size_in_bytes:
        return False
    return True


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


def send_file(client, path, boundary):
    attachment_filename = os.path.basename(path)

    client.send(f'--{boundary}\r\n'.encode())
    client.send(
        f'Content-Type:{get_type_content_file(path)}; charset={"UTF-8"};name ="{attachment_filename}"\r\n'.encode())
    client.send(
        f'Content-Disposition: attachment; filename="{attachment_filename}"\r\n'.encode())

    # Attach the file
    with open(path, 'rb') as file:
        attachment_data = base64.b64encode(file.read()).decode()
        client.send(f'Content-Transfer-Encoding: base64\r\n\r\n'.encode())
        for data in range(0, len(attachment_data), 72):
            line = attachment_data[data:data+72]
            client.send(f'{line}\r\n'.encode())


def generate_boundary():              # Generate a random boundary value
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def send_email(to_email, cc_email, bcc_email, subject, content, file_choice):
    mail_server = "127.0.0.1"
    mail_port = 2225

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        try:
            c.connect((mail_server, mail_port))
            c.sendall(b'EHLO \r\n')
            c.recv(1024)

            # Send MAIL FROM
            mail_from = "MAIL FROM: <tin75vn@gmail.com>\r\n"
            c.send(mail_from.encode("utf8"))
            c.recv(1024)

            # Send MAIL TO
            if to_email:
                sendList_emails(c, to_email)
            if cc_email:
                sendList_emails(c, cc_email)
            if bcc_email:
                sendList_emails(c, bcc_email)

            # Begin sending data
            c.send(b'DATA\r\n')
            c.recv(1024)

            # Generate a random boundary
            boundary = generate_boundary()

            # Send email structure

            c.send(f'Subject: {subject}\r\n'.encode())
            c.send(f'From: {"tin75vn@gmail.com"}\r\n'.encode())
            c.send(f'To: {", ".join(to_email)}\r\n'.encode())
            if cc_email:
                c.send(f'Cc: {", ".join(cc_email)}\r\n'.encode())
            c.send(
                f'Content-Type: multipart/mixed; boundary={boundary}\r\n'.encode())
            c.send('\r\n'.encode())  # End header

            # Send body email
            c.send(f'--{boundary}\r\n'.encode())
            c.send(f'Content-Type: text/plain\r\n\r\n{content}\r\n'.encode())

            # Send file attachments
            if file_choice == 1:
                file_amount = int(input("Số lượng file muốn gửi: "))
                path_list = []
                for i in range(1, file_amount + 1):
                    path = input(f"Cho biết đường dẫn file thứ {i}: ")
                    path_list.append(path)

                if check_list_file_size(path_list, 3):
                    for path_file in path_list:
                        send_file(c, path_file, boundary)

            # End mail
            c.send(f'\r\n--{boundary}--\r\n'.encode())
            end = f'.\r\n'
            c.send(end.encode())
            c.recv(1024)

            # Close connect
            quit = "QUIT\r\n"
            c.send(quit.encode())
            c.recv(1024)

            c.close()

            print("\nĐã gửi email thành công\n\n")
        except Exception as error:
            print("Error: ", error)


# ------------------------------------------------main-------------------------------------------------
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

send_email(to_receivers, cc_receivers, bcc_receivers,
           subject, content, have_file)
