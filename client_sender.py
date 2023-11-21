import socket
import base64

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the SMTP server
s.connect(('127.0.0.1', 2225))

# Receive the server's response
print(s.recv(1024).decode())

# Send HELO command to the server
s.sendall(b'HELO \r\n')
print(s.recv(1024).decode())

# Send MAIL FROM command
s.sendall(b'MAIL FROM:<hailong552004@gmail.com>\r\n')
print(s.recv(1024).decode())

# Send RCPT TO command
s.sendall(b'RCPT TO:<hailong552004@gmail.com>\r\n')
print(s.recv(1024).decode())

# Send DATA command
s.sendall(b'DATA\r\n')
print(s.recv(1024).decode())

# Send email headers and body
email_body = 'From: hailong552004@gmail.com\r\nTo: hailong552004@gmail.com\r\nSubject: Test email\r\n\r\nThis is a test email.\r\n.\r\n'
s.sendall(email_body.encode())
print(s.recv(1024).decode())

# Send QUIT command
s.sendall(b'QUIT\r\n')
print(s.recv(1024).decode())

# Close the socket
s.close()
