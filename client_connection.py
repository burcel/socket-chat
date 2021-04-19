import threading


class ClientConnection(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(self, client):
        super().__init__()
        self.client = client

    def run(self) -> None:
        """
        Start listening thread
        """
        while True:
            message = self.client.receive().decode("UTF-8")
            print("{}".format(message))

