from message import Message
from typing import TYPE_CHECKING, Any
import threading


class ServerConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, server, conn, address):
        super().__init__()
        self.server = server
        self.conn = conn
        self.address = address
        self.username = None

    def run(self) -> None:
        self.username = self.get_username()
        self.server.add_client(self)

        # Start listening to messages
        while True:
            message = self.conn.recv(self.BUFFER_SIZE).decode('ascii')
            if message:
                print("{} says {!r}".format(self.address, message))
                self.server.broadcast(message, self.username)
            else:
                # Socket is closed
                print('{} has closed the connection'.format(self.address))
                self.conn.close()
                self.server.remove_client(self)
                return None

    def get_username(self) -> str:
        """
        Get username from client and return it
        """
        message = "Please enter a username."
        while True:
            self.send(message)
            received_message = self.conn.recv(self.BUFFER_SIZE).decode('ascii')
            if received_message is not None and len(received_message) > 0:
                if self.server.check_username(received_message) is True:
                    message = "That username is taken. Please enter another username."
                else:
                    self.send(Message.OK)
                    return received_message
            else:
                message = "Please enter a valid username."

    def send(self, message: str) -> None:
        """
        Send message through socket
        """
        self.conn.sendall(message.encode('ascii'))
