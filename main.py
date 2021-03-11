from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance
from pid_controller import PIDController


def main():
    # PID Setup
    Kp = 0.2
    Ki = 0.0
    Kd = 0.2
    pid = PIDController(Kp, Ki, Kd, 0.0, 1/60)
    a319 = performance.Performance("A319")
    a319_wrp = WRAP(ac="A319")
    # print(a319_wrp.takeoff_speed())
    a319.cas = a319_wrp.takeoff_speed()["maximum"]
    a319.mass = 60_000.00
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 15.0
    a319.gear = False
    a319.flaps = 1
    a319.pitch_target = 15.0
    # simulation varibale
    a319.phase = "TO_CLIMB"
    # print("Starting")
    pitchs = []
    alts = []
    vs = []
    cas = []
    times = []
    i = 0
    # # DEBUG AP Variables
    # target_vs = 1000.0
    # vs_min = target_vs * 0.95
    # vs_max = target_vs * 1.50
    # END
    while a319.altitude < 20_000.0 * aero.ft:
        a319.run()
        # When passing 100ft RA, the gear is up
        if a319.gear and (a319.altitude / aero.ft) > 100.0:
            a319.gear = False

        if a319.flaps > 0 and (a319.cas / aero.kts) > 210.0:
            a319.flaps = 0

        if (a319.altitude / aero.ft) > 1500.0 and\
           (a319.altitude / aero.ft) < 1550.0 and a319.phase != "THR_RED":
            a319.thrust_percent = 0.8  # Thrust reduction altitud
            a319.phase = "THR_RED"

        if (a319.altitude / aero.ft) > 3000.0 and a319.phase != "CLIMB_1":
            if a319.phase != "ACC":
                i = 0
                a319.pitch_target = 10.0
                a319.phase = "ACC"
                pid.target = 1000.0
                pid.max_val = 15
                pid.reveverse = False
            # cas.append(a319.cas / aero.kts)
            # pitchs.append(a319.pitch)
            # times.append(i / 60.0)
            # a319.pitch_target = pid.compute(a319.cas)
            alts.append(int(round(a319.altitude / aero.kts)))
            a319.pitch_target = pid.compute(a319.vs)
            vs.append(int(a319.vs))
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            i += 1

        if a319.flaps == 0 and round(a319.cas / aero.kts) > 250:
            a319.phase = "CLIMB_1"
            # print(a319.altitude / aero.ft, round(a319.cas / aero.kts))
            Kp = 0.3
            Ki = 0.005
            Kd = 0.1
            pid = PIDController(Kp, Ki, Kd, 0.0, 1/60)
            pid.max_val = 15
            pid.target = 250.0 * aero.kts
            pid.reveverse = True  # as we want a positive result
            # if error is negative
            alts.append(int(round(a319.altitude / aero.kts)))
            vs.append(int(a319.vs))
            a319.pitch_target = pid.compute(a319.cas)
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            i += 1

    # print(f"Cas Start  = {cas_start / aero.kts}")
    print(f"Cas End  = {a319.cas / aero.kts}")
    # print("Finished")
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.plot(times, pitchs)
    ax3.set(ylabel='Pitch')
    ax4.plot(times, cas)
    ax4.set(ylabel='CAS')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
