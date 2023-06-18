from src.config.Config import Config
import socket
import _pickle as pickle
import time


class Network:

    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.config = Config()
        self.host = "3.85.99.21"
        self.port = 420
        self.addr = (self.host, self.port)

    def connect(self, name):

        self.client.connect(self.addr)
        self.client.send(str.encode(name))
        val = self.client.recv(8)
        return int(val.decode())  # can be int because will be an int id

    def disconnect(self):

        self.client.close()

    def send(self, data, pick=False):

        try:
            if pick:
                self.client.send(pickle.dumps(data))
            else:
                self.client.send(str.encode(data))

            reply = self.client.recv(2048 * 8)

            try:
                reply = pickle.loads(reply)
            except Exception as e:
                print(e)

            return reply
        except socket.error as e:
            print(e)
