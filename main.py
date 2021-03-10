from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance


def main():
    a319 = performance.Performance("A319")
    a319_wrp = WRAP(ac="A319")
    # print(a319_wrp.takeoff_speed())
    cas_start = a319_wrp.takeoff_speed()["maximum"]
    a319.cas = a319_wrp.takeoff_speed()["maximum"]
    a319.mass = 60_000.00
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 15.0
    a319.gear = False
    a319.flaps = 1
    a319.pitch_target = 15.0
    # simulation varibale
    a319.phase = "TO_CLIMB"
    print("Starting")
    alts = []
    vs = []
    times = []
    i = 0
    while a319.altitude < 4_000.0 * aero.ft:
        a319.run()
        # When passing 100ft RA, the gear is up
        if (a319.altitude / aero.ft) > 100.0:
            a319.gear = False

        if (a319.altitude / aero.ft) > 1500.0 and\
           (a319.altitude / aero.ft) < 1550.0 and a319.phase != "THR_RED":
            a319.thrust_percent = 0.8  # Thrust reduction altitud
            a319.phase = "THR_RED"

        if (a319.altitude / aero.ft) > 3000.0:
            alts.append(int(round(a319.altitude / aero.kts)))
            vs.append(int(a319.vs))
            if a319.phase != "ACC":
                i = 0
                a319.pitch_target = 10.0
                a319.phase = "ACC"
            if a319.flaps > 0 and (a319.cas / aero.kts) > 210.0:
                a319.flaps = 0
            if a319.vs > 1000.0 and round(a319.pitch) == a319.pitch_target:
                a319.pitch_target -= 1
            elif a319.vs < 1000.0 and round(a319.pitch) == a319.pitch_target:
                a319.pitch_target += 1
            i += 1
            times.append(i / 60.0)

        # if a319.flaps == 0 and round(a319.cas / aero.kts) == 250:
        #     a319.phase = "CLIMB_1"
        #     if a319.pitch == a319.pitch_target:
        #         if a319.acc_x > 0:
        #             a319.pitch_target += 1
        #         elif a319.acc_x < 0:
        #             a319.pitch_target -=1

    print(f"Cas Start  = {cas_start / aero.kts}")
    print(f"Cas End  = {a319.cas / aero.kts}")
    print("Finished")
    fig, ax = plt.subplots()
    ax.plot(times, vs)
    ax.plot(times, alts)
    plt.axhline(1000.0)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
