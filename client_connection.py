import threading


class ClientConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self) -> None:
        """
        Start listening thread
        """
        while True:
            message = self.sock.recv(self.BUFFER_SIZE).decode('ascii')
            print("{!r}".format(message))

