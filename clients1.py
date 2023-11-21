import socket
import ssl
import base64

def send_email(smtp_server, port, password, sender_email, receiver_email, message):
    try:
        # Create a socket and connect to the server
        sock = socket.create_connection((smtp_server, port))
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Wrap the socket with SSL
        context = ssl.create_default_context()
        context.ssl_version = ssl.PROTOCOL_TLSv1_2  # Specify the desired SSL/TLS version
        sock = context.wrap_socket(sock, server_hostname=smtp_server)
        server_info = sock.recv(1024).decode()

        print(server_info)

       # Send HELO
        sock.sendall(f"HELO {smtp_server}\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Authenticate
        sock.sendall(f"AUTH LOGIN\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send username
        sock.sendall(base64.b64encode(sender_email.encode()) + b'\r\n')
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send password
        sock.sendall(base64.b64encode(password.encode()) + b'\r\n')
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send mail from
        sock.sendall(f"MAIL FROM:<{sender_email}>\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send mail to
        sock.sendall(f"RCPT TO:<{receiver_email}>\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send mail data
        sock.sendall("DATA\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Send message data
        sock.sendall(f"{message}\r\n.\r\n".encode())
        server_info = sock.recv(1024).decode()

        print(server_info)

        # Close the connection
        sock.sendall("QUIT\r\n".encode())
        sock.close()
    except Exception as e:
        print(f"Error: {e}")
        sock.close()
        
smtp_server = '127.0.0.1'
port = 2225
password = input("Enter your password: ")
sender_email = "hailong552004@gmail.com"
receiver_email = "hailong552004@gmail.com"

message = f"Subject: Hello\n\nThis is a test message from an SMTP client."

send_email(smtp_server, port, password, sender_email, receiver_email, message)
