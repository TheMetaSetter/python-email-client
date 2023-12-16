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
            ConnectionAbortedError: "client_socket.py: An established connection was aborted by the software in your host machine",
            OSError: "[WinError 10056] A connect request was made on an already connected socket",
            ConnectionResetError: "client_socket.py: An existing connection was forcibly closed by the remote host.",
            TimeoutError: "client_socket.py: The connection attempt timed out."
        }

        self.__BYTES_PER_RECIEVE = 1000 * 1000 * 1000

    # These are public methods.
    def recieve_bytes(self) -> bytes:
        """Recieve a message in bytes from the server.

        Returns:
            bytes: The message recieved from the server.
        """
        
        try:
            recieved_bytes = self.__socket.recv(self.__BYTES_PER_RECIEVE)
        except ConnectionResetError:
            print(self.__error_dict[ConnectionResetError])
            exit(1)
        except TimeoutError:
            return b''
        
        return recieved_bytes

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
        except Exception:
            print(Exception)
            sys.exit(1)

    def connect(self):
        """Connect to the server.

        Raises:
            Exception: If the server is not ready.
        """

        try:
            # Create a socket object
            if self.__socket is None:
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            self.__socket.settimeout(2)
            self.__socket.connect((self.__address, self.__port))

            # Receive the server's response
            server_response = self.recieve_bytes()

            # Check if the server is ready
            if b"+OK" not in server_response:
                self.__socket.close()
                raise Exception(server_response)
            
        except ConnectionRefusedError:
            print(self.__error_dict[ConnectionRefusedError])
            sys.exit(1)
            
        except socket.gaierror:
            print(self.__error_dict[socket.gaierror])
            sys.exit(1)

        except OSError:
            print(self.__error_dict[OSError])
            sys.exit(1)

    def close(self):
        if self.__socket is None:
            return
        
        # Close the connection
        self.__socket.close()

        # Close the socket
        self.__socket = None