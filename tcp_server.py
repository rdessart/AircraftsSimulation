import socket
import select


class TCPServer():
    def __init__(self, port):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.clients = {}

    def bind(self) -> bool:
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        print(f"Server running on {self.port}")
        self.inputs.append(self.sock)
        return True

    def parse_data(self, data: str) -> list:
        data = data.strip('|')
        cmds = data.split(' ')
        if cmds[0] == "CRE":
            # Create AI AIRCRAFT
            try:
                icao_type, latitude, longitude, *other = cmds[1:]
            except ValueError:
                print("Not enought parameters")
                return [False, "Not enought parameters"]
            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except ValueError:
                print("Latitude and/or longitude are not float")
                return [False, "Latitude and/or longitude are not float"]
            print(f"Creating an {icao_type} at {latitude:02f}°N ",
                  f"- {longitude:02f}°S")
            return [True, "Ok"]

    def run(self):
        execute = True
        while execute:
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
                        continue
                    else:
                        res, error = self.parse_data(data)
                        s.send(error.encode())


if __name__ == "__main__":
    server = TCPServer(50_555)
    server.bind()
    server.run()
