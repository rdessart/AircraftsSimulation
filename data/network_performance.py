import socket
import matplotlib.pyplot as plt

list_aoas = []
list_cl = []
list_cd = []
list_alt = []
mach_thrust = {}
aoas = {}


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    soc.bind(('0.0.0.0', 50_555))
    while True:
        try:
            data = soc.recvfrom(1024, 0)
        except KeyboardInterrupt:
            return
        perfo = data[0].decode().strip('|')
        aoa, cl, cd, mach, altitude, thrust = perfo.split(',')
        aoa = round(float(aoa), 2)
        cl = float(cl)
        cd = float(cd)
        mach = round(float(mach), 3)
        altitude = round(float(altitude))
        thrust = round(float(thrust))
        aoas[aoa] = [cl, cd]
        print(f"{aoa} - {cl} - {cd} - {mach} - {altitude} - {thrust}")
        if aoa not in list_aoas:
            list_aoas.append(aoa)
            list_cd.append(cd)
            list_cl.append(cl)
        else:
            index = list_aoas.index(aoa)
            list_cd[index] = cd
            list_cl[index] = cl

        mach_thrust[mach] = thrust


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
    fout.close()
    fout2 = open("a319_thrust_40k.csv", 'w+')
    fout2.write("Mach,Thrust\n")
    keys = [mach for mach in mach_thrust.keys()]
    keys.sort()
    machs = []
    thrusts = []
    for key in keys:
        fout2.write(f"{key},{mach_thrust[key]}\n")
        fout2.flush()
        machs.append(key)
        thrusts.append(mach_thrust[key])
    fout2.close()

    fig, ax = plt.subplots()
    plt.plot(list_aoas, list_cd)
    plt.plot(list_aoas, list_cl)
    ax.legend(["Cd", "Cl"])
    plt.show()
    fig2, ax2 = plt.subplots()
    plt.plot(machs, thrusts)
    ax2.legend(["Thrust"])
    plt.show()
