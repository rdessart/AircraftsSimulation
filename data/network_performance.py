import socket
import matplotlib.pyplot as plt

list_aoas = []
list_cl = []
list_cd = []
aoas = {}


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    soc.bind(('0.0.0.0', 50_555))
    while True:
        try:
            data = soc.recvfrom(1024, 0)
        except KeyboardInterrupt:
            return
        aoa, cl, cd = data[0].decode().strip('|').split(',')
        aoa = round(float(aoa), 2)
        cl = float(cl)
        cd = float(cd)
        aoas[aoa] = [cl, cd]
        print(f"{float(aoa)} - {float(cl)} - {float(cd)}")
        if aoa not in list_aoas:
            list_aoas.append(aoa)
            list_cd.append(cd)
            list_cl.append(cl)
        else:
            index = list_aoas.index(aoa)
            list_cd[index] = cd
            list_cl[index] = cl


if __name__ == "__main__":
    main()
    fout = open("a319_ld.csv", 'w+')
    fout.write("AOA,Cl,Cd\n")
    keys = [aoa for aoa in aoas.keys()]
    keys.sort()
    keys.reverse()

    for key in keys:
        fout.write(f"{key},{aoas[key][0]},{aoas[key][1]}\n")
        fout.flush()
    fig, ax = plt.subplots()
    plt.plot(list_aoas, list_cd)
    plt.plot(list_aoas, list_cl)
    ax.legend(["Cl", "Cd"])
    plt.show()
