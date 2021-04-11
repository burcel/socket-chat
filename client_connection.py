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
            # TODO: encryption
            message = self.sock.recv(self.BUFFER_SIZE).decode("UTF-8")
            print("{}".format(message))

