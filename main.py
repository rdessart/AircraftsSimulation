from openap import WRAP, aero
import matplotlib.pyplot as plt
import performance
# from automation.pid_controller import PIDController2
from automation.autopilot import Autopilot


def main():
    # PID Setup
    a319 = performance.Performance("A319", False)
    a319_wrp = WRAP(ac="A319")
    autopilot = Autopilot()
    a319.mass = 55_000.00
    a319.tas = aero.cas2tas(a319.cas, a319.altitude)
    a319.pitch = 0.0
    a319.gear = False
    a319.flaps = 1
    a319.pitch_target = 0.0
    a319.pitch_rate_of_change = 3.0
    target_alt = 30_000
    # simulation varibale
    a319.phase = 0
    pitchs = []
    fd_pitchs = []
    alts = []
    vs = []
    cas = []
    times = []
    thrusts = []
    drags = []
    phases = []
    i = 0
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
                a319.phase = 3
                autopilot.VerticalSpeedHold(1000.0 * aero.fpm, target_alt)

        if a319.flaps == 0 and round(a319.cas / aero.kts) > 250:
            if a319.phase != 4:
                a319.phase = 4
            speed_target = 320 * aero.kts
            if a319.altitude / aero.ft < 10_000:
                speed_target = 250 * aero.kts
            elif a319.altitude >= aero.crossover_alt(320 * aero.kts, 0.78):
                speed_target = aero.mach2cas(0.78, a319.altitude)
            if autopilot.active_mode != Autopilot.speed_hold \
                    or autopilot.target != speed_target:
                autopilot.SpeedHold(speed_target, target_alt)

        if a319.altitude + (a319.v_y * 30) >= target_alt * aero.ft:
            if a319.phase != 5:
                a319.phase = 5

        if target_alt - 200 <= a319.altitude / aero.ft <= target_alt + 200:
            if a319.phase != 6:
                a319.phase = 6
                distance_0 = a319.distance_x
                autopilot.AltitudeHold(target_alt)
            if distance_0 / aero.nm >= 100.0:
                run = False
            if a319.tas > aero.mach2tas(0.78, a319.altitude):
                a319.tas = aero.mach2tas(0.78, a319.altitude)

        if a319.phase >= 0:
            if autopilot.active_mode is not None:
                a319.pitch_target = autopilot.run(a319.cas,
                                                  a319.v_y,
                                                  a319.altitude,
                                                  a319.pitch)
            print(f"{a319.phase} : {a319.altitude / aero.ft:02f}",
                  f"- {a319.vs:02f} - {a319.cas / aero.kts:02f} - ",
                  f"{aero.tas2mach(a319.tas, a319.altitude):0.3f}",
                  f"{a319.pitch:02f} / {a319.pitch_target:02f}")
            alts.append(int(round(a319.altitude / aero.kts)))
            vs.append(int(a319.vs))
            cas.append(a319.cas / aero.kts)
            pitchs.append(a319.pitch)
            times.append(i / 60.0)
            fd_pitchs.append(a319.pitch_target)
            thrusts.append(a319.thrust)
            drags.append(a319.drag)
            phases.append(a319.phase)
            i += 1

    print(f"Cas End  = {a319.cas / aero.kts}")
    draw(times, vs, alts, cas, pitchs, fd_pitchs, thrusts, drags, phases)


def draw(times, vs, alts, cas, pitchs, fd_pitchs, thurst, drag, phases):
    fig, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(6, sharex=True)
    ax1.plot(times, vs)
    ax1.set(ylabel='VS(fpm)')
    ax2.plot(times, alts)
    ax2.set(ylabel='ATL')
    ax3.set(ylabel='CAS')
    ax3.plot(times, cas)
    ax4.set(ylabel='X Forces')
    ax4.plot(times, thurst)
    ax4.plot(times, drag)
    ax5.set(ylabel='Pitch')
    ax5.plot(times, pitchs)
    ax5.plot(times, fd_pitchs)
    ax6.set(ylabel='Phase')
    ax6.plot(times, phases)
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
