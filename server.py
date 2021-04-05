from server_connection import ServerConnection
from typing import List, Set, Any
import socket


class Server:
    HOST = "192.168.1.21"
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

    def broadcast(self, username: str, message: str) -> None:
        """
        Broadcast message to other connected clients with respect to connected username
        """
        for server_connection in self.client_list:
            if server_connection.username != username:
                server_connection.send("{}: {}".format(username, message))

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


if __name__ == '__main__':
    server = Server()
    server.start()
