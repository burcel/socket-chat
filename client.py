from client_connection import ClientConnection
from message import Message
import socket


class Client:
    SERVER_HOST = "192.168.1.21"
    SERVER_PORT = 8756

    def __init__(self):
        self.sock = None
        self.username = None

    def start(self) -> None:
        """
        Start client and open socket to server
        """
        try:
            self.connect()
        except KeyboardInterrupt:
            print("Shutting down the client... Bye!")
        finally:
            if self.sock is not None:
                self.sock.close()

    def connect(self):
        """
        Create socket connection and start conversation
        """
        print("Trying to connect server...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("Connected to server.")
        self.register_username()
        # Create thread for connection
        server_connection = ClientConnection(self.sock)
        server_connection.start()
        # Start conversation
        self.converse()

    def register_username(self):
        """
        Register username to server
        """
        while True:
            received_message = self.sock.recv(ClientConnection.BUFFER_SIZE).decode('ascii')
            print(received_message)
            if received_message == Message.OK:
                break
            self.username = input("Username: ")
            self.sock.sendall(self.username.encode('ascii'))

    def converse(self):
        """
        Start conversation
        """
        while True:
            message = input("{}: ".format(self.username))
            self.sock.sendall(message.encode('ascii'))


if __name__ == "__main__":
    client = Client()
    client.start()
