from message import Message
from secret import Secret
from typing import TYPE_CHECKING, Any
import threading
import traceback
import json


class ServerConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, server, conn, address):
        super().__init__()
        self.server = server
        self.conn = conn
        self.address = address
        self.username = None
        self.secret = Secret()

    def run(self) -> None:
        """
        Start server listener thread for particular client
        """
        self.authenticate()
        encrypted = self.validate_encryption()
        if encrypted is False:
            self.conn.close()
            return None

        self.get_username()
        self.server.add_client(self)
        try:
            self.listen()
        except Exception:
            print(traceback.format_exc())

    def listen(self) -> None:
        """
        Listen for incoming messages
        """
        while True:
            message = self.receive().decode("UTF-8")
            if len(message) > 0:
                print("{}: {}".format(self.username, message))
                self.server.broadcast(self.username, message)
            else:
                # Socket is closed
                print("{} has closed the connection".format(self.address))
                self.conn.close()
                self.server.remove_client(self)
                return None

    def get_username(self) -> None:
        """
        Get username from client
        """
        message = Message.ENTER_USERNAME
        while True:
            self.send(message)
            received_message = self.receive().decode("UTF-8")
            if len(received_message) > 0:
                if self.server.check_username(received_message) is True:
                    message = Message.TAKEN_USERNAME
                else:
                    self.server.add_username(received_message)
                    self.username = received_message
                    self.send(Message.OK)
            else:
                message = Message.ENTER_VALID_USERNAME

    def send(self, message: bytes) -> None:
        """
        Send message through socket
        """
        if self.secret.ready is True:
            message = self.secret.encrypt_aes(message)
        self.conn.sendall(message)

    def receive(self) -> bytes:
        """
        Receive message from socket
        """
        message = self.conn.recv(self.BUFFER_SIZE)
        if self.secret.ready is True:
            message = self.secret.decrypt_aes(message)
        return message

    def authenticate(self):
        """
        Start crypto process -> Send public key and receive AES key for encryption
        """
        self.secret.init_rsa()
        self.send(self.secret.export_public_key())
        # Wait for encrypted AES key & nonce
        message = self.receive()
        # Decrypt AES key & nonce
        payload = self.secret.decrypt_rsa(message)
        # Parse AES key & nonce
        self.secret.parse_aes_key(payload)
        self.secret.ready = True

    def validate_encryption(self) -> bool:
        """
        Validate whether the encryption with client works or not
        """
        # Send the first encrypted message to client
        self.send(Message.HI)
        # Receive the encrypted message
        message = self.receive()
        if message == Message.HI:
            print("Encryption is established.")
            # Send the encrypted OK message
            self.send(Message.OK)
            return True
        else:
            print("Encryption error! Closing this socket...")
            return False

