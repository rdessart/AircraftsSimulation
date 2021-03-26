import socket
import select
from threading import Thread
from simulation.aircraft import Aircraft
from simulation.aircrafts import Aircrafts


class TCPServer(Thread):
    def __init__(self, port, list_ac: Aircrafts):
        Thread.__init__(self, name="TCP Server")
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.inputs = []
        self.outputs = []
        self.message_queues = {}
        self.clients = {}
        self.list_ac = Aircrafts()

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
                (icao_type, callsign, latitude, longitude, mass, altitude,
                    cas, takeoff, target_alt, gnd_lvl) = cmds[1:]
            except ValueError:
                print("Not enought parameters")
                return [False, "Not enought parameters"]
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                mass = float(mass)
                altitude = float(altitude)
                cas = float(cas)
                takeoff = bool(takeoff)
                target_alt = float(target_alt)
                gnd_lvl = float(gnd_lvl)
            except ValueError:
                print("input(s) are not in the correct format")
                return [False, "input(s) are not in the correct format"]
            print(f"Creating an {icao_type} at {latitude:02f}°N ",
                  f"- {longitude:02f}°E of {mass} kg")
            acf = Aircraft(icao_type, callsign)
            self.list_ac.append(acf)
            return [True, str(acf.id)]

    def send_data(self, data: bytes) -> int:
        for client in self.clients.keys():
            client.send(data)

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
