from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance
from pid_controller import PIDController2


def main():
    # PID Setup
    a319 = performance.Performance("A319", False)
    a319_wrp = WRAP(ac="A319")
    # print(a319_wrp.takeoff_speed())
    # a319.cas = a319_wrp.takeoff_speed()["maximum"]
    a319.mass = 55_000.00
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    # a319.pitch = 15.0
    # a319.pitch_target = 15.0
    a319.pitch = 0.0
    a319.gear = False
    a319.flaps = 1
    a319.pitch_target = 0.0
    # simulation varibale
    a319.phase = 0
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
    distance_0 = 0.0
    run = True
    while run:
        a319.run()
        if a319.cas > a319_wrp.takeoff_speed()["default"] and a319.phase == 0:
            a319.phase = 1
            a319.pitch_target = 15.0
        # When passing 100ft RA, the gear is up
        if a319.gear and (a319.altitude / aero.ft) > 100.0:
            a319.gear = False

        if a319.flaps > 0 and (a319.cas / aero.kts) > 210.0:
            a319.flaps = 0

        if (a319.altitude / aero.ft) > 1500.0 and\
           (a319.altitude / aero.ft) < 1550.0 and a319.phase < 2:
            a319.thrust_percent = 0.9  # Thrust reduction altitud
            a319.phase = 2

        if (a319.altitude / aero.ft) > 3000.0 and a319.phase < 4:
            if a319.phase != 3:
                Kp = 0.007
                Ki = 0.0003
                Kd = 0.09
                pid = PIDController2(Kp, Ki, Kd, -15.0, 15.0, 1.0, dt=1/60)
                a319.phase = 3
            outputs.append(pid.compute(1000.0, a319.vs))
            if len(outputs) > 15:
                a319.pitch_target = sum(outputs) / len(outputs)
                outputs.remove(outputs[0])

        if a319.flaps == 0 and round(a319.cas / aero.kts) > 250:
            if a319.phase != 4:
                a319.phase = 4
                Kp = 4.0
                Ki = 0.0
                Kd = 4.0
                pid = PIDController2(Kp, Ki, Kd, -15.0, 15.0, 1.0, dt=1/60)
            a319.pitch_target = -1 * pid.compute(250.0 * aero.kts, a319.cas)

        if a319.altitude + (a319.v_y * 30) >= 33_000 * aero.ft:
            if a319.phase != 5:
                a319.phase = 5
                Kp = 4.0
                Ki = 0.0
                Kd = 4.0
                pid = PIDController2(Kp, Ki, Kd, -15.0, 15.0, 1.0, dt=1/60)

            target_vs = ((33_000 * aero.ft) - a319.altitude) / 60.0
            a319.pitch_target = pid.compute(target_vs, a319.v_y)

            if a319.tas > aero.mach2tas(0.78, a319.altitude):
                a319.tas = aero.mach2tas(0.78, a319.altitude)

        if 32_800 <= a319.altitude / aero.ft <= 33_200:
            if a319.phase != 6:
                a319.phase = 6
                distance_0 = a319.distance_x
                Kp = 4.0
                Ki = 1.0
                Kd = 1.0
                pid = PIDController2(Kp, Ki, Kd, -15.0, 15.0, 1.0, dt=1/60)

            a319.pitch_target = pid.compute(a319.altitude, 33_000 * aero.ft)
            if distance_0 / aero.nm >= 100.0:
                run = False
            if a319.tas > aero.mach2tas(0.78, a319.altitude):
                a319.tas = aero.mach2tas(0.78, a319.altitude)
        # OUTPUTS:
        if a319.phase >= 0:
            print(f"{a319.phase} : {a319.altitude / aero.ft:02f}",
                  f"- {a319.vs:02f} - {a319.cas / aero.kts}")
            alts.append(int(round(a319.altitude / aero.kts)))
            vs.append(int(a319.vs))
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            fd_pitchs.append(a319.pitch_target)
            i += 1

    print(f"Cas End  = {a319.cas / aero.kts}")
    draw(times, vs, alts, cas, pitchs, fd_pitchs, kpe, kie, kde)


def draw(times, vs, alts, cas, pitchs, fd_pitchs, kpe, kde, kie):
    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.plot(times, cas)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
