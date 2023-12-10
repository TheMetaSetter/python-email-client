# Standard library imports
import socket
import sys


class client_socket:
    def __init__(self, address: str, port: int):
        # These are private attributes.
        self.__address = address
        self.__port = port
        self.__socket: socket.socket = None

        self.__error_dict = {
            ConnectionRefusedError: "client_socket.py: The server might not listening.",
            socket.gaierror: "client_socket.py: The hostname or the service you’re trying to connect to cannot be resolved.",
            BrokenPipeError: "client_socket.py: The server is not ready.",
        }

        self.__BYTES_PER_RECIEVE = 1024

        # These are public attributes.

    def recieve_string(self) -> str:
        """Recieve a message in string format from the server.

        Returns:
            str: The message recieved from the server.
        """

        return self.__socket.recv(self.__BYTES_PER_RECIEVE).decode('utf-8')

    def recieve_bytes(self) -> bytes:
        """Recieve a message in bytes from the server.

        Returns:
            bytes: The message recieved from the server.
        """

        return self.__socket.recv(self.__BYTES_PER_RECIEVE)

    def send(self, message: str):
        """Send a message in bytes to the server.

        Args:
            message (str): The message to be sent in string format.
        """

        try:
            message = message.encode('utf-8') + b'\r\n'
            self.__socket.send(message)
        except BrokenPipeError:
            print(self.__error_dict[BrokenPipeError])
            sys.exit(1)

    def connect(self):
        """Connect to the server.

        Raises:
            Exception: If the server is not ready.
        """

        try:
            # Create a socket object
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            self.__socket.connect((self.__address, self.__port))

            # Receive the server's response
            server_response = self.recieve_string()

            # Check if the server is ready
            if server_response[:3] != "+OK":
                
                print('.........')
                
                self.__socket.close()
                raise Exception(server_response)
        except ConnectionRefusedError:
            print(self.__error_dict[ConnectionRefusedError])
            sys.exit(1)

        except socket.gaierror:
            print(self.__error_dict[socket.gaierror])
            sys.exit(1)

    def close(self):
        # Close the connection
        self.__socket.close()

        # Close the socket
        self.__socket = None