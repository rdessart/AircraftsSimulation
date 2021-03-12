from math import inf
from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance
from pid_controller import PIDController2, butter_lowpass_filter


def main():
    # PID Setup
    a319 = performance.Performance("A319", False)
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
    fd_pitchs = []
    alts = []
    vs = []
    cas = []
    times = []
    kpe = []
    kie = []
    kde = []
    i = 0
    outputs = []
    outputs2 = []
    # # DEBUG AP Variables
    # target_vs = 1000.0
    # vs_min = target_vs * 0.95
    # vs_max = target_vs * 1.50
    # END
    while a319.altitude < 10_000.0 * aero.ft:
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
                # Kp = 0.0000100
                # Ki = 0.0000030
                # Kd = 0.0000500
                Kp = 0.05
                Ki = 0.03
                Kd = 0.1
                pid = PIDController2(Kp, Ki, Kd, -15.0, 15.0,1.0 ,dt=1/60)
                i = 0
                a319.phase = "ACC"
            # a319.pitch_target = pid.compute(1000.0,a319.vs)
            outputs2.append(pid.compute(1000.0,a319.vs))
            if len(outputs2) > 15:
                a319.pitch_target = sum(outputs2) / len(outputs2)
                outputs2.remove(outputs2[0])
            #debug
            if a319.tas > aero.cas2tas(250 * aero.kts, a319.altitude):
                a319.tas = aero.cas2tas(250 * aero.kts, a319.altitude)

        # if a319.flaps == 0 and round(a319.cas / aero.kts) > 250:
        #     if a319.phase != "CLIMB_1":
        #         a319.phase = "CLIMB_1"
        #         Kp = 1.5
        #         Ki = 0.1
        #         Kd = 0.0
        #         pid = PIDController(Kp, Ki, Kd, 250.0 * aero.kts, 1/60)
        #         pid.max_val = 15
        #         pid.reveverse = True
        #     output = pid.compute(a319.cas)

        if a319.phase == "ACC" or a319.phase == "CLIMB_1":
            alts.append(int(round(a319.altitude / aero.kts)))
            vs.append(int(a319.vs))
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            fd_pitchs.append(a319.pitch_target)
            kpe.append(pid.get_kpe())
            kie.append(pid.get_kie())
            kde.append(pid.get_kde())
            i += 1

    print(f"Cas End  = {a319.cas / aero.kts}")
    draw(times, vs, alts, cas, pitchs, fd_pitchs, kpe, kie, kde, outputs)


def draw(times, vs, alts, cas, pitchs, fd_pitchs, kpe, kde, kie, outputs):
    fig, (ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9) \
        = plt.subplots(8, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.plot(times, cas)
    ax3.set(ylabel='CAS')
    ax4.plot(times, pitchs)
    ax4.set(ylabel='Pitch')
    ax5.plot(times, fd_pitchs)
    ax5.set(ylabel='FD Y')
    ax6.plot(times, kpe)
    ax6.set(ylabel='KPE')
    ax7.plot(times, kie)
    ax7.set(ylabel='KIE')
    ax8.plot(times, kde)
    ax8.set(ylabel='KDE')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
