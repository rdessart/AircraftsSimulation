import socket
from openap.extra import aero
# icao_type, callsign, latitude, longitude, mass, altitude, cas,
# takeoff, target_alt, gnd_lvl


def main():
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    so.connect(("127.0.0.1", 50_555))
    data = f"CRE A319 OOAAA 50.0 5.0 60000 {1000 * aero.ft} {200 * aero.kts} "
    data += f"0 {6_000 * aero.ft} 0.0|"
    so.send(data.encode())
    data = so.recv(1024).decode()
    print(data)
    while 1:
        data = so.recv(1024)
        if len(data) > 0:
            print(data.decode())
        
    print(data)


if __name__ == "__main__":
    main()
