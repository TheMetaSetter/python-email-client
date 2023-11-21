import socket
import sys
import hashlib


class client_socket():
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ip, int(self.port))
        self.logged_on = False  # Used for logging on and off (state variable)
        self.ID = 0  # Keeps track of session ID
