import socket
import select
import queue


class Server():
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.clients = {}

    def bind(self) -> bool:
        try:
            self.sock.bind(("0.0.0.0", self.port))
        except:
            print("Unable to bind")
            return False
        try:
            self.sock.listen(5)
        except:
            print("Unable to listen")
            return False
        print(f"Server running on {self.port}")
        self.inputs.append(self.sock)
        return True

    def run(self):
        execute = True
        while execute:
            # connection, client_address = self.sock.accept()
            # self.clients[connection] = client_address
            readable, writable, exceptional = select.select(self.inputs,
                                                            self.outputs,
                                                            self.inputs)
            for s in readable:
                if s is self.sock:
                    connection, client_address = s.accept()
                    print(f"New connection {client_address}")
                    self.clients[connection] = client_address
                    connection.setblocking(0)
                    self.inputs.append(connection)

                else:
                    try:
                        data = s.recv(1024).decode()
                    except ConnectionResetError:
                        print(f"{self.clients[s]} has disconnected !")
                        self.inputs.remove(s)
                        self.clients.__delitem__(s)
                    if len(data) <= 0:
                        print(f"{self.clients[s]} has disconnected !")
                        self.inputs.remove(s)
                        self.clients.__delitem__(s)
                    print(f">>>{data}")
                    if data == "QUIT":
                        execute = False


if __name__ == "__main__":
    server = Server(50_555)
    server.bind()
    server.run()
