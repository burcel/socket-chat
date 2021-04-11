from client_connection import ClientConnection
from message import Message
from secret import Secret
import socket
import traceback


class Client:
    SERVER_HOST = "192.168.1.21"
    SERVER_PORT = 8756

    def __init__(self):
        self.sock = None
        self.username = None
        self.secret = Secret()

    def start(self) -> None:
        """
        Start client and open socket to server
        """
        try:
            self.connect()
        except KeyboardInterrupt:
            print("Shutting down the client... Bye!")
        except Exception:
            print(traceback.format_exc())
        finally:
            if self.sock is not None:
                self.sock.close()

    def send(self, message: bytes) -> None:
        """
        Send message through socket
        """
        if self.secret.ready is True:
            self.secret.encrypt_aes(message)
        self.sock.sendall(message)

    def receive(self) -> bytes:
        """
        Receive message from socket
        """
        message = self.sock.recv(ClientConnection.BUFFER_SIZE)
        if self.secret.ready is True:
            message = self.secret.decrypt_aes(message)
        return message

    def connect(self) -> None:
        """
        Create socket connection and start conversation
        """
        print("Trying to connect server...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.SERVER_HOST, self.SERVER_PORT))
        print("Connected to server.")
        self.authenticate()
        encrypted = self.validate_encryption()
        if encrypted is False:
            self.sock.close()
            return None

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
            message = self.receive().decode("UTF-8")
            print(message)
            if message == Message.OK:
                break
            while True:
                self.username = input("Username: ")
                if len(self.username) > 0:
                    self.send(self.username.encode("UTF-8"))
                    break
                else:
                    print("Empty username!")

    def converse(self):
        """
        Start conversation
        """
        while True:
            message = input("")
            self.send(message.encode("UTF-8"))

    def authenticate(self):
        """
        Start crypto process -> Receive public key and send AES key for encryption
        """
        # Receive public key from server
        message = self.receive()
        # Initialize RSA with public key of server
        self.secret.init_rsa(public_key=message)
        # Initialize AES
        self.secret.init_aes()
        # Encrypt AES key & nonce
        payload = self.secret.encrypt_rsa(self.secret.export_aes_key())
        # Send encrypted AES key & nonce pair to server
        self.send(payload)
        self.secret.ready = True

    def validate_encryption(self) -> bool:
        """
        Validate whether the encryption with client works or not
        """
        # Receive the first encrypted message from server
        message = self.receive()
        if message != Message.HI:
            print("Encryption error! Closing this socket...")
            return False
        # Send the first encrypted message
        self.send(Message.HI)
        # Receive the encrypted OK message
        message = self.receive()
        if message == Message.OK:
            print("Encryption is established.")
            return True
        else:
            print("Encryption error! Closing this socket...")
            return False


if __name__ == "__main__":
    client = Client()
    client.start()
