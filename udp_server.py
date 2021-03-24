import socket
from threading import Thread, Lock


class UDPServer(Thread):
    mutex = Lock()

    def __init__(self, port_in, port_out):
        Thread.__init__(self, name="UDP Server")
        self.sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                     socket.IPPROTO_UDP)
        self.sock_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                      socket.IPPROTO_UDP)
        self.sock_in.bind(("0.0.0.0", port_in))
        self.clients = []
        self.port_out = port_out
        self.running = True

    def stop(self):
        locked = UDPServer.mutex.acquire(True, 1.0)
        if locked:
            self.running = False
            UDPServer.mutex.release()

    def addClient(self, ip: str) -> None:
        locked = UDPServer.mutex.acquire(True, 1.0)
        if locked:
            self.clients.append(ip)
            print(f"! Client added, there are {len(self.clients)} connections")
            UDPServer.mutex.release()
        else:
            print("Couldn't aquire lock")

    def broadcastData(self, data: str) -> int:
        bytes_send = 0
        for client in self.clients:
            bytes_send += self.sendData(data, client)
        return bytes_send

    def sendData(self, data: str, ip: str) -> int:
        bytes_send = self.sock_out.sendto(data.encode(), (ip, self.port_out))
        return bytes_send

    def checkIncomingData(self):
        data, sender = self.sock_in.recvfrom(1024, 0)
        print(f"<<< {data}")
        ip, port = sender
        print(f"Ip : {ip}, port: {port}")
        if len(data) > 0 and ip not in self.clients:
            self.addClient(ip)

    def run(self):
        while self.running:
            self.checkIncomingData()


if __name__ == "__main__":
    server = UDPServer(50_555, 50_556)
    server.start()
    while True:
        message = input(">>> ")
        server.broadcastData(message)
