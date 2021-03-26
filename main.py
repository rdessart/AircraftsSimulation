import time
from networking.tcp_server import TCPServer
# from networking.udp_server import UDPServer
from simulation.aircrafts import Aircrafts


def main():
    """ """
    aircrafts = Aircrafts()
    server_tcp = TCPServer(50_555, aircrafts)
    server_tcp.bind()
    server_tcp.start()
    while(1):
        server_tcp.list_ac.run_once()
        acf_data = str(server_tcp.list_ac)
        server_tcp.send_data(acf_data.encode())
        time.sleep(1.0/60.0)

if __name__ == "__main__":
    main()
