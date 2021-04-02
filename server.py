from server_connection import ServerConnection
from typing import List, Set, Any
import socket
import threading


class Server:
    HOST = '10.100.130.47'
    PORT = 8756

    def __init__(self):
        self.client_list: List[ServerConnection] = []
        self.username_set: Set[str] = set()

    def start(self) -> None:
        """
        Start server and get ready for accepting new requests
        """
        print("Server is commencing...")
        try:
            self.listen()
        except KeyboardInterrupt:
            print("Shutting down the server... Bye!")
        finally:
            for connection in self.client_list:
                connection.conn.close()

    def listen(self) -> None:
        """
        Listen for incoming connections
        """
        # Create server socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.HOST, self.PORT))
        sock.listen(1)
        print("Listening at {}:{}".format(self.HOST, self.PORT))
        while True:
            # Accept new connections
            conn, address = sock.accept()
            print("Established a new connection from: {}".format(conn.getpeername()))
            # Create thread for connection
            server_connection = ServerConnection(self, conn, address)
            server_connection.start()

    def broadcast(self, message: str, username: str) -> None:
        """
        Broadcast message to other connected clients with respect to connected username
        """
        for server_connection in self.client_list:
            if server_connection.username != username:
                server_connection.send(message)

    def add_client(self, server_connection: ServerConnection) -> None:
        """
        Add connected client to list
        """
        self.client_list.append(server_connection)

    def remove_client(self, server_connection: ServerConnection) -> None:
        """
        Remove connected client from list
        """
        self.client_list.remove(server_connection)

    def check_username(self, username: str) -> bool:
        """
        Check if username exists in server; return True if it is, False otherwise
        """
        return username in self.username_set


class ServerConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, server_host: Server, conn: Any, address: Any):
        super().__init__()
        self.server_host = server_host
        self.conn = conn
        self.address = address
        self.username = None

    def run(self) -> None:
        self.username = self.get_username()
        self.server_host.add_client(self)
        # TODO: greeting message
        # Start listening to messages
        while True:
            message = self.conn.recv(self.BUFFER_SIZE).decode('ascii')
            if message:
                print("{} says {!r}".format(self.address, message))
                self.server_host.broadcast(message, self.username)
            else:
                # Socket is closed
                print('{} has closed the connection'.format(self.address))
                self.conn.close()
                self.server_host.remove_client(self)
                return None

    def get_username(self) -> str:
        """
        Get username from client and return it
        """
        sent_message = "Please enter a username."
        while True:
            self.send(sent_message)
            received_message = self.conn.recv(self.BUFFER_SIZE).decode('ascii')
            if received_message is not None and len(received_message) > 0:
                if self.server_host.check_username(received_message) is True:
                    sent_message = "That username is taken. Please enter another username."
                else:
                    return received_message
            else:
                sent_message = "Please enter a valid username."

    def send(self, message: str) -> None:
        """
        Send message through socket
        """
        self.conn.sendall(message.encode('ascii'))


if __name__ == '__main__':
    server = Server()
    server.start()
